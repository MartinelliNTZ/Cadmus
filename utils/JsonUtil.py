# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from .BaseUtil import BaseUtil


class JsonUtil(BaseUtil):
    """
    Constroi o JSON e tambem e responsavel por manipulacao do mesmo.

    Métodos estáticos, tool_key em todos os métodos que logam.
    """

    @staticmethod
    def build(
        records: List[Dict[str, Any]],
        source: str,
        base_folder: str,
        tool_key: str,
        recursive: bool = False,
        timestamps: Optional[Dict[str, str]] = None,
        project_title: str = "",
        logo_path: str = "",
    ) -> Dict[str, Any]:
        logger = BaseUtil._get_logger(tool_key)

        normalized_records = records or []

        with_coords = 0
        without_coords = 0
        with_xmp = 0
        with_exif_gps = 0
        missing_xmp_and_exif = 0

        for r in normalized_records:
            source_txt = str(r.get("CoordSource") or "").strip().upper()
            if source_txt and source_txt != "NONE":
                with_coords += 1
            else:
                without_coords += 1

            has_xmp_raw = r.get("HasXmp")
            has_exif_gps_raw = r.get("HasExifGps")
            source_hint = str(r.get("CoordSource") or "").strip().upper()
            has_xmp = bool(has_xmp_raw) or source_hint == "XMP"
            has_exif_gps = bool(has_exif_gps_raw) or source_hint == "EXIF"
            if has_xmp:
                with_xmp += 1
            if has_exif_gps:
                with_exif_gps += 1
            if (not has_xmp) and (not has_exif_gps):
                missing_xmp_and_exif += 1

        quality = {
            "total_files": len(normalized_records),
            "with_coords": with_coords,
            "without_coords": without_coords,
            "with_xmp": with_xmp,
            "with_exif_gps": with_exif_gps,
            "missing_xmp_and_exif": missing_xmp_and_exif,
        }

        groups = {}
        for record in normalized_records:
            folder_key = record.get("MrkFolder") or os.path.dirname(
                record.get("Path", "")
            )
            if folder_key not in groups:
                groups[folder_key] = {
                    "MrkFile": record.get("MrkFile", ""),
                    "FlightName": record.get("FlightName", ""),
                    "FlightNumber": record.get("FlightNumber", 0),
                    "points_count": 0,
                    "indexed_count": 0,
                    "records": {},
                }

            file_key = record.get("File")
            if not file_key:
                foto = record.get("Foto")
                if foto is not None:
                    file_key = f"foto_{foto}"
                else:
                    file_key = f"record_{len(groups[folder_key]['records'])}"

            groups[folder_key]["records"][file_key] = record
            groups[folder_key]["points_count"] += 1
            groups[folder_key]["indexed_count"] += 1

        now_iso = datetime.now().isoformat()

        json_data = {
            "schema_version": "2.0",
            "source": source,
            "tool_key": tool_key,
            "base_folder": base_folder,
            "recursive": recursive,
            "generated_at": now_iso,
        }

        if project_title:
            json_data["titulo"] = project_title
        if logo_path:
            json_data["logotipo"] = logo_path

        if timestamps:
            json_data["timestamps"] = timestamps

        json_data["quality"] = quality
        json_data["groups"] = groups

        logger.debug(
            f"Built JSON v2.0 with {len(groups)} groups and {len(normalized_records)} records"
        )
        return json_data

    @staticmethod
    def save(json_data: Dict[str, Any], output_path: str) -> str:
        logger = BaseUtil._get_logger(json_data.get("tool_key", "json_util"))
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved JSON to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving JSON to {output_path}: {e}")
            raise

    @staticmethod
    def update_timestamps(
        json_path: str, new_timestamps: Dict[str, str]
    ) -> Dict[str, Any]:
        logger = BaseUtil._get_logger("json_util")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            existing = json_data.get("timestamps", {})
            existing.update(new_timestamps)
            json_data["timestamps"] = existing

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"Timestamps atualizados no JSON: {list(new_timestamps.keys())}"
            )
            return json_data
        except Exception as e:
            logger.error(f"Erro ao atualizar timestamps em {json_path}: {e}")
            raise

    @staticmethod
    def update_json(
        json_path: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Método genérico para atualizar um arquivo JSON com um dicionário de dados.

        Abre o JSON existente, mescla (update) o dict informado no nível raiz
        e salva de volta. Útil para steps que precisam adicionar dados simples
        ao cabeçalho do JSON sem criar um método específico em JsonUtil.

        Args:
            json_path: Caminho do arquivo JSON
            updates: Dict com os dados a serem inseridos/atualizados no nível raiz

        Returns:
            JSON data atualizado

        Example:
            >>> JsonUtil.update_json(json_path, {"minha_chave": {"sub": 123}})
        """
        logger = BaseUtil._get_logger("json_util")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            json_data.update(updates)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            logger.debug(
                f"Dados atualizados no JSON: {json_path}",
                data={"keys": list(updates.keys())},
            )
            return json_data
        except Exception as e:
            logger.error(f"Erro ao atualizar dados em {json_path}: {e}")
            raise

    @staticmethod
    def load_records(json_path: str) -> List[Dict[str, Any]]:
        logger = BaseUtil._get_logger("json_util")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            version = data.get("schema_version")
            if version != "2.0":
                raise ValueError(
                    f"JSON com schema_version='{version}' nao e suportado. "
                    "Regenere o JSON usando a versao atual do plugin."
                )

            records = []
            for group in data.get("groups", {}).values():
                for record in group.get("records", {}).values():
                    records.append(record)

            logger.debug(f"Loaded {len(records)} records from {json_path}")
            return records
        except Exception as e:
            logger.error(f"Error loading records from {json_path}: {e}")
            raise
