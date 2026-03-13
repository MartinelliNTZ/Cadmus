from pathlib import Path
import os
from typing import Optional

from qgis.core import (
    QgsVectorFileWriter,
    QgsProject,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsCoordinateTransformContext,
)
from qgis.PyQt.QtCore import QVariant

from ...utils.StringUtils import StringUtils
from ...core.config.LogUtils import LogUtils
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
    - Cada método estático instancia LogUtilsNew com tool_key fornecido
    - Padrão: external_tool_key='untraceable' como valor padrão
    - Helper method: _get_logger(tool_key) centraliza criação de instâncias
    - Benefícios: Thread-safe, flexível (tool_key customizável), sem estado global
    """
    
    @staticmethod
    def _get_logger(tool_key: str = "untraceable") -> LogUtils:
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
    def create_point_layer_from_dicts(
        points: list,
        name: str = "MRK_Pontos",
        extra_fields: Optional[dict] = None,
    ) -> Optional[QgsVectorLayer]:
        """Cria uma camada de pontos em memória a partir de uma lista de dicionários."""
        if not points:
            return None

        fields = QgsFields()
        fields.append(QgsField("foto", QVariant.Int))
        fields.append(QgsField("alt", QVariant.Double))
        fields.append(QgsField("data_name", QVariant.String))
        fields.append(QgsField("numdovoo", QVariant.String))
        fields.append(QgsField("nomedovoo", QVariant.String))
        fields.append(QgsField("pasta1", QVariant.String))
        fields.append(QgsField("pasta2", QVariant.String))
        # 🔴 NOVO: Campo para rastrear qual pasta (voo) cada ponto veio
        # Isso permite PhotoMetadata distinguir fotos de múltiplos voos com mesma numeração
        fields.append(QgsField("mrk_folder", QVariant.String))

        if extra_fields:
            for field_name, qtype in extra_fields.items():
                fields.append(QgsField(field_name, qtype))

        vl = QgsVectorLayer("Point?crs=EPSG:4326", name, "memory")
        vl.dataProvider().addAttributes(fields)
        vl.updateFields()

        vl.startEditing()
        for p in points:
            f = QgsFeature(vl.fields())
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(p.get("lon"), p.get("lat"))))
            attrs = [
                p.get("foto"),
                p.get("alt"),
                p.get("data_name"),
                p.get("numdovoo"),
                p.get("nomedovoo"),
                p.get("pasta1"),
                p.get("pasta2"),
                p.get("mrk_folder"),  # 🔴 NOVO: pasta de origem do ponto
            ]
            if extra_fields:
                for field_name in extra_fields.keys():
                    attrs.append(p.get(field_name))
            f.setAttributes(attrs)
            vl.addFeature(f)

        vl.commitChanges()
        vl.updateExtents()
        return vl

    @staticmethod
    def create_line_layer_from_points(
        points: list,
        name: str = "Trilha",
    ) -> Optional[QgsVectorLayer]:
        """Cria uma camada de linha em memória a partir de uma lista de pontos."""
        if not points or len(points) < 2:
            return None

        line = QgsVectorLayer("LineString?crs=EPSG:4326", name, "memory")
        geom = QgsGeometry.fromPolylineXY([
            QgsPointXY(p.get("lon"), p.get("lat")) for p in points
        ])
        f = QgsFeature()
        f.setGeometry(geom)
        line.dataProvider().addFeature(f)
        line.updateExtents()
        return line

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
        external_tool_key="untraceable"        
    ) -> Optional[QgsVectorLayer]:
        """Cria buffer ao redor das geometrias com distância e número de segmentos especificados."""
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.debug(f"create_buffer_geometry: distance={distance}, segments={segments}, dissolve={dissolve}")
        if VectorLayerGeometry.get_layer_type(layer) not in (
            QgsWkbTypes.PointGeometry,QgsWkbTypes.LineGeometry,QgsWkbTypes.PolygonGeometry
        ):
            return None

        params = {
            'INPUT': layer,
            'DISTANCE': distance,
            'SEGMENTS': segments,
            'END_CAP_STYLE': end_cap_style,
            'JOIN_STYLE': join_style,
            'MITER_LIMIT': miter_limit,
            'DISSOLVE': dissolve,
            'OUTPUT': output_path or 'memory:'
        }

        result = processing.run(
            'native:buffer',
            params,            
        )

        return result.get('OUTPUT')

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
        external_tool_key="untraceable",
        feedback = None
    ) -> str:
        """
        Executa buffer usando arquivo físico (GPKG).
        Seguro para execução em QgsTask.
        """

        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.info(f"create_buffer_to_path_safe start: {input_path} -> {output_path}, distance={distance}")

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
            "OUTPUT": output_path
        }

        processing.run("native:buffer", params,feedback = feedback)

        logger.info("create_buffer_to_path_safe completed")

        return output_path


    def explode_multipart_features(        *, 
                                   layer: QgsVectorLayer,
                                external_tool_key="untraceable"
    ) -> Optional[QgsVectorLayer]:
        """Explode feições multipart em feições simples."""

        if VectorLayerGeometry.get_layer_type(layer) == QgsWkbTypes.LineGeometry:
            result = processing.run(
                'native:explodelines',
                {
                    'INPUT': layer,
                    'OUTPUT': 'memory:'
                },
            
            )

            return result.get('OUTPUT')
        return None # poligons e point a implementar
    @staticmethod
    def explode_lines_to_path(
        *,
        input_path: str,
        output_path: str,
        external_tool_key="untraceable"
    ) -> str:
        """
        Explode linhas usando arquivos físicos.
        Seguro para grandes volumes.
        """
        logger = VectorLayerGeometry._get_logger(external_tool_key)
        logger.info(f"explode_lines_to_path: {input_path} -> {output_path}")
        if not input_path or not output_path:
            raise ValueError("input_path e output_path são obrigatórios")

        params = {
            "INPUT": input_path,
            "OUTPUT": output_path
        }

        processing.run("native:explodelines", params)

        logger.info("explode_lines_to_path completed")
        return output_path

    @staticmethod
    def explode_lines_to_path_safe(
        *,
        layer: QgsVectorLayer,
        output_path: str,
        external_tool_key="untraceable"
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
            options
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
        logger.info(f"explode_lines_to_path_safe completed, processed features (approx): {processed}")
        return output_path


    @staticmethod
    def get_layer_type(layer: QgsVectorLayer) -> Optional[str]:
        logger = VectorLayerGeometry._get_logger()
        logger.debug("get_layer_type called")
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
    def get_selected_features( layer: QgsVectorLayer):
            logger = VectorLayerGeometry._get_logger()
            logger.debug("get_selected_features called")
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
    def singleparts_to_multparts(layer, feedback=None, only_selected=False):
        logger = VectorLayerGeometry._get_logger()
        logger.debug("singleparts_to_multparts start")
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
            logger.info(f"singleparts_to_multparts added {len(new_features)} features and removed {len(ids_to_delete)}")
        return True


    def get_geometry_difference(self, geometry1, geometry2, external_tool_key="untraceable"):
        """Calcula a diferença entre duas geometrias."""
        pass

    def convert_geometry_type(self, layer, target_type, external_tool_key="untraceable"):
        """Converte geometrias para um tipo diferente quando possível."""
        pass
    
    
    def simplify_geometry(self, layer, tolerance, external_tool_key="untraceable"):
        """Simplifica geometrias reduzindo vértices mantendo forma geral."""
        pass

    def smooth_geometry(self, layer, smoothing_iterations, external_tool_key="untraceable"):
        """Suaviza geometrias através de algoritmo iterativo."""
        pass

    def validate_geometry(self, geometry, external_tool_key="untraceable"):
        """Verifica se uma geometria é válida e sem problemas topológicos."""
        pass

    def fix_invalid_geometry(self, geometry, external_tool_key="untraceable"):
        """Tenta corrigir automaticamente uma geometria inválida."""
        pass

    def get_geometry_intersection(self, geometry1, geometry2, external_tool_key="untraceable"):
        """Calcula a interseção entre duas geometrias."""
        pass

    def get_geometry_union(self, geometry1, geometry2, external_tool_key="untraceable"):
        """Calcula a união entre duas geometrias."""
        pass    
    
    def dissolve_geometries_by_attribute(self, layer, dissolve_field, external_tool_key="untraceable"):
        """Dissolve geometrias agrupadas por um atributo específico."""
        pass

    def merge_geometries(self, geometries_list, external_tool_key="untraceable"):
        """Combina múltiplas geometrias em uma única geometria multipart."""
        pass