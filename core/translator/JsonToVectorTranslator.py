# -*- coding: utf-8 -*-
import json
from typing import List, Dict, Any, Optional, Tuple

from qgis.core import QgsVectorLayer, QgsPointXY
from qgis.PyQt.QtCore import QVariant

from ..config.LogUtils import LogUtils
from ..enum import MetadataFieldKey
from ...utils.mrk.MetadataFields import MetadataFields
from ...utils.vector.VectorLayerGeometry import VectorLayerGeometry


class JsonToVectorTranslator:
    """
    Traduz JSON canônico v2.0 para QgsVectorLayer.

    Para cada registro:
    - busca o Field em MetadataFields via field.key
    - usa field.attribute como nome do atributo no layer (máx 9 chars)
    - usa field.label para documentação interna

    Geometria:
    - source "mrk":        usa MetadataFieldKey.LAT / LON / ALT
    - source "mrk+photo":  usa MetadataFieldKey.GPS_LATITUDE / GPS_LONGITUDE / ABSOLUTE_ALTITUDE
    - source "photo_only": usa MetadataFieldKey.GPS_LATITUDE / GPS_LONGITUDE / ABSOLUTE_ALTITUDE
    - fallback:            qualquer campo de coordenada válido presente no registro
    """

    def __init__(self, tool_key: str = "json_translator"):
        self.tool_key = tool_key
        self.logger = LogUtils(
            tool=tool_key, class_name="JsonToVectorTranslator")

    def translate(
        self,
        json_path: str,
        layer_name: str,
        selected_keys: Optional[List[str]] = None,
        source: Optional[str] = None,
    ) -> QgsVectorLayer:
        """
        Lê o JSON v2.0, monta schema de campos, cria features com
        geometria Point e retorna o layer.
        Lança ValueError se schema_version != "2.0".
        """
        from ...utils.JsonUtil import JsonUtil

        # Carregar registros do JSON
        records = JsonUtil.load_records(json_path)

        if not records:
            raise ValueError(
                f"Nenhum registro encontrado no JSON: {json_path}")

        # Determinar source - usar parâmetro ou tentar ler do JSON
        if source is None:
            # Tentar ler source do JSON raiz
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                source = json_data.get("source", "unknown")
            except Exception as e:
                self.logger.warning(f"Erro ao ler source do JSON: {e}")
                source = "unknown"

        # Resolver geometria para todos os registros
        valid_records = []
        for record in records:
            geom = self._resolve_geometry(record, source)
            if geom:
                record["_geometry"] = geom
                valid_records.append(record)

        if not valid_records:
            raise ValueError(
                f"Nenhum registro com geometria válida encontrado: {valid_records}"
            )

        # Construir schema (usando todos os registros para inferir tipo corretamente)
        schema = self._build_schema(
            valid_records[0], selected_keys, all_records=valid_records
        )

        # Preparar registros para VectorLayerGeometry
        points = []
        for record in valid_records:
            point_dict = {}
            geom = record.pop("_geometry")

            # Adicionar campos selecionados
            for key, value in record.items():
                if selected_keys is None or key in selected_keys:
                    # Resolver nome do atributo
                    attr_name = self._resolve_attribute_name(key)
                    point_dict[attr_name] = value

            # Adicionar coordenadas separadamente para geometria
            point_dict["_lon"] = geom.x()
            point_dict["_lat"] = geom.y()
            points.append(point_dict)

        # Criar layer
        layer = VectorLayerGeometry.create_point_layer_from_dicts(
            points=points,
            name=layer_name,
            field_specs=schema,
            geometry_keys=("_lon", "_lat"),
            tool_key=self.tool_key,
        )

        self.logger.info(
            f"Layer criado: {layer_name}",
            data={
                "total_records": len(records),
                "valid_records": len(valid_records),
                "schema_fields": len(schema),
                "source": source,
            },
        )

        return layer

    def _build_schema(
        self,
        sample_record: Dict,
        selected_keys: Optional[List[str]],
        all_records: Optional[List[Dict]] = None,
    ) -> List[Tuple[str, QVariant, str]]:
        """
        Para cada chave do registro, determina o tipo QVariant correto.
        1. Tenta inferir do sample_record
        2. Se for string, varre todos os records tentando converter para numérico
        3. Usa field.attribute como nome do QgsField (MetadataFields)
        4. Chaves sem Field catalogado usam a própria chave truncada
        """
        schema = []

        for key in sample_record.keys():
            if key.startswith("_") or key in ["source"]:
                continue

            if selected_keys is not None and key not in selected_keys:
                continue

            attr_name = self._resolve_attribute_name(key)

            # Determinar tipo QVariant - tenta converter string para númerico
            qtype = self._infer_field_type(key, sample_record, all_records)

            schema.append((attr_name, qtype, attr_name))

        return schema

    @staticmethod
    def _try_parse_number(value: Any) -> Optional[type]:
        """
        Tenta converter valor para int ou float.
        Retorna QVariant.Double, QVariant.Int ou None se não for numérico.
        """
        if value is None:
            return None
        if isinstance(value, bool):
            return QVariant.Bool
        if isinstance(value, int):
            return QVariant.Int
        if isinstance(value, float):
            return QVariant.Double
        if not isinstance(value, str):
            return None

        raw = value.strip().replace("+", "")
        if not raw or raw.lower() in ("none", "null", "nan", "inf", "true", "false"):
            return None

        # Tenta int primeiro (valores sem ponto decimal, ex: "50", "-1", "0")
        if "." not in raw:
            try:
                val = int(raw)
                # Limite QVariant.Int (32 bits signed): -2147483648 a 2147483647
                if -2147483648 <= val <= 2147483647:
                    return QVariant.Int
                # Valor grande demais para Int32 → usa String para evitar overflow
                return QVariant.String
            except (ValueError, TypeError):
                pass

        # Tenta float (valores com ou sem ponto, ex: "72.0", "-89.90", "0.02591")
        try:
            float(raw)
            return QVariant.Double
        except (ValueError, TypeError):
            return None

    def _infer_field_type(
        self,
        key: str,
        sample_record: Dict,
        all_records: Optional[List[Dict]] = None,
    ) -> QVariant:
        """
        Infere o tipo QVariant de um campo varrendo múltiplos registros.
        """
        value = sample_record.get(key)

        # 1. Se o sample já é numérico, usa direto
        native_type = self._try_parse_number(value)
        if native_type is not None:
            return native_type

        # 2. Se é string no sample, varre todos os records em busca de valor numérico
        has_real_float = False
        has_real_int = False
        has_non_numeric = False

        if all_records and isinstance(value, str):
            for record in all_records:
                v = record.get(key)
                if v is None:
                    continue
                t = self._try_parse_number(v)
                if t == QVariant.Double:
                    has_real_float = True
                elif t == QVariant.Int:
                    has_real_int = True
                else:
                    # É string de verdade (não numérica)
                    if isinstance(v, str) and v.strip():
                        has_non_numeric = True
                        break

            # Se pelo menos um registro tem float, o campo é Double
            if has_real_float:
                return QVariant.Double
            # Se só tem ints, é Int
            if has_real_int and not has_non_numeric:
                return QVariant.Int
            # Se encontrou string não numérica, fica String
            if has_non_numeric:
                return QVariant.String

        # 3. Fallback: infere do sample
        if isinstance(value, bool):
            return QVariant.Bool
        if isinstance(value, (int, float)):
            return QVariant.Double
        return QVariant.String

    def _resolve_geometry(self, record: Dict, source: str) -> Optional[QgsPointXY]:
        """
        Resolve coordenadas exclusivamente das FOTOS (EXIF/XMP).

        O MRK não fornece mais coordenadas geométricas — apenas atributos
        de contexto (MrkFile, MrkPath, FolderLevel*, etc.).

        Ordem de tentativas (apenas fotos):
        1. GpsLatitude/GpsLongitude (XMP do drone → sobrescreve EXIF quando disponível)
        2. DMS tuple em GpsLatitude/GpsLongitude (EXIF bruto, safety net)
        3. Nenhuma válida → retorna None (registro ignorado)
        """
        lat, lon = None, None

        # ── Tentativa 1: GpsLatitude/GpsLongitude (XMP + EXIF decimal) ──
        lat = self._try_get_float(record, MetadataFieldKey.GPS_LATITUDE.value)
        lon = self._try_get_float(record, MetadataFieldKey.GPS_LONGITUDE.value)

        # ── Tentativa 2: DMS tuple em GpsLatitude/GpsLongitude (safety net) ──
        if lat is None or lon is None:
            raw_lat = record.get(MetadataFieldKey.GPS_LATITUDE.value)
            raw_lon = record.get(MetadataFieldKey.GPS_LONGITUDE.value)

            dms_lat = self._dms_tuple_to_float(raw_lat)
            dms_lon = self._dms_tuple_to_float(raw_lon)

            if dms_lat is not None and dms_lon is not None:
                # Tenta ref de sinal (GPSLatitudeRef / GPSLongitudeRef) se existir
                ref_lat = record.get(
                    "GPSLatitudeRef") or record.get("GpsLatitudeRef")
                ref_lon = record.get("GPSLongitudeRef") or record.get(
                    "GpsLongitudeRef")
                if str(ref_lat or "").strip().upper() == "S":
                    dms_lat = -dms_lat
                if str(ref_lon or "").strip().upper() == "W":
                    dms_lon = -dms_lon
                lat = dms_lat
                lon = dms_lon

        if lat is not None and lon is not None:
            return QgsPointXY(float(lon), float(lat))

        return None

    @staticmethod
    def _try_get_float(record: Dict, key: str) -> Optional[float]:
        """Tenta extrair valor float de um campo do registro."""
        try:
            value = record.get(key)
            if value is None:
                return None
            if isinstance(value, bool):
                return None
            return float(value)
        except (ValueError, TypeError, OverflowError):
            return None

    @staticmethod
    def _dms_tuple_to_float(value, logger=None) -> Optional[float]:
        """
        Converte tupla DMS do EXIF (ex: ((13,1), (5,1), (1583,100))) para
        graus decimais.
        """
        if value is None:
            return None
        if not isinstance(value, (list, tuple)):
            return None
        parts = list(value)
        if len(parts) < 3:
            return None

        def _part(p):
            if isinstance(p, (int, float)):
                return float(p)
            if isinstance(p, (list, tuple)):
                p_list = list(p)
                if len(p_list) >= 2:
                    try:
                        return (
                            float(p_list[0]) / float(p_list[1])
                            if float(p_list[1]) != 0
                            else 0.0
                        )
                    except (ValueError, ZeroDivisionError):
                        return 0.0
            try:
                return float(p)
            except (ValueError, TypeError):
                return 0.0

        try:
            deg = _part(parts[0])
            minute = _part(parts[1])
            sec = _part(parts[2])
            return deg + (minute / 60.0) + (sec / 3600.0)
        except Exception as e:
            if logger:
                logger.warning(f"Erro ao converter DMS para float: {e}")
            return None

    def _resolve_attribute_name(self, key: str) -> str:
        """
        Resolve o nome do atributo usando MetadataFields.
        """
        # Procurar field por key.value
        for field_key, field in MetadataFields.INITIAL_FIELDS.items():
            if field_key.value == key and field.key:
                return field.attribute

        for field_key, field in MetadataFields.EXIF_FIELDS.items():
            if field_key.value == key and field.key:
                return field.attribute

        for field_key, field in MetadataFields.DJI_XMP_FIELDS.items():
            if field_key.value == key and field.key:
                return field.attribute

        for field_key, field in MetadataFields.CUSTOM_FIELDS.items():
            if field_key.value == key and field.key:
                return field.attribute

        for field_key, field in MetadataFields.MRK_FIELDS.items():
            if field_key.value == key and field.key:
                return field.attribute

        # Fallback: truncar chave a 9 caracteres
        return key[:9]
