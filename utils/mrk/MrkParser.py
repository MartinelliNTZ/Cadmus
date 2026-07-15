# -*- coding: utf-8 -*-
import os
import re

from ...core.config.LogUtils import LogUtils


class MrkParser:

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
    def _extract_file_metadata(file_name: str) -> dict:
        match = MrkParser.FILE_META_RE.search(file_name)

        if not match:
            return {"flight_number": None, "flight_name": None}

        return {
            "flight_number": match.group("flight_number"),
            "flight_name": match.group("flight_name"),
        }

    @staticmethod
    def _generate_folder_fields(
        file_dir: str, base_folder: str, tool_key: str = "untraceable"
    ) -> dict:

        file_dir = os.path.abspath(file_dir)
        base_folder = os.path.abspath(base_folder)
        logger = LogUtils(tool=tool_key, class_name="MrkParser")

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
            data[f"folder_level{i}"] = name
        logger.debug(
            f"Generated folder fields: {data} for file_dir: {file_dir} and base_folder: {base_folder}"
        )
        return data

    @staticmethod
    def parse_folder(
        folder,
        recursive=True,
        extra_fields=None,
        gerarpastas=True,
        tool_key="untraceable",
    ):
        """
        Lê todos os MRK de uma pasta e retorna lista de pontos.
        """
        logger = MrkParser._get_logger(tool_key)

        points = []
        folder = os.path.abspath(folder)

        total_files = 0
        for root, _, files in os.walk(folder):
            for f in files:
                if not f.lower().endswith(".mrk"):
                    continue

                file_path = os.path.join(root, f)
                file_points = MrkParser.parse_file(
                    file_path,
                    base_folder=folder,
                    extra_fields=extra_fields,
                    gerarpastas=gerarpastas,
                    tool_key=tool_key,
                )
                total_files += 1
                points.extend(file_points)

            if not recursive:
                break

        if gerarpastas:
            points = MrkParser._normalize_folder_fields(points)

        logger.debug(
            "MRK folder parsing completed",
            code="MRK_FOLDER_PARSED",
            folder=folder,
            mrk_count=total_files,
            points_count=len(points),
            recursive=recursive,
        )
        return points

    @staticmethod
    def parse_file(
        file_path,
        base_folder=None,
        extra_fields=None,
        gerarpastas=True,
        tool_key="untraceable",
    ):
        """
        Lê um único arquivo MRK e retorna lista de pontos.
        """
        logger = MrkParser._get_logger(tool_key)

        if not file_path:
            return []

        file_path = os.path.abspath(file_path)
        if not os.path.isfile(file_path):
            logger.warning(
                "MRK file not found",
                code="MRK_FILE_NOT_FOUND",
                file_path=file_path,
            )
            return []

        root = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        base_folder = os.path.abspath(base_folder or root)

        file_meta = MrkParser._extract_file_metadata(file_name)
        date_match = MrkParser.DATE_RE.search(file_name)
        data_mrk = date_match.group(1) if date_match else None

        folder_fields = {}
        if gerarpastas:
            folder_fields = MrkParser._generate_folder_fields(root, base_folder, tool_key)
            logger.debug(
                f"Generated folder fields for file: {file_path} - {folder_fields}"
            )

        points = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                m = MrkParser.LINE_RE.search(line)
                if not m:
                    continue

                point = {
                    "foto": int(m.group("foto")),
                    "lat": float(m.group("lat")),
                    "lon": float(m.group("lon")),
                    "alt": float(m.group("alt")),
                    "date_name": data_mrk,
                    "folder": os.path.basename(root),
                    "folder_path": root,
                    "mrk_file": file_name,
                    "mrk_path": file_path,
                    "flight_number": file_meta["flight_number"],
                    "flight_name": file_meta["flight_name"],
                }

                if gerarpastas:
                    point.update(folder_fields)

                points.append(point)

        if gerarpastas:
            points = MrkParser._normalize_folder_fields(points)

        logger.debug(
            "MRK file parsing completed",
            code="MRK_FILE_PARSED",
            file_path=file_path,
            points_count=len(points),
        )
        return points

    @staticmethod
    def _normalize_folder_fields(points: list) -> list:
        """
        Garante que todos os pontos tenham os mesmos campos folder_level1..folder_levelN.
        """
        max_n = 0

        for p in points:
            for k in p.keys():
                if k.startswith("folder_level"):
                    try:
                        n = int(k[len("folder_level"):])
                        if n > max_n:
                            max_n = n
                    except ValueError as e:
                        logger = LogUtils(tool="mrk_parser", class_name="MrkParser")
                        logger.warning(
                            f"Unexpected folder field format: {k} in point: {p}. Error: {e}"
                        )

        if max_n == 0:
            return points

        for p in points:
            for i in range(1, max_n + 1):
                key = f"folder_level{i}"
                if key not in p:
                    p[key] = None

        return points

    @staticmethod
    def to_point_layer(points, name="MRK_Pontos", extra_fields=None):
        from ..vector.VectorLayerGeometry import VectorLayerGeometry
        from .MetadataFields import MetadataFields
        from qgis.PyQt.QtCore import QVariant

        field_specs = [
            ("foto", QVariant.Int, MetadataFields.resolve_output_name("foto")),
            ("alt", QVariant.Double, MetadataFields.resolve_output_name("alt")),
            ("date_name", QVariant.String, MetadataFields.resolve_output_name("date_name")),
            ("flight_number", QVariant.String, MetadataFields.resolve_output_name("flight_number")),
            ("flight_name", QVariant.String, MetadataFields.resolve_output_name("flight_name")),
            ("folder_level1", QVariant.String, MetadataFields.resolve_output_name("folder_level1")),
            ("folder_level2", QVariant.String, MetadataFields.resolve_output_name("folder_level2")),
            ("mrk_folder", QVariant.String, MetadataFields.resolve_output_name("mrk_folder")),
        ]

        return VectorLayerGeometry.create_point_layer_from_dicts(
            points=points,
            name=name,
            field_specs=field_specs,
            geometry_keys=("lon", "lat"),
            extra_fields=extra_fields,
        )

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
        return LogUtils(tool=tool_key, class_name="MrkParser")
