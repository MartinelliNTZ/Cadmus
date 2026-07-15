# -*- coding: utf-8 -*-
from pathlib import Path
import json
import math
import re
from typing import Union, Tuple

from typing import Optional

from qgis.core import (
    QgsVectorFileWriter,
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsDistanceArea,
    QgsCoordinateReferenceSystem,
)
from qgis.PyQt.QtCore import QVariant


from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey
from ..mrk.MetadataFields import MetadataFields
import processing


class VectorLayerGeometry:
    """
    Responsável pelas transformações geométricas de camadas vetoriais.

    Escopo:
    - Aplicar operações geométricas (buffer, dissolve, merge, explode)
    - Transformar geometrias (simplificar, suavizar, validar)
    - Operações topológicas (union, intersection, difference)
    - Alterar estrutura geométrica das feições
    - Converter entre tipos de geometria

    Responsabilidade Principal:
    - Orquestrar transformações que ALTERAM as geometrias
    - Garantir validade após transformações
    - Manter coerência topológica

    NÃO é Responsabilidade:
    - Ler ou calcular métricas (use VectorLayerMetrics)
    - Reprojetar (use VectorLayerProjection)
    - Manipular atributos (use VectorLayerAttributes)
    - Carregar ou salvar (use VectorLayerSource)

    Logging Strategy (Métodos Estáticos):
    - Cada método estático instancia LogUtils com tool_key fornecido
    - Padrão: external_tool_key='untraceable' como valor padrão
    - Helper method: _get_logger(tool_key) centraliza criação de instâncias
    - Benefícios: Thread-safe, flexível (tool_key customizável), sem estado global
    """

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        """Helper para obter logger com tool_key específico.

        Parameters
        ----------
        tool_key : str
            Identificador da ferramenta (padrão: 'untraceable')

        Returns
        -------
        LogUtils
            Instância de logger configurada para a classe
        """
        return LogUtils(tool=tool_key, class_name="VectorLayerGeometry")

    @staticmethod
    def calculate_point_azimuth(point_a: QgsPointXY, point_b: QgsPointXY) -> float:
        """Calcula azimute 0-360 usando norte=0 e leste=90."""
        dx = point_b.x() - point_a.x()
        dy = point_b.y() - point_a.y()
        angle = math.degrees(math.atan2(dx, dy))
        return (angle + 360.0) % 360.0

    @staticmethod
    def angular_difference_degrees(angle_a: float, angle_b: float) -> float:
        """Menor diferença angular absoluta entre dois ângulos."""
        diff = (float(angle_a) - float(angle_b) + 180.0) % 360.0 - 180.0
        return abs(diff)

    @staticmethod
    def circular_mean_degrees(values) -> float:
        """Calcula média circular em graus."""
        clean = [float(v) for v in values if v is not None]
        if not clean:
            return 0.0

        sin_sum = sum(math.sin(math.radians(v)) for v in clean)
        cos_sum = sum(math.cos(math.radians(v)) for v in clean)

        if sin_sum == 0 and cos_sum == 0:
            return clean[-1]

        angle = math.degrees(math.atan2(sin_sum, cos_sum))
        return (angle + 360.0) % 360.0

    @staticmethod
    def measure_distance_between_points(
        point_a: QgsPointXY,
        point_b: QgsPointXY,
        crs: Optional[QgsCoordinateReferenceSystem] = None,
    ) -> float:
        """Mede distância entre pontos no CRS informado."""
        logger = VectorLayerGeometry._get_logger()
        if point_a is None or point_b is None:
            return 0.0

        if crs and crs.isValid():
            distance_area = QgsDistanceArea()
            distance_area.setSourceCrs(crs, QgsProject.instance().transformContext())
            ellipsoid = crs.ellipsoidAcronym() or "WGS84"
            distance_area.setEllipsoid(ellipsoid)
            try:
                return float(distance_area.measureLine(point_a, point_b))
            except Exception as e:
                logger.error(f"Erro ao medir distância entre pontos: {e}")
                return 0.0

        return math.hypot(point_b.x() - point_a.x(), point_b.y() - point_a.y())

    @staticmethod
    def get_representative_point(geometry: QgsGeometry) -> Optional[QgsPointXY]:
        """Extrai um ponto representativo de geometrias Point/MultiPoint."""
        if geometry is None or geometry.isEmpty():
            return None

        try:
            if geometry.isMultipart():
                points = geometry.asMultiPoint()
                return points[0] if points else None
            return geometry.asPoint()
        except Exception:
            return None

    @staticmethod
    def create_point_layer_from_dicts(
        points: list,
        name: str = "MRK_Points",
        field_specs: Optional[list] = None,
        geometry_keys: tuple = ("lon", "lat"),
        extra_fields: Optional[dict] = None,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Optional[QgsVectorLayer]:
        """
        Cria uma camada de pontos em memória a partir de registros genéricos.

        field_specs:
            - [("input_key", QVariant.Type), ...] ou
            - [("input_key", QVariant.Type, "output_field_name"), ...]

        geometry_keys:
            - tupla (x_key, y_key) usada para montar a geometria ponto.
        """
        logger = VectorLayerGeometry._get_logger(tool_key)
        logger.debug(
            f"create_point_layer_from_dicts(points={len(points) if points else 0}, name={name}, field_specs_count={len(field_specs) if field_specs else 0}, extra_fields={list(extra_fields.keys()) if extra_fields else None})"
        )
        if not points:
            return None

        if len(geometry_keys) != 2:
            raise ValueError("geometry_keys deve conter exatamente (x_key, y_key)")

        x_key, y_key = geometry_keys

        def infer_qvariant_type(values):
            for value in values:
                if value is None:
                    continue
                if isinstance(value, bool):
                    return QVariant.Bool
                if isinstance(value, int):
                    return QVariant.Int
                if isinstance(value, float):
                    return QVariant.Double
                return QVariant.String
            return QVariant.String

        # field_specs esperado:
        #   [("key", QVariant.Type), ("key", QVariant.Type, "output_name"), ...]
        # Se nao informado, infere a partir das chaves do primeiro registro.
        normalized_specs = []
        if field_specs:
            for spec in field_specs:
                if not isinstance(spec, (tuple, list)):
                    continue
                if len(spec) == 2:
                    input_name, qvariant_type = spec
                    output_name = input_name
                elif len(spec) >= 3:
                    input_name, qvariant_type, output_name = spec[:3]
                else:
                    continue
                normalized_specs.append((input_name, qvariant_type, output_name))
        else:
            first = points[0] if points else {}
            for key in first.keys():
                if key in (x_key, y_key):
                    continue
                qvariant_type = infer_qvariant_type(p.get(key) for p in points)
                normalized_specs.append((key, qvariant_type, key))

        fields = QgsFields()
        for _, qvariant_type, output_name in normalized_specs:
            fields.append(QgsField(output_name, qvariant_type))

        if extra_fields:
            for field_name, qtype in extra_fields.items():
                fields.append(QgsField(field_name, qtype))

        vl = QgsVectorLayer("Point?crs=EPSG:4326", name, "memory")
        vl.dataProvider().addAttributes(fields)
        vl.updateFields()

        def _coerce_attr_value(value, qvariant_type):
            if value is None:
                return None
            # Serializa containers para evitar erro de escrita em provider OGR.
            if isinstance(value, (list, tuple, dict)):
                try:
                    value = json.dumps(value, ensure_ascii=False)
                except Exception:
                    value = str(value)

            if qvariant_type == QVariant.String:
                try:
                    return str(value)
                except Exception:
                    return ""
            if qvariant_type in (QVariant.Double,):
                try:
                    if value == "":
                        return None
                    return float(value)
                except Exception:
                    return None
            if qvariant_type in (QVariant.Int, QVariant.LongLong):
                try:
                    if value == "":
                        return None
                    return int(float(value))
                except Exception:
                    return None
            if qvariant_type == QVariant.Bool:
                if isinstance(value, str):
                    lowered = value.strip().lower()
                    if lowered in ("1", "true", "sim", "yes"):
                        return True
                    if lowered in ("0", "false", "nao", "não", "no"):
                        return False
                try:
                    return bool(value)
                except Exception:
                    return None
            return value

        skipped_invalid_geometry = 0
        features = []
        for p in points:
            x_val = p.get(x_key)
            y_val = p.get(y_key)
            if x_val is None or y_val is None:
                skipped_invalid_geometry += 1
                continue
            try:
                x_num = float(x_val)
                y_num = float(y_val)
            except Exception:
                skipped_invalid_geometry += 1
                continue
            f = QgsFeature(vl.fields())
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x_num, y_num)))
            attrs = []
            for input_name, qvariant_type, _ in normalized_specs:
                value = p.get(input_name)
                value = _coerce_attr_value(value, qvariant_type)
                attrs.append(value)
            if extra_fields:
                for field_name in extra_fields.keys():
                    attrs.append(p.get(field_name))
            f.setAttributes(attrs)
            features.append(f)

        vl.dataProvider().addFeatures(features)
        vl.commitChanges()
        vl.updateExtents()
        if skipped_invalid_geometry:
            logger.warning(
                f"create_point_layer_from_dicts: pulados {skipped_invalid_geometry} registros sem coordenada valida"
            )
        if vl.featureCount() == 0:
            logger.warning(
                "create_point_layer_from_dicts: nenhuma feicao valida foi criada"
            )
            return None
        return vl

    def natural_sort_key(value: Union[str, int, float, None]) -> Tuple:
        """
        Gera uma chave de ordenação para valores mistos (string com números ou números puros).
        Exemplos:
            'A1'   -> ('A', 1)
            'A2'   -> ('A', 2)
            'A10'  -> ('A', 10)
            'B1'   -> ('B', 1)
            123    -> (123,)
            12.5   -> (12.5,)
            None   -> ('',)  # ou (float('-inf'),)
        """
        if value is None:
            return ("",)  # valores nulos vão para o início

        if isinstance(value, (int, float)):
            return (value,)

        # Converte para string e separa partes numéricas e não numéricas
        s = str(value)
        parts = re.split(r"(\d+)", s)  # ex: 'A10' -> ['A', '10', '']
        key_parts = []
        for part in parts:
            if part.isdigit():
                key_parts.append(int(part))
            else:
                key_parts.append(part)
        return tuple(key_parts)

    @staticmethod
    def create_line_layer_from_points(
        points: list,
        order_by_field: str,
        name: str = "Trilha",
        group_by_fields: Optional[list] = None,
        attribute_fields: Optional[list] = None,
        output_field_specs: Optional[list] = None,
        attributes_resolver=None,
        crs_authid: str = "EPSG:4326",
        min_vertices_per_line: int = 2,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Optional[QgsVectorLayer]:
        """
        Cria linha(s) em memória a partir de QgsFeature com geometria Point.

        As coordenadas são extraídas diretamente da geometria de cada feição.

        Parâmetros obrigatórios:
            points         — lista de QgsFeature com geometria Point
            order_by_field — campo usado para ordenar as feições dentro de cada grupo

        Parâmetros opcionais:
            group_by_fields    — campos para separar os pontos em linhas distintas
            attribute_fields   — campos copiados do primeiro ponto para a feição da linha
            output_field_specs — schema explícito: [(nome, tipo, len, prec), ...]
            attributes_resolver — callback(group, group_key) -> dict
        """
        logger = VectorLayerGeometry._get_logger(tool_key)

        if not points:
            logger.warning("create_line_layer_from_points: lista de pontos vazia")
            return None

        logger.debug(
            f"create_line_layer_from_points("
            f"points={len(points)}, order={order_by_field}, "
            f"group_by={group_by_fields})"
        )

        # --- Extração de coordenadas direto da geometria ---
        def _extract_xy(feature: QgsFeature) -> Optional[QgsPointXY]:
            geom = feature.geometry()
            if not geom or geom.isEmpty():
                return None
            pt = geom.asPoint()
            return QgsPointXY(pt.x(), pt.y())

        def _safe_attribute(feature: QgsFeature, field_name: str):
            try:
                return feature.attribute(field_name)
            except Exception:
                return None

        # --- Ordenação por sequência ---
        def _sort_key(feature: QgsFeature):
            val = _safe_attribute(feature, order_by_field)
            return VectorLayerGeometry.natural_sort_key(val)

        # --- Agrupamento ---
        if group_by_fields:
            groups: dict = {}
            for feat in points:
                key = tuple(
                    str(_safe_attribute(feat, f) or "").strip() for f in group_by_fields
                )
                groups.setdefault(key, []).append(feat)
        else:
            groups = {None: points}

        # --- Schema de campos ---
        fields = QgsFields()
        resolved_attr_pairs = []

        if output_field_specs:
            for spec in output_field_specs:
                if not spec:
                    continue
                fields.append(
                    QgsField(
                        spec[0],
                        spec[1] if len(spec) > 1 else QVariant.String,
                        len=spec[2] if len(spec) > 2 else 0,
                        prec=spec[3] if len(spec) > 3 else 0,
                    )
                )

        elif attribute_fields:
            seen = set()
            for input_name in attribute_fields:
                output_name = MetadataFields.resolve_output_name(input_name)
                if output_name in seen:
                    continue
                seen.add(output_name)
                resolved_attr_pairs.append((input_name, output_name))
                fields.append(QgsField(output_name, QVariant.String))

        # --- Camada de memória ---
        line_layer = QgsVectorLayer(f"LineString?crs={crs_authid}", name, "memory")
        line_layer.dataProvider().addAttributes(fields)
        line_layer.updateFields()

        # --- Feições ---
        for group_key, group in groups.items():
            try:
                group = sorted(group, key=_sort_key)
            except Exception as e:
                logger.error(f"Erro ao ordenar grupo {group_key}: {e}")
                continue

            vertices = []
            for feat in group:
                xy = _extract_xy(feat)
                if xy is not None:
                    vertices.append(xy)

            if len(vertices) < max(2, min_vertices_per_line):
                logger.debug(f"Grupo {group_key} ignorado: {len(vertices)} vértice(s)")
                continue

            feature = QgsFeature(line_layer.fields())
            feature.setGeometry(QgsGeometry.fromPolylineXY(vertices))

            if attributes_resolver:
                try:
                    custom_attrs = attributes_resolver(group, group_key=group_key) or {}
                except TypeError:
                    custom_attrs = attributes_resolver(group) or {}
                except Exception as e:
                    logger.warning(
                        f"attributes_resolver falhou para grupo {group_key}: {e}"
                    )
                    custom_attrs = {}
                for attr_name, attr_value in custom_attrs.items():
                    if line_layer.fields().lookupField(attr_name) != -1:
                        feature.setAttribute(attr_name, attr_value)

            elif resolved_attr_pairs:
                source = group[0]
                for input_name, output_name in resolved_attr_pairs:
                    value = _safe_attribute(source, input_name)
                    if value is None and output_name != input_name:
                        value = _safe_attribute(source, output_name)
                    if value is not None:
                        feature.setAttribute(output_name, value)

            line_layer.dataProvider().addFeature(feature)

        line_layer.updateExtents()

        if line_layer.featureCount() == 0:
            logger.warning("create_line_layer_from_points: nenhuma feição gerada")
            return None

        return line_layer

    @staticmethod
    def merge_memory_layers(
        layers: list,
        crs_authid: str,
        layer_name: str,
    ) -> Optional[QgsVectorLayer]:
        """Mescla camadas de memória em uma única camada."""
        if not layers:
            return None
        if len(layers) == 1:
            return layers[0]

        first = None
        for lyr in layers:
            if lyr and lyr.isValid():
                first = lyr
                break

        if first is None:
            uri = f"Point?crs={crs_authid}"
        else:
            geom_type = first.geometryType()  # 0=Point,1=Line,2=Polygon
            if geom_type == 1:
                uri = f"LineString?crs={crs_authid}"
            elif geom_type == 2:
                uri = f"Polygon?crs={crs_authid}"
            else:
                uri = f"Point?crs={crs_authid}"

        merged = QgsVectorLayer(uri, layer_name, "memory")
        merged_data = merged.dataProvider()

        all_field_names = []
        for lyr in layers:
            if not lyr or not lyr.isValid():
                continue
            for field in lyr.fields():
                if field.name() not in all_field_names:
                    all_field_names.append(field.name())

        unique_fields = []
        seen = set()
        for lyr in layers:
            if not lyr or not lyr.isValid():
                continue
            for fname in all_field_names:
                idx = lyr.fields().lookupField(fname)
                if idx >= 0 and fname not in seen:
                    seen.add(fname)
                    unique_fields.append(lyr.fields().field(idx))

        merged_data.addAttributes(unique_fields)
        merged.updateFields()

        for lyr in layers:
            if not lyr or not lyr.isValid():
                continue
            for feat in lyr.getFeatures():
                new_feat = QgsFeature(merged.fields())
                new_feat.setGeometry(feat.geometry())
                for field_name in all_field_names:
                    src_idx = lyr.fields().lookupField(field_name)
                    tgt_idx = merged.fields().lookupField(field_name)
                    if src_idx >= 0 and tgt_idx >= 0:
                        new_feat.setAttribute(tgt_idx, feat.attribute(src_idx))
                merged_data.addFeatures([new_feat])

        merged.updateExtents()
        merged.updateFields()
        return merged

    @staticmethod
    def create_buffer_geometry(
        *,
        layer: QgsVectorLayer,
        distance: float,
        output_path: Optional[str] = None,
        segments: int = 5,
        end_cap_style: int = 1,
        join_style: int = 1,
        miter_limit: float = 2.0,
        dissolve: bool = False,
        external_tool_key=ToolKey.UNTRACEABLE,
    ) -> Optional[QgsVectorLayer]:
        """Cria buffer ao redor das geometrias com distância e número de segmentos especificados."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"create_buffer_geometry: distance={distance}, segments={segments}, dissolve={dissolve}"
        )
        if VectorLayerGeometry.get_layer_type(
            layer, tool_key=external_tool_key
        ) not in (
            QgsWkbTypes.PointGeometry,
            QgsWkbTypes.LineGeometry,
            QgsWkbTypes.PolygonGeometry,
        ):
            return None

        params = {
            "INPUT": layer,
            "DISTANCE": distance,
            "SEGMENTS": segments,
            "END_CAP_STYLE": end_cap_style,
            "JOIN_STYLE": join_style,
            "MITER_LIMIT": miter_limit,
            "DISSOLVE": dissolve,
            "OUTPUT": output_path or "memory:",
        }

        result = processing.run(
            "native:buffer",
            params,
        )

        return result.get("OUTPUT")

    @staticmethod
    def create_buffer_to_path_safe(
        *,
        input_path: str,
        output_path: str,
        distance: float,
        segments: int = 5,
        end_cap_style: int = 1,
        join_style: int = 1,
        miter_limit: float = 2.0,
        dissolve: bool = False,
        external_tool_key=ToolKey.UNTRACEABLE,
        feedback=None,
    ) -> str:
        """
        Executa buffer usando arquivo físico (GPKG).
        Seguro para execução em QgsTask.
        """

        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.info(
            f"create_buffer_to_path_safe start: {input_path} -> {output_path}, distance={distance}"
        )

        if not input_path or not output_path:
            raise ValueError("input_path e output_path são obrigatórios")

        params = {
            "INPUT": input_path,
            "DISTANCE": distance,
            "SEGMENTS": segments,
            "END_CAP_STYLE": end_cap_style,
            "JOIN_STYLE": join_style,
            "MITER_LIMIT": miter_limit,
            "DISSOLVE": dissolve,
            "OUTPUT": output_path,
        }

        processing.run("native:buffer", params, feedback=feedback)

        logger.info("create_buffer_to_path_safe completed")

        return output_path

    def explode_multipart_features(
        *, layer: QgsVectorLayer, external_tool_key=ToolKey.UNTRACEABLE
    ) -> Optional[QgsVectorLayer]:
        """Explode feições multipart em feições simples."""

        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"explode_multipart_features(layer={layer})")
        if (
            VectorLayerGeometry.get_layer_type(layer, tool_key=external_tool_key)
            == QgsWkbTypes.LineGeometry
        ):
            result = processing.run(
                "native:explodelines",
                {"INPUT": layer, "OUTPUT": "memory:"},
            )

            return result.get("OUTPUT")
        return None  # poligons e point a implementar

    @staticmethod
    def explode_lines_to_path(
        *, input_path: str, output_path: str, external_tool_key=ToolKey.UNTRACEABLE
    ) -> str:
        """
        Explode linhas usando arquivos físicos.
        Seguro para grandes volumes.
        """
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.info(f"explode_lines_to_path: {input_path} -> {output_path}")
        if not input_path or not output_path:
            raise ValueError("input_path e output_path são obrigatórios")

        params = {"INPUT": input_path, "OUTPUT": output_path}

        processing.run("native:explodelines", params)

        logger.info("explode_lines_to_path completed")
        return output_path

    @staticmethod
    def explode_lines_to_path_safe(
        *,
        layer: QgsVectorLayer,
        output_path: str,
        external_tool_key=ToolKey.UNTRACEABLE,
    ) -> str:
        """
        Explode linhas (LineString / MultiLineString) manualmente.
        Thread-safe. Compatível com QgsTask.
        """
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.info(f"explode_lines_to_path_safe start -> output: {output_path}")
        if not layer or not layer.isValid():
            logger.critical("Camada inválida para explode_lines_to_path_safe")
            raise ValueError("Camada inválida")

        if layer.geometryType() != QgsWkbTypes.LineGeometry:
            logger.critical("Camada não é do tipo linha em explode_lines_to_path_safe")
            raise ValueError("Camada não é do tipo linha")

        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GPKG"
        options.fileEncoding = "UTF-8"
        options.layerName = Path(output_path).stem
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        transform_context = QgsProject.instance().transformContext()

        writer = QgsVectorFileWriter.create(
            output_path,
            layer.fields(),
            QgsWkbTypes.LineString,
            layer.crs(),
            transform_context,
            options,
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            logger.critical(f"Erro ao criar writer: {writer.errorMessage()}")
            raise RuntimeError(writer.errorMessage())

        logger.debug("Writer criado com sucesso para explode_lines_to_path_safe")

        feat_out = QgsFeature(layer.fields())

        processed = 0
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            if geom.isMultipart():
                parts = geom.asMultiPolyline()
            else:
                parts = [geom.asPolyline()]

            for part in parts:
                if len(part) < 2:
                    continue

                for i in range(len(part) - 1):
                    line = QgsGeometry.fromPolylineXY([part[i], part[i + 1]])
                    feat_out.setAttributes(feat.attributes())
                    feat_out.setGeometry(line)
                    writer.addFeature(feat_out)
                    processed += 1

        del writer
        logger.info(
            f"explode_lines_to_path_safe completed, processed features (approx): {processed}"
        )
        return output_path

    @staticmethod
    def get_layer_type(
        layer: QgsVectorLayer, tool_key: str = ToolKey.UNTRACEABLE
    ) -> Optional[str]:
        logger = VectorLayerGeometry._get_logger(tool_key)
        logger.debug(f"get_layer_type(layer={layer})")
        if not isinstance(layer, QgsVectorLayer):
            return None

        geom_type = layer.geometryType()

        if geom_type == QgsWkbTypes.PointGeometry:
            logger.info("get_layer_type: PointGeometry")
            return QgsWkbTypes.PointGeometry
        if geom_type == QgsWkbTypes.LineGeometry:
            logger.info("get_layer_type: LineGeometry")
            return QgsWkbTypes.LineGeometry
        if geom_type == QgsWkbTypes.PolygonGeometry:
            logger.info("get_layer_type: PolygonGeometry")
            return QgsWkbTypes.PolygonGeometry

        return None

    @staticmethod
    def get_selected_features(
        layer: QgsVectorLayer, tool_key: str = ToolKey.UNTRACEABLE
    ):
        logger = VectorLayerGeometry._get_logger(tool_key)
        logger.debug(f"get_selected_features(layer={layer})")
        if not isinstance(layer, QgsVectorLayer):
            return None, "Layer inválido"

        fids = layer.selectedFeatureIds()
        if not fids:
            logger.info("Nenhuma feição selecionada na camada")
            return None, "Nenhuma feição selecionada na camada."

        request = QgsFeatureRequest().setFilterFids(fids)

        mem_layer = layer.materialize(request)
        if not mem_layer or not mem_layer.isValid():
            logger.critical("Falha ao materializar feições selecionadas")
            return None, "Falha ao materializar feições selecionadas."

        logger.info(f"get_selected_features: {len(fids)} features")
        return mem_layer, None

    @staticmethod
    def singleparts_to_multparts(
        layer, feedback=None, only_selected=False, tool_key: str = ToolKey.UNTRACEABLE
    ):
        logger = VectorLayerGeometry._get_logger(tool_key)
        logger.debug(
            f"singleparts_to_multparts(layer={layer}, only_selected={only_selected}, feedback={feedback})"
        )
        if not isinstance(layer, QgsVectorLayer):
            return False

        if not QgsWkbTypes.isMultiType(layer.wkbType()):
            # camada não é multipart
            return True

        # 🔀 decide fonte das feições
        if only_selected and layer.selectedFeatureCount() > 0:
            feats = list(layer.selectedFeatures())
        else:
            feats = list(layer.getFeatures())

        total = len(feats)
        logger.info(f"singleparts_to_multparts: total features to process {total}")
        new_features = []
        ids_to_delete = []

        for i, feat in enumerate(feats):

            if feedback and feedback.isCanceled():
                logger.info("singleparts_to_multparts canceled by feedback")
                return False

            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            if not geom.isMultipart():
                continue

            parts = geom.constGet()

            for part in parts:
                new_feat = QgsFeature(layer.fields())
                new_feat.setAttributes(feat.attributes())
                new_feat.setGeometry(QgsGeometry(part.clone()))
                new_features.append(new_feat)

            ids_to_delete.append(feat.id())

            if feedback:
                feedback.setProgress(int((i + 1) / total * 100))

        # 🔥 Remove multipart
        if ids_to_delete:
            layer.deleteFeatures(ids_to_delete)

        # ➕ Adiciona singleparts
        if new_features:
            layer.addFeatures(new_features)
            logger.info(
                f"singleparts_to_multparts added {len(new_features)} features and removed {len(ids_to_delete)}"
            )
        return True

    def get_geometry_difference(
        self, geometry1, geometry2, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Calcula a diferença entre duas geometrias."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"get_geometry_difference(geometry1={geometry1}, geometry2={geometry2})"
        )
        pass

    def convert_geometry_type(
        self, layer, target_type, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Converte geometrias para um tipo diferente quando possível."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"convert_geometry_type(layer={layer}, target_type={target_type})")
        pass

    def simplify_geometry(
        self, layer, tolerance, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Simplifica geometrias reduzindo vértices mantendo forma geral."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"simplify_geometry(layer={layer}, tolerance={tolerance})")
        pass

    def smooth_geometry(
        self, layer, smoothing_iterations, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Suaviza geometrias através de algoritmo iterativo."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"smooth_geometry(layer={layer}, smoothing_iterations={smoothing_iterations})"
        )
        pass

    def validate_geometry(self, geometry, external_tool_key=ToolKey.UNTRACEABLE):
        """Verifica se uma geometria é válida e sem problemas topológicos."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"validate_geometry(geometry={geometry})")
        pass

    def fix_invalid_geometry(self, geometry, external_tool_key=ToolKey.UNTRACEABLE):
        """Tenta corrigir automaticamente uma geometria inválida."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"fix_invalid_geometry(geometry={geometry})")
        pass

    def get_geometry_intersection(
        self, geometry1, geometry2, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Calcula a interseção entre duas geometrias."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"get_geometry_intersection(geometry1={geometry1}, geometry2={geometry2})"
        )
        pass

    def get_geometry_union(
        self, geometry1, geometry2, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Calcula a união entre duas geometrias."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"get_geometry_union(geometry1={geometry1}, geometry2={geometry2})"
        )
        pass

    def dissolve_geometries_by_attribute(
        self, layer, dissolve_field, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Dissolve geometrias agrupadas por um atributo específico."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(
            f"dissolve_geometries_by_attribute(layer={layer}, dissolve_field={dissolve_field})"
        )
        pass

    def merge_geometries(self, geometries_list, external_tool_key=ToolKey.UNTRACEABLE):
        """Combina múltiplas geometrias em uma única geometria multipart."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"merge_geometries(geometries_list={geometries_list})")
        pass
