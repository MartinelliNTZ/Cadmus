# -*- coding: utf-8 -*-
"""
InitialParamsUtil - Etapa 1 do pipeline de enriquecimento de fotos.

RESPONSABILIDADE ÚNICA:
    Gerar o JSON inicial (esqueleto) com os campos básicos de cada foto:
    - File, Path
    - FolderLevel1..FolderLevel5
    - FlightNumber, FlightName

DIFERENCIAL:
    Escreve diretamente em disco (JSON) para evitar uso excessivo de memória
    em pastas com milhares de fotos. O JSON gerado segue o schema v2.0.

FLUXO:
    1. Varre o diretório de fotos
    2. Para cada foto .JPG, extrai:
       - File, Path
       - FolderLevel1..FolderLevel5 (pelo caminho relativo)
       - FlightNumber, FlightName (pelo nome da pasta DJI_*_NNN_NAME)
    3. Monta cabeçalho com metadados da execução
    4. Salva em disco e retorna o caminho do JSON
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from ...core.config.LogUtils import LogUtils
from ...core.enum import MetadataFieldKey


class InitialParamsUtil:
    """
    Gera o JSON inicial (Etapa 1) do pipeline de metadados.
    """

    # Regex para identificar fotos DJI: _0001_V.JPG, _0001_W.JPG etc.
    DJI_RE = re.compile(r"_(\d{4})_[A-Z]\.JPG$", re.IGNORECASE)

    # Regex para extrair FlightNumber e FlightName do nome da pasta
    # Ex: "DJI_202605101003_001_IRIA01" → number=1, name=IRIA01
    FLIGHT_FOLDER_RE = re.compile(
        r"DJI_\d+_(?P<flight_number>\d+?)_(?P<flight_name>[^_]+)",
        re.IGNORECASE,
    )

    @staticmethod
    def _get_logger(tool_key: str) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="InitialParamsUtil")

    @staticmethod
    def build_initial_json(
        base_folder: str,
        tool_key: str = "drone_coordinates",
        recursive: bool = True,
    ) -> Optional[Dict]:
        """
        Gera o dict do JSON inicial (esqueleto) com os campos básicos de cada foto.

        Args:
            base_folder: Pasta raiz onde as fotos estão localizadas
            tool_key: Chave da ferramenta para logging
            recursive: Se deve varrer subpastas recursivamente

        Returns:
            Dict com a estrutura:
                {"total_files": N, "timestamps": {...}, "groups": {"folder": {"records": {filename: record}}}}
            O dict NÃO é salvo em disco - o caller (PhotoMetadata) faz o save final.
        """
        logger = InitialParamsUtil._get_logger(tool_key)
        initial_start = datetime.now().isoformat()

        logger.info(
            "Iniciando geracao do esqueleto inicial (Etapa 1)",
            data={
                "base_folder": base_folder,
                "recursive": recursive,
            },
        )

        # ── Escaneia fotos e monta esqueleto ──
        skeleton = InitialParamsUtil._build_file_skeleton(base_folder, recursive)

        if not skeleton:
            logger.warning("Nenhuma foto encontrada no diretorio")
            initial_end = datetime.now().isoformat()
            return {
                "total_files": 0,
                "timestamps": {
                    "initial_start": initial_start,
                    "initial_end": initial_end,
                },
                "skeleton": {},
            }

        initial_end = datetime.now().isoformat()

        logger.info(
            "Esqueleto inicial gerado",
            data={
                "total_files": len(skeleton),
            },
        )

        return {
            "total_files": len(skeleton),
            "timestamps": {
                "initial_start": initial_start,
                "initial_end": initial_end,
            },
            "skeleton": skeleton,
        }

    # ─────────────────────────────────────────────
    # Varredura de fotos
    # ─────────────────────────────────────────────

    @staticmethod
    def _build_file_skeleton(
        base_folder: str,
        recursive: bool,
    ) -> Dict[str, dict]:
        """
        Varre o diretório de fotos e cria um dicionário onde cada chave
        é o nome do arquivo da foto (filename). Para cada registro, já
        são calculados e armazenados:

        - File, Path
        - FolderLevel1..FolderLevel5 (determinístico pelo path real)
        - FlightNumber, FlightName (extraídos do nome da pasta mais profunda
          que segue o padrão DJI_YYYYMMDD_HHMMSS_NNN_NAME)
        """
        skeleton: Dict[str, dict] = {}

        walker = os.walk(base_folder) if recursive else [(base_folder, [], os.listdir(base_folder))]
        for root, _, files in walker:
            for fname in files:
                if not fname.lower().endswith(".jpg"):
                    continue
                match = InitialParamsUtil.DJI_RE.search(fname)
                if not match:
                    continue

                abs_path = os.path.join(root, fname)

                # Calcula FolderLevels subindo a hierarquia de pastas
                rel_path = os.path.relpath(root, base_folder)
                folder_levels = InitialParamsUtil._extract_folder_levels(rel_path)

                # ── Correção: quando rel_path == "." (fotos diretamente na base_folder) ──
                current_folder_name = os.path.basename(root)

                if rel_path == ".":
                    if not folder_levels.get("FolderLevel1"):
                        folder_levels["FolderLevel1"] = current_folder_name
                    path_parts = [current_folder_name]
                else:
                    path_parts = rel_path.replace("\\", "/").strip("/").split("/")

                # Extrai FlightNumber e FlightName
                flight_number = None
                flight_name = None
                for part in reversed(path_parts):
                    fm = InitialParamsUtil.FLIGHT_FOLDER_RE.search(part)
                    if fm:
                        try:
                            flight_number = int(fm.group("flight_number"))
                        except (ValueError, TypeError):
                            flight_number = None
                        flight_name = fm.group("flight_name")
                        break

                record = {
                    MetadataFieldKey.FILE.value: fname,
                    MetadataFieldKey.PATH.value: abs_path,
                    MetadataFieldKey.FOLDER_LEVEL_1.value: folder_levels.get("FolderLevel1", ""),
                    MetadataFieldKey.FOLDER_LEVEL_2.value: folder_levels.get("FolderLevel2", ""),
                    MetadataFieldKey.FOLDER_LEVEL_3.value: folder_levels.get("FolderLevel3", ""),
                    MetadataFieldKey.FOLDER_LEVEL_4.value: folder_levels.get("FolderLevel4", ""),
                    MetadataFieldKey.FOLDER_LEVEL_5.value: folder_levels.get("FolderLevel5", ""),
                    MetadataFieldKey.FLIGHT_NUMBER.value: flight_number,
                    MetadataFieldKey.FLIGHT_NAME.value: flight_name,
                }

                skeleton[fname] = record

        return skeleton

    @staticmethod
    def _extract_folder_levels(rel_path: str) -> Dict[str, str]:
        """
        Extrai FolderLevel1..FolderLevel5 de um caminho relativo.

        A lógica inverte a ordem das pastas: FolderLevel1 é a pasta mais
        próxima do arquivo (immediate parent), FolderLevel2 é a pai desta,
        e assim sucessivamente.

        Exemplo:
            Path: "10052026/M3E/IMAGEM/DJI_202605101003_001_IRIA01"
            FolderLevel1 = "DJI_202605101003_001_IRIA01" (pasta da foto)
            FolderLevel2 = "IMAGEM"
            FolderLevel3 = "M3E"
            FolderLevel4 = "10052026"
        """
        if not rel_path or rel_path == ".":
            return {}

        parts = rel_path.replace("\\", "/").strip("/").split("/")
        # Inverte para que FolderLevel1 seja a pasta mais próxima da foto
        reversed_parts = list(reversed(parts))

        levels = {}
        for i in range(min(len(reversed_parts), 5)):
            levels[f"FolderLevel{i + 1}"] = reversed_parts[i]

        return levels

    @staticmethod
    def load_initial_json(json_path: str) -> Optional[List[Dict]]:
        """
        Carrega o JSON inicial e retorna a lista de registros (dicts).

        Args:
            json_path: Caminho do JSON gerado por build_initial_json

        Returns:
            Lista de registros (dicts) ou None se erro
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            records = []
            for group in data.get("groups", {}).values():
                for record in group.get("records", {}).values():
                    records.append(record)

            return records
        except Exception:
            return None

    @staticmethod
    def update_metadata_json(
        json_path: str,
        new_timestamp_key: str,
        new_timestamp_value: str,
        new_data: dict,
    ) -> bool:
        """
        Atualiza o JSON inicial com novos dados (ex: após EXIF, XMP, etc.).

        Args:
            json_path: Caminho do JSON
            new_timestamp_key: Nome do timestamp a adicionar (ex: "exif_start")
            new_timestamp_value: Valor do timestamp
            new_data: Dict com novos campos para mesclar nos registros

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Atualiza timestamps
            if "timestamps" not in data:
                data["timestamps"] = {}
            data["timestamps"][new_timestamp_key] = new_timestamp_value

            # Mescla novos dados nos registros
            for group in data.get("groups", {}).values():
                for filename, record in group.get("records", {}).items():
                    for k, v in new_data.get(filename, {}).items():
                        if k not in record or record.get(k) in (None, "", "None", "null"):
                            record[k] = v

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True
        except Exception:
            return False
