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
        re.IGNORECASE
    )

    DATE_RE = re.compile(r"DJI_(\d{8})", re.IGNORECASE)

    FILE_META_RE = re.compile(
        r"DJI_\d+_(?P<numdovoo>\d+?)_(?P<nomedovoo>[^_]+?)_Timestamp",
        re.IGNORECASE
    )

    @staticmethod
    def _extract_file_metadata(file_name: str) -> dict:
        match = MrkParser.FILE_META_RE.search(file_name)

        if not match:
            return {"numdovoo": None, "nomedovoo": None}

        return {
            "numdovoo": match.group("numdovoo"),
            "nomedovoo": match.group("nomedovoo"),
        }

    @staticmethod
    def _generate_folder_fields(file_dir: str, base_folder: str, tool_key: str="untraceable") -> dict:

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
            data[f"pasta{i}"] = name
        logger.debug(f"Generated folder fields: {data} for file_dir: {file_dir} and base_folder: {base_folder}")
        return data
    @staticmethod
    def parse_folder(folder, recursive=True, extra_fields=None, gerarpastas=True, tool_key="untraceable"):
        """
        Lê todos os MRK de uma pasta e retorna lista de pontos.
        """
        logger = MrkParser._get_logger(tool_key)

        points = []
        folder = os.path.abspath(folder)

        for root, _, files in os.walk(folder):

            for f in files:

                if not f.lower().endswith(".mrk"):
                    continue

                file_path = os.path.join(root, f)

                file_meta = MrkParser._extract_file_metadata(f)

                date_match = MrkParser.DATE_RE.search(f)
                data_mrk = date_match.group(1) if date_match else None

                folder_fields = {}
                if gerarpastas:
                    folder_fields = MrkParser._generate_folder_fields(root, folder, tool_key)
                    logger.debug(f"Generated folder fields for file: {file_path} - {folder_fields}")

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
                            "data_name": data_mrk,
                            "folder": root,
                            "mrk_file": f,
                            "mrk_path": file_path,
                            "numdovoo": file_meta["numdovoo"],
                            "nomedovoo": file_meta["nomedovoo"],
                        }
                        

                        if gerarpastas:
                            point.update(folder_fields)

                        points.append(point)
                       

            if not recursive:
                break

        if gerarpastas:
            points = MrkParser._normalize_folder_fields(points)
        logger.debug(f"Parsed point: {point} from file: {file_path}Points parsed so far: {len(points)}")
        return points
    @staticmethod
    def _normalize_folder_fields(points: list) -> list:
        """
        Garante que todos os pontos tenham os mesmos campos pasta1..pastaN.
        """
        max_n = 0

        for p in points:
            for k in p.keys():
                if k.startswith("pasta"):
                    try:
                        n = int(k[5:])
                        if n > max_n:
                            max_n = n
                    except ValueError:
                        pass

        if max_n == 0:
            return points

        for p in points:
            for i in range(1, max_n + 1):
                key = f"pasta{i}"
                if key not in p:
                    p[key] = None

        return points

    @staticmethod
    def to_point_layer(points, name="MRK_Pontos", extra_fields=None):
        from ..vector.VectorLayerGeometry import VectorLayerGeometry

        return VectorLayerGeometry.create_point_layer_from_dicts(
            points=points,
            name=name,
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
