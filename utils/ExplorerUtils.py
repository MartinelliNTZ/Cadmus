import os
from pathlib import Path
from typing import List, Dict

from ..core.config.LogUtils import LogUtils
from .vector.VectorLayerSource import VectorLayerSource
from .raster.RasterLayerSource import RasterLayerSource


VECTOR_EXTS = {".shp", ".geojson", ".json", ".kml", ".kmz", ".gpx", ".csv", ".tab", ".las", ".laz", ".gpkg"}
RASTER_EXTS = {".tif", ".tiff", ".ecw", ".jp2", ".asc"}


class ExplorerUtils:
    """Utilitário para varredura de diretórios e carregamento de layers.

    Métodos estáticos, log com LogUtilsNew.
    """

    @staticmethod
    def _get_logger(tool_key: str):
        return LogUtils(tool=tool_key, class_name="ExplorerUtils")

    @staticmethod
    def scan_folder(folder: str, extensions: List[str], tool_key: str) -> List[Dict]:
        """Varre `folder` e retorna lista de registros de arquivos que batem nas `extensions`.

        Cada registro: {"path": str, "ext": str, "type": "vector"|"raster"}
        """
        logger = ExplorerUtils._get_logger(tool_key)
        results = []
        if not folder or not os.path.isdir(folder):
            logger.error(f"scan_folder: pasta inválida: {folder}")
            return results

        exts_set = set(e.lower() for e in extensions)

        for root, dirs, files in os.walk(folder):
            for f in files:
                p = Path(root) / f
                ext = p.suffix.lower()
                if exts_set and ext not in exts_set:
                    continue
                rec = {"path": str(p), "ext": ext}
                if ext in RASTER_EXTS:
                    rec["type"] = "raster"
                else:
                    rec["type"] = "vector"
                results.append(rec)
        logger.info(f"scan_folder: encontrados {len(results)} arquivos em {folder}")
        return results

    @staticmethod
    def create_layer(record: Dict, tool_key: str):
        """Carrega e retorna uma camada QGIS baseada no registro (usa Vector/RasterSource).

        Retorna: QgsMapLayer ou None
        """
        logger = ExplorerUtils._get_logger(tool_key)
        path = record.get("path")
        rtype = record.get("type")

        if rtype == "raster":
            layer = RasterLayerSource().load_raster_from_file(path, external_tool_key=tool_key)
            if layer:
                logger.info(f"Raster criado: {path}")
            return layer
        else:
            layer = VectorLayerSource().load_vector_layer_from_file(path, external_tool_key=tool_key)
            if layer:
                logger.info(f"Vector criado: {path}")
            return layer