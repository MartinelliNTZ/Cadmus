# -*- coding: utf-8 -*-
"""
Utilities para extracao de metadados EXIF/OS/PIL de imagens.
"""

import os
from datetime import datetime

from PIL import ExifTags, Image

from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey
from .MetadataFields import MetadataFields


class ExifUtil:
    """Utilitario para extrair metadados de arquivo de imagem."""

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="ExifUtil")

    @staticmethod
    def extract_metadata_os(
        image_path: str, tool_key: str = ToolKey.UNTRACEABLE
    ) -> dict:
        """
        Extrai metadados do sistema operacional.

        Retorna campos CANONICOS (legalizados em MetadataFields):
        - File: nome do arquivo (era "file")
        - Path: caminho completo (era "path")
        - SizeMb: tamanho em MB (era "size_mb")
        - DateTime: data do sistema operacional (era "os_date")
        """
        logger = ExifUtil._get_logger(tool_key)
        data = {}
        try:
            stat = os.stat(image_path)
            data["File"] = os.path.basename(image_path)
            data["Path"] = image_path
            data["SizeMb"] = round(stat.st_size / (1024 * 1024), 2)
            data["DateTime"] = datetime.fromtimestamp(stat.st_ctime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception as exc:
            logger.error(
                f"Erro ao extrair metadados do sistema para {image_path}: {exc}"
            )
        return data

    @staticmethod
    def extract_metadata_image(
        image_path: str, tool_key: str = ToolKey.UNTRACEABLE
    ) -> dict:
        """
        Extrai metadados de dimensao/formato/dpi via PIL.

        Retorna campos CANONICOS (legalizados em MetadataFields):
        - ExifImageWidth: largura em pixels (era "width_px")
        - ExifImageHeight: altura em pixels (era "height_px")
        - Format: formato_modo (era "format")
        - DPIWidth: DPI horizontal (era "dpi")
        """
        logger = ExifUtil._get_logger(tool_key)
        data = {}
        try:
            with Image.open(image_path) as img:
                data["ExifImageWidth"], data["ExifImageHeight"] = img.size
                data["Format"] = f"{img.format}_{img.mode}"
                dpi = img.info.get("dpi")
                if dpi:
                    dpi_x, dpi_y = dpi
                    data["DPIWidth"] = dpi_x
                    data["DPIHeight"] = dpi_y
        except Exception as exc:
            logger.error(f"Erro ao extrair metadados PIL para {image_path}: {exc}")
        return data

    @staticmethod
    def _to_numeric(value):
        """
        Tenta converter valor string para int ou float.
        Mantem tipo original se ja for numerico ou se falhar.
        """
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        if not isinstance(value, str):
            return value

        raw = value.strip().replace("+", "")
        if not raw or raw.lower() in ("none", "null", "nan", "inf"):
            return value

        # Tenta int primeiro
        if "." not in raw:
            try:
                return int(raw)
            except (ValueError, TypeError):
                pass

        # Tenta float
        try:
            return float(raw)
        except (ValueError, TypeError):
            return value

    @staticmethod
    def _dms_to_decimal(dms_tuple, ref):
        """
        Converte tupla DMS (graus, minutos, segundos) para decimal com sinal.

        Args:
            dms_tuple: Tupla/list com 3 valores (graus, minutos, segundos)
            ref: Referencia 'N'/'S' para latitude ou 'E'/'W' para longitude

        Returns:
            float: Valor decimal com sinal (negativo para S/W), ou None se invalido
        """
        if dms_tuple is None:
            return None
        try:
            parts = list(dms_tuple)
            if len(parts) < 3:
                return None

            def _to_float(p):
                if isinstance(p, (int, float)):
                    return float(p)
                text = str(p).strip()
                if "/" in text:
                    num, den = text.split("/", 1)
                    return float(num) / float(den) if float(den) != 0 else 0.0
                return float(text)

            deg = _to_float(parts[0])
            minute = _to_float(parts[1])
            sec = _to_float(parts[2])
            decimal = deg + (minute / 60.0) + (sec / 3600.0)

            ref_txt = str(ref or "").strip().upper()
            if ref_txt in ("S", "W"):
                decimal = -decimal
            return decimal
        except Exception:
            return None

    @staticmethod
    def extract_metadata_exif(
        image_path: str, tool_key: str = ToolKey.UNTRACEABLE
    ) -> dict:
        """
        Extrai e sanitiza campos EXIF disponiveis.

        Converte automaticamente coordenadas DMS (GPSLatitude/GPSLongitude) para
        decimal com sinal, armazenando o resultado em GpsLatitudeRef/GpsLongitudeRef.

        Campos retornados:
        - GpsLatitude: tupla DMS original (RAW) - pode ser sobrescrito pelo XMP
        - GpsLatitudeRef: decimal com sinal (ex: -13.11816) - EXCLUSIVO do EXIF
        - GpsLongitude: tupla DMS original (RAW) - pode ser sobrescrito pelo XMP
        - GpsLongitudeRef: decimal com sinal (ex: -54.79313) - EXCLUSIVO do EXIF

        Apenas campos autorizados em MetadataFields sao retornados.
        Campos nao autorizados sao descartados (log em DEBUG).
        """
        logger = ExifUtil._get_logger(tool_key)
        data = {}
        try:
            with Image.open(image_path) as img:
                exif_raw = img._getexif() or {}
                exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}

                # Expande GPSInfo para chaves individuais
                gps_info = exif.get("GPSInfo")
                if isinstance(gps_info, dict):
                    gps_named = {
                        ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info.items()
                    }
                    for gk, gv in gps_named.items():
                        exif[gk] = gv

                # SANITIZA campos EXIF contra MetadataFields
                for key, value in exif.items():
                    canonical_name = MetadataFields.sanitize_field_name(str(key))
                    if canonical_name:
                        data[canonical_name] = ExifUtil._to_numeric(value)
                    else:
                        logger.debug(f"Campo EXIF rejeitado (nao autorizado): {key}")

                # ── Converte DMS → decimal com sinal ──
                # GpsLat (tupla DMS) + GpsLatRef ("S"/"N") → GpsLatRef (decimal)
                # GpsLong (tupla DMS) + GpsLongRef ("E"/"W") → GpsLongRef (decimal)
                lat_raw = data.get("GpsLat")  # tupla DMS
                lat_ref = data.get("GpsLatRef", "")  # "S" ou "N"
                lon_raw = data.get("GPSLong")  # tupla DMS
                lon_ref = data.get("GpsLongRef", "")  # "W" ou "E"

                if isinstance(lat_raw, (list, tuple)):
                    dec_lat = ExifUtil._dms_to_decimal(lat_raw, lat_ref)
                    if dec_lat is not None:
                        data["GpsLatRef"] = dec_lat
                if isinstance(lon_raw, (list, tuple)):
                    dec_lon = ExifUtil._dms_to_decimal(lon_raw, lon_ref)
                    if dec_lon is not None:
                        data["GpsLongRef"] = dec_lon

        except Exception as exc:
            logger.warning(f"Erro ao extrair EXIF de {image_path}: {exc}")

        return data
