# -*- coding: utf-8 -*-
"""Utilitarios para extracao e parsing de metadados XMP."""

import os
from datetime import datetime
from xml.etree import ElementTree as ET  # nosec B405  # defusedxml nao disponivel no QGIS 3.16; XMP lido de arquivos confiaveis

from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey
from ...core.enum import MetadataFieldKey
from .MetadataFields import MetadataFields


class XmpUtil:
    """Utilitario para extracao e normalizacao de dados XMP."""

    _NAMESPACE_PREFIXES = {
        "http://www.dji.com/drone-dji/1.0/": "drone-dji",
        "http://ns.adobe.com/xap/1.0/": "xmp",
        "http://purl.org/dc/elements/1.1/": "dc",
        "http://ns.adobe.com/camera-raw-settings/1.0/": "crs",
        "http://pix4d.com/camera/1.0": "Camera",
        "http://ns.adobe.com/exif/1.0/aux/": "aux",
        "http://ns.adobe.com/photoshop/1.0/": "photoshop",
        "http://ns.adobe.com/tiff/1.0/": "tiff",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    }

    _FIELD_PRIORITY = [
        "drone-dji:Version",
        "drone-dji:ImageSource",
        "drone-dji:GpsStatus",
        "drone-dji:AltitudeType",
        "drone-dji:AbsoluteAltitude",
        "drone-dji:RelativeAltitude",
        "drone-dji:GimbalRollDegree",
        "drone-dji:GimbalYawDegree",
        "drone-dji:GimbalPitchDegree",
        "drone-dji:FlightRollDegree",
        "drone-dji:FlightYawDegree",
        "drone-dji:FlightPitchDegree",
        "drone-dji:SurveyingMode",
        "drone-dji:DewarpFlag",
        "drone-dji:DewarpData",
        "drone-dji:CalibratedFocalLength",
        "drone-dji:CalibratedOpticalCenterX",
        "drone-dji:CalibratedOpticalCenterY",
        "drone-dji:UTCAtExposure",
        "drone-dji:ShutterType",
        "drone-dji:ShutterCount",
        "drone-dji:FocusDistance",
        "drone-dji:CameraSerialNumber",
        "drone-dji:DroneModel",
        "drone-dji:DroneSerialNumber",
        "drone-dji:CaptureUUID",
        "drone-dji:PictureQuality",
        "xmp:ModifyDate",
        "xmp:CreateDate",
        "xmp:CreatorTool",
        "dc:format",
    ]

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="XmpUtil")

    @staticmethod
    def _extract_xmp_text_raw(image_path: str) -> str:
        with open(image_path, "rb") as fh:
            raw = fh.read().decode("latin1", errors="ignore")

        start = raw.find("<x:xmpmeta")
        if start == -1:
            return ""

        end_marker = "</x:xmpmeta>"
        end = raw.find(end_marker, start)
        if end == -1:
            return ""

        end += len(end_marker)
        return raw[start:end]

    @staticmethod
    def _normalize_attribute_name(attr_name: str) -> str:
        if not attr_name.startswith("{"):
            return attr_name

        namespace, local_name = attr_name[1:].split("}", 1)
        prefix = XmpUtil._NAMESPACE_PREFIXES.get(namespace, namespace)
        return f"{prefix}:{local_name}"

    @staticmethod
    def _parse_xmp_xml(xmp_text: str) -> dict:
        data = {}

        try:
            root = ET.fromstring(xmp_text)  # nosec B314  # defusedxml nao disponivel; XMP extraido de arquivos confiaveis
        except ET.ParseError as exc:
            data["xmp_erro"] = str(exc)
            return data

        description = root.find(
            ".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
        )
        if description is None:
            data["xmp_erro"] = "Bloco rdf:Description nao encontrado"
            return data

        for attr_name, attr_value in description.attrib.items():
            data[XmpUtil._normalize_attribute_name(attr_name)] = attr_value

        return data

    @staticmethod
    def _order_fields_by_priority(xmp_data: dict) -> dict:
        ordered = {}

        for key in XmpUtil._FIELD_PRIORITY:
            if key in xmp_data:
                ordered[key] = xmp_data[key]

        for key in sorted(xmp_data):
            if key not in ordered:
                ordered[key] = xmp_data[key]

        return ordered

    @staticmethod
    def _to_numeric(value: str):
        """
        Tenta converter valor string para int ou float.
        Mantem string original se falhar.

        Lida com: '+123.4', '-89.90', '1.20000', '50', '-1', '0.000'
        """
        if value is None:
            return None
        if not isinstance(value, str):
            return value

        raw = value.strip().replace("+", "")
        if not raw or raw.lower() in ("none", "null", "nan", "inf"):
            return value

        logger = XmpUtil._get_logger()
        # Tenta int primeiro (se nao tiver ponto decimal)
        if "." not in raw:
            try:
                return int(raw)
            except (ValueError, TypeError) as e:
                logger.debug(
                    f"_to_numeric: int falhou para '{raw}'", error=str(e))

        # Tenta float
        try:
            return float(raw)
        except (ValueError, TypeError) as e:
            logger.debug(
                f"_to_numeric: float falhou para '{raw}'", error=str(e))
            return value

    @staticmethod
    def parse_dewarp_string(dewarp_raw: str) -> dict:
        """
        Interpreta a string XMP:DewarpData e retorna dicionario com
        campos individuais (DewarpDate, DewarpFocalX, ...).

        As chaves retornadas sao os valores dos enum MetadataFieldKey
        (ex.: MetadataFieldKey.DEWARP_FOCAL_X.value = "DewarpFocalX"),
        garantindo consistencia com o catalogo MetadataFields.

        Formato esperado::

            YYYY-MM-DD;focal_x,focal_y,cx,cy,k1,k2,k3,p1,p2

        Exemplo::

            2022-06-08;3713.29,3713.29,7.02,-8.72,-0.11257524,0.01487443,-8.572e-05,1e-07,-0.02706411

        Returns:
            dict com chaves canonicas (ex.: "DewarpDate", "DewarpFocalX", "DewarpCx", ...)
            ou dict vazio se o parse falhar.
        """
        result = {}
        if not dewarp_raw or not isinstance(dewarp_raw, str):
            return result

        parts = dewarp_raw.split(";")
        if len(parts) < 2:
            return result

        # Data — usa MetadataFieldKey.DEWARP_DATE.value
        result[MetadataFieldKey.DEWARP_DATE.value] = parts[0].strip()

        logger = XmpUtil._get_logger()
        # Valores numericos
        try:
            vals = list(map(float, parts[1].split(",")))
        except (ValueError, TypeError) as e:
            logger.debug(
                f"parse_dewarp_string: falha ao converter valores numericos: '{parts[1]}'", error=str(e))
            return result

        # Mapeamento posicional usando MetadataFieldKey enum values
        dewarp_keys = [
            MetadataFieldKey.DEWARP_FOCAL_X.value,
            MetadataFieldKey.DEWARP_FOCAL_Y.value,
            MetadataFieldKey.DEWARP_CX.value,
            MetadataFieldKey.DEWARP_CY.value,
            MetadataFieldKey.DEWARP_K1.value,
            MetadataFieldKey.DEWARP_K2.value,
            MetadataFieldKey.DEWARP_K3.value,
            MetadataFieldKey.DEWARP_P1.value,
            MetadataFieldKey.DEWARP_P2.value,
        ]

        for i, key in enumerate(dewarp_keys):
            if i < len(vals):
                result[key] = vals[i]

        return result

    @staticmethod
    def _sanitize_metadata(data: dict, logger: LogUtils) -> dict:
        """
        Valida e sanitiza metadata contra MetadataFields.

        Mapeia nomes de campos ilegais para campos canonicos usando MetadataFields.sanitize_field_name().
        Campos nao autorizados sao ignorados.
        Converte valores numericos de string para float/int automaticamente.

        Args:
            data: Dicionario bruto com campos potencialmente ilegais
            logger: Logger para registrar campos rejeitados

        Returns:
            Dicionario com apenas campos autorizados, com nomes sanitizados e valores convertidos
        """
        sanitized = {}
        rejected = []

        for field_name, field_value in data.items():
            # Tenta sanitizar o nome do campo
            canonical_name = MetadataFields.sanitize_field_name(field_name)

            if canonical_name:
                # Campo e autorizado - converte valor para numerico se possivel
                if canonical_name not in sanitized:
                    sanitized[canonical_name] = XmpUtil._to_numeric(
                        field_value)
            else:
                # Campo nao e autorizado - registra rejeicao
                rejected.append(field_name)

        # Log de campos rejeitados
        if rejected:
            logger.debug(
                f"Campos rejeitados (nao autorizados em MetadataFields): {sorted(set(rejected))}"
            )

        return sanitized

    @staticmethod
    def _extract_file_metadata(image_path: str) -> dict:
        """
        Extrai metadados do arquivo do sistema operacional.

        Retorna campos CANONICOS (legalizados em MetadataFields):
        - File: nome do arquivo
        - Path: caminho completo
        - SizeMb: tamanho em megabytes
        - DateTime: data de criacao do arquivo
        """
        stat = os.stat(image_path)
        return {
            "File": os.path.basename(image_path),
            "Path": image_path,
            "SizeMb": round(stat.st_size / (1024 * 1024), 2),
            "DateTime": datetime.fromtimestamp(stat.st_ctime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    @staticmethod
    def extract_metadata(image_path: str, tool_key: str = ToolKey.UNTRACEABLE) -> dict:
        """
        Extrai metadados XMP de uma imagem com validacao contra MetadataFields.

        Apenas campos autorizados em MetadataFields sao retornados.
        Campos ilegais sao silenciosamente descartados (log em DEBUG).

        Args:
            image_path: Caminho para a imagem
            tool_key: Chave de ferramenta para logging

        Returns:
            Dicionario com metadados sanitizados (apenas campos autorizados)
        """
        logger = XmpUtil._get_logger(tool_key)
        data = {}

        try:
            # Extrai metadados do arquivo (retorna nomes canonicos)
            data = XmpUtil._extract_file_metadata(image_path)

            # Extrai XMP bruto
            xmp_text = XmpUtil._extract_xmp_text_raw(image_path)
            if not xmp_text:
                logger.debug(f"Nenhum bloco XMP encontrado em {image_path}")
                return data

            xmp_data = XmpUtil._parse_xmp_xml(xmp_text)
            if "xmp_erro" in xmp_data:
                logger.warning(
                    f"Erro ao parsear XMP em {image_path}: {xmp_data.get('xmp_erro')}"
                )
                return data

            # SANITIZA dados XMP antes de adicionar ao resultado
            ordered_data = XmpUtil._order_fields_by_priority(xmp_data)
            sanitized_xmp = XmpUtil._sanitize_metadata(ordered_data, logger)

            # ── Parsing do DewarpData ──
            # O campo bruto "drone-dji:DewarpData" nao e autorizado em MetadataFields,
            # mas seus valores individuais (focal_x, cx, cy, k1..k3, p1..p2, date) sao.
            # Extrai o raw, parseia e adiciona ao resultado sanitizado.
            dewarp_raw = ordered_data.get("drone-dji:DewarpData")
            if dewarp_raw:
                dewarp_parsed = XmpUtil.parse_dewarp_string(str(dewarp_raw))
                if dewarp_parsed:
                    # Os campos retornados por parse_dewarp_string sao nomes canonicos
                    # (ex.: DewarpDate, DewarpFocalX, ...) e serao mapeados corretamente
                    # pelo sanitize_field_name / _sanitize_metadata
                    sanitized_dewarp = XmpUtil._sanitize_metadata(
                        dewarp_parsed, logger)
                    sanitized_xmp.update(sanitized_dewarp)

            # Mescla dados sanitizados
            data.update(sanitized_xmp)
            return data

        except Exception as exc:
            logger.error(
                f"Erro ao extrair metadata XMP de {image_path}: {exc}")
            # Retorna pelo menos os metadados de arquivo (legalizados)
            return data

    @staticmethod
    def process_directory(
        base_folder: str,
        output_file: str = "relatorio_xmp.txt",
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> str:
        logger = XmpUtil._get_logger(tool_key)
        output_path = os.path.join(base_folder, output_file)
        all_data = []

        for root, _, files in os.walk(base_folder):
            for name in sorted(files):
                if not name.lower().endswith((".jpg", ".jpeg")):
                    continue

                full_path = os.path.join(root, name)
                try:
                    all_data.append(
                        XmpUtil.extract_metadata(full_path, tool_key=tool_key)
                    )
                except Exception as exc:
                    all_data.append(
                        {
                            "arquivo": name,
                            "caminho": full_path,
                            "erro": str(exc),
                        }
                    )

        with open(output_path, "w", encoding="utf-8") as fh:
            for index, item in enumerate(all_data, 1):
                fh.write(f"{'=' * 60}\n")
                fh.write(f"FOTO {index}\n")
                fh.write(f"{'=' * 60}\n")
                for key, value in item.items():
                    fh.write(f"{key}: {value}\n")
                fh.write("\n")

        logger.info(
            "Relatorio XMP gerado",
            data={"output_path": output_path, "total_photos": len(all_data)},
        )
        return output_path
