# -*- coding: utf-8 -*-
import os
import re
from typing import List, Dict, Any

from ...core.config.LogUtils import LogUtils
from ...core.enum import MetadataFieldKey


class MrkUtil:
    """
    Extrai campos de um arquivo MRK e retorna registros normalizados.
    Chaves dos registros usam MetadataFieldKey.value (PascalCase).
    Mesmo padrão de ExifUtil e XmpUtil.
    """

    LINE_RE = re.compile(
        r"(?P<foto>\d+).*?"
        r"(?P<lat>-?\d+\.\d+),Lat.*?"
        r"(?P<lon>-?\d+\.\d+),Lon.*?"
        r"(?P<alt>-?\d+(?:\.\d+)?),Ellh",
        re.IGNORECASE,
    )

    DATE_RE = re.compile(r"DJI_(\d{8})", re.IGNORECASE)

    FILE_META_RE = re.compile(
        r"DJI_\d+_(?P<flight_number>\d+?)_(?P<flight_name>[^_]+?)_Timestamp",
        re.IGNORECASE,
    )

    @staticmethod
    def extract_records(mrk_path: str) -> List[Dict[str, Any]]:
        """
        Lê um arquivo MRK e retorna lista de registros.
        Cada registro contém:
          - MetadataFieldKey.FOTO.value       → número da foto
          - MetadataFieldKey.LAT.value        → latitude MRK
          - MetadataFieldKey.LON.value        → longitude MRK
          - MetadataFieldKey.ALT.value        → altitude MRK
          - MetadataFieldKey.DATE_NAME.value  → data derivada do nome
          - MetadataFieldKey.MRK_FILE.value   → nome do arquivo MRK
          - MetadataFieldKey.MRK_PATH.value   → caminho absoluto do MRK
          - MetadataFieldKey.MRK_FOLDER.value → pasta do MRK
          - MetadataFieldKey.FLIGHT_NUMBER.value
          - MetadataFieldKey.FLIGHT_NAME.value
          - MetadataFieldKey.FOLDER_LEVEL_1.value
          - MetadataFieldKey.FOLDER_LEVEL_2.value
          - MetadataFieldKey.COORD_SOURCE.value → "MRK"
          - MetadataFieldKey.QUALITY_FLAG.value → "ok"
        """
        logger = LogUtils(tool="mrk_util", class_name="MrkUtil")
        records = []

        try:
            with open(mrk_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extrair metadata do arquivo
            file_meta = MrkUtil._extract_file_metadata(os.path.basename(mrk_path))
            mrk_folder = os.path.dirname(mrk_path)
            mrk_file = os.path.basename(mrk_path)

            # Extrair campos de pasta
            folder_fields = MrkUtil._generate_folder_fields(mrk_folder, mrk_folder, "mrk_util")

            # Processar cada linha
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue

                match = MrkUtil.LINE_RE.search(line)
                if match:
                    record = {
                        MetadataFieldKey.FOTO.value: int(match.group('foto')),
                        MetadataFieldKey.LAT.value: float(match.group('lat')),
                        MetadataFieldKey.LON.value: float(match.group('lon')),
                        MetadataFieldKey.ALT.value: float(match.group('alt')),
                        MetadataFieldKey.MRK_FILE.value: mrk_file,
                        MetadataFieldKey.MRK_PATH.value: mrk_path,
                        MetadataFieldKey.MRK_FOLDER.value: mrk_folder,
                        MetadataFieldKey.FLIGHT_NUMBER.value: file_meta.get('flight_number'),
                        MetadataFieldKey.FLIGHT_NAME.value: file_meta.get('flight_name'),
                        MetadataFieldKey.COORD_SOURCE.value: "MRK",
                        MetadataFieldKey.QUALITY_FLAG.value: "ok",
                    }

                    # Adicionar campos de pasta
                    for i in range(1, 3):  # folder_level_1, folder_level_2
                        key = f"folder_level_{i}"
                        if key in folder_fields:
                            record[MetadataFieldKey.FOLDER_LEVEL_1.value if i == 1 else MetadataFieldKey.FOLDER_LEVEL_2.value] = folder_fields[key]

                    # Extrair data do nome do arquivo
                    date_match = MrkUtil.DATE_RE.search(mrk_file)
                    if date_match:
                        record[MetadataFieldKey.DATE_NAME.value] = date_match.group(1)

                    records.append(record)

            logger.debug(f"Extracted {len(records)} records from {mrk_path}")

        except Exception as e:
            logger.error(f"Error extracting records from {mrk_path}: {e}")
            raise

        return records

    @staticmethod
    def extract_folder(mrk_folder: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Varre pasta de arquivos MRK e agrega todos os registros.
        """
        logger = LogUtils(tool="mrk_util", class_name="MrkUtil")
        all_records = []

        mrk_folder = os.path.abspath(mrk_folder)

        try:
            for root, _, files in os.walk(mrk_folder):
                if not recursive and root != mrk_folder:
                    continue

                for f in files:
                    if f.lower().endswith('.mrk'):
                        mrk_path = os.path.join(root, f)
                        records = MrkUtil.extract_records(mrk_path)
                        all_records.extend(records)

            logger.debug(f"Extracted {len(all_records)} total records from folder {mrk_folder}")

        except Exception as e:
            logger.error(f"Error extracting folder {mrk_folder}: {e}")
            raise

        return all_records

    @staticmethod
    def _extract_file_metadata(file_name: str) -> Dict[str, Any]:
        match = MrkUtil.FILE_META_RE.search(file_name)

        if not match:
            return {"flight_number": None, "flight_name": None}

        return {
            "flight_number": int(match.group("flight_number")),
            "flight_name": match.group("flight_name"),
        }

    @staticmethod
    def _generate_folder_fields(
        file_dir: str, base_folder: str, tool_key: str = "mrk_util"
    ) -> Dict[str, str]:
        file_dir = os.path.abspath(file_dir)
        base_folder = os.path.abspath(base_folder)
        logger = LogUtils(tool=tool_key, class_name="MrkUtil")

        folders = []
        current = file_dir

        while True:
            name = os.path.basename(current)
            if name:
                folders.append(name)

            if current.lower() == base_folder.lower():
                break

            parent = os.path.dirname(current)

            if parent == current:
                break

            current = parent

        data = {}
        for i, name in enumerate(folders, 1):
            data[f"folder_level_{i}"] = name

        logger.debug(
            f"Generated folder fields: {data} for file_dir: {file_dir} and base_folder: {base_folder}"
        )
        return data

    @staticmethod
    def _get_logger(tool_key):
        return LogUtils(tool=tool_key, class_name="MrkUtil")
