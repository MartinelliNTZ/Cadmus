# -*- coding: utf-8 -*-
import os
import tempfile

import processing
from qgis.core import QgsCoordinateReferenceSystem, QgsRasterLayer

from ...core.enum.ResamplingMethod import ResamplingMethod
from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey


class RasterLayerProjection:
    """
    Responsavel pelo CRS, resolucao, alinhamento e extent de rasters.

    Escopo:
    - Gerenciar sistemas de referencia de coordenadas de rasters
    - Reprojetar rasters entre CRS diferentes
    - Ajustar resolucao e tamanho de pixel
    - Alinhar rasters a uma grade ou extent
    - Gerenciar transformacoes espaciais

    Responsabilidade Principal:
    - Orquestrar operacoes de reprojecao e ajuste espacial
    - Garantir consistencia espacial entre rasters
    - Validar e ajustar parametros de resolucao

    NAO e Responsabilidade:
    - Alterar valores de pixels (use RasterLayerProcessing)
    - Calcular estatisticas (use RasterLayerMetrics)
    - Carregar ou salvar (use RasterLayerSource)
    - Modificar visualizacao (use RasterLayerRendering)
    """

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        """Helper para obter logger com tool_key especifico."""
        return LogUtils(tool=tool_key, class_name="RasterLayerProjection")

    @staticmethod
    def _normalize_crs(crs_value):
        if crs_value in (None, ""):
            return None

        if isinstance(crs_value, QgsCoordinateReferenceSystem):
            return crs_value if crs_value.isValid() else None

        normalized = QgsCoordinateReferenceSystem(str(crs_value))
        if normalized.isValid():
            return normalized

        normalized = QgsCoordinateReferenceSystem()
        normalized.createFromUserInput(str(crs_value))
        return normalized if normalized.isValid() else None

    @staticmethod
    def get_raster_crs(raster, external_tool_key=ToolKey.UNTRACEABLE):
        """Obtem o CRS atual do raster."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"get_raster_crs(raster={raster})")
        if raster is None:
            logger.warning("get_raster_crs: raster nao informado")
            return None

        if isinstance(raster, QgsRasterLayer):
            crs = raster.crs()
            if crs and crs.isValid():
                logger.info(f"get_raster_crs: CRS obtido do QgsRasterLayer: {crs.authid()}")
                return crs
            logger.warning("get_raster_crs: QgsRasterLayer sem CRS valido")
            return None

        if isinstance(raster, str):
            if not os.path.exists(raster):
                logger.warning(f"get_raster_crs: raster nao encontrado: {raster}")
                return None
            raster_layer = QgsRasterLayer(raster, os.path.basename(raster))
            if raster_layer.isValid() and raster_layer.crs().isValid():
                logger.info(
                    f"get_raster_crs: CRS obtido do caminho raster: {raster_layer.crs().authid()}"
                )
                return raster_layer.crs()
            logger.warning("get_raster_crs: falha ao carregar raster ou CRS invalido")
            return None

        logger.warning(f"get_raster_crs: tipo nao suportado: {type(raster).__name__}")
        return None

    def set_raster_crs(self, raster, target_crs, external_tool_key=ToolKey.UNTRACEABLE):
        """Define o CRS do raster sem reprojetar (apenas muda a definicao)."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"set_raster_crs(raster={raster}, target_crs={target_crs})")
        pass

    @staticmethod
    def reproject_raster_to_crs(
        raster_path,
        target_crs,
        resampling_method=ResamplingMethod.CUBICO_SUAVIZADO,
        external_tool_key=ToolKey.UNTRACEABLE,
        nodata_value=None,
        output_data_type=0,
        target_resolution=None,
        output_path=None,
        source_crs=None,
        target_extent=None,
        target_extent_crs=None,
        multithreading=False,
        creation_options="",
        extra="",
        context=None,
        feedback=None,
        is_child_algorithm=False,
    ):
        """Reprojeta ou reamostra raster via `gdal:warpreproject`.

        Defaults:
        - `nodata_value=None`
        - `output_data_type=0` para usar o tipo do raster de entrada
        - `target_resolution=None` para nao reamostrar
        - `resampling_method=ResamplingMethod.CUBICO_SUAVIZADO`
        - `multithreading=False`
        """
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(
            "reproject_raster_to_crs("
            f"raster_path={raster_path}, "
            f"target_crs={target_crs}, "
            f"resampling_method={resampling_method}, "
            f"nodata_value={nodata_value}, "
            f"output_data_type={output_data_type}, "
            f"target_resolution={target_resolution}, "
            f"output_path={output_path}, "
            f"source_crs={source_crs}, "
            f"target_extent={target_extent}, "
            f"target_extent_crs={target_extent_crs}, "
            f"multithreading={multithreading}, "
            f"creation_options={creation_options}, "
            f"extra={extra})"
        )

        if not raster_path or not os.path.exists(raster_path):
            logger.critical(f"Raster nao encontrado para reprojecao: {raster_path}")
            raise ValueError("raster_path invalido ou inexistente")

        raster_layer = QgsRasterLayer(raster_path, os.path.basename(raster_path))
        if not raster_layer or not raster_layer.isValid():
            logger.critical(f"Falha ao carregar raster para reprojecao: {raster_path}")
            raise ValueError("Falha ao carregar raster de entrada")

        resolved_source_crs = RasterLayerProjection._normalize_crs(source_crs)
        resolved_target_crs = RasterLayerProjection._normalize_crs(target_crs)
        resolved_target_extent_crs = RasterLayerProjection._normalize_crs(target_extent_crs)

        if resolved_target_crs is None and raster_layer.crs().isValid():
            resolved_target_crs = raster_layer.crs()

        if output_path is None:
            temp_dir = tempfile.mkdtemp(prefix="cadmus_reproject_")
            output_path = os.path.join(temp_dir, "OUTPUT.tif")

        should_resample = target_resolution not in (None, 0, 0.0, "0", "0.0", "")

        resolved_resampling_method = resampling_method
        if resolved_resampling_method is None:
            resolved_resampling_method = ResamplingMethod.CUBICO_SUAVIZADO

        if isinstance(resolved_resampling_method, ResamplingMethod):
            resolved_resampling_value = resolved_resampling_method.value
        else:
            resolved_resampling_value = int(resolved_resampling_method)

        params = {
            "INPUT": raster_path,
            "SOURCE_CRS": resolved_source_crs,
            "TARGET_CRS": resolved_target_crs,
            "TARGET_EXTENT": target_extent,
            "TARGET_EXTENT_CRS": resolved_target_extent_crs,
            "NODATA": nodata_value,
            "OPTIONS": creation_options or "",
            "DATA_TYPE": 0 if output_data_type in (None, "") else output_data_type,
            "MULTITHREADING": multithreading,
            "EXTRA": extra or "",
            "OUTPUT": output_path,
        }

        if should_resample:
            params["TARGET_RESOLUTION"] = target_resolution
            params["RESAMPLING"] = resolved_resampling_value
            logger.debug(
                f"Reamostragem habilitada com target_resolution={target_resolution} e resampling_method={resolved_resampling_method}"
            )
        else:
            params["TARGET_RESOLUTION"] = None
            logger.debug(
                "Reamostragem desabilitada porque target_resolution e None ou 0"
            )

        logger.info(
            f"Executando gdal:warpreproject | input={raster_path} | output={output_path}"
        )
        result = processing.run(
            "gdal:warpreproject",
            params,
            context=context,
            feedback=feedback,
            is_child_algorithm=is_child_algorithm,
        )
        output = result.get("OUTPUT")

        if not output or not os.path.exists(output):
            logger.critical("Falha na reprojecao raster: saida nao foi gerada")
            raise RuntimeError("Falha ao reprojetar raster")

        logger.info(f"Raster reprojetado com sucesso: {output}")
        return output

    def get_raster_resolution(self, raster, external_tool_key=ToolKey.UNTRACEABLE):
        """Obtem a resolucao do raster (tamanho do pixel em X e Y)."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"get_raster_resolution(raster={raster})")
        pass

    def set_raster_resolution(
        self,
        raster,
        new_resolution_x,
        new_resolution_y,
        external_tool_key=ToolKey.UNTRACEABLE,
    ):
        """Altera a resolucao do raster reamostrando os pixels."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(
            f"set_raster_resolution(raster={raster}, new_resolution_x={new_resolution_x}, new_resolution_y={new_resolution_y})"
        )
        pass

    def get_raster_extent(self, raster, external_tool_key=ToolKey.UNTRACEABLE):
        """Obtem a extensao geografica do raster (bounds)."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"get_raster_extent(raster={raster})")
        pass

    def align_raster_to_grid(
        self,
        raster,
        grid_origin_x,
        grid_origin_y,
        grid_size,
        external_tool_key=ToolKey.UNTRACEABLE,
    ):
        """Alinha o raster a uma grade regular com origem e tamanho de celula especificados."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(
            f"align_raster_to_grid(raster={raster}, grid_origin_x={grid_origin_x}, grid_origin_y={grid_origin_y}, grid_size={grid_size})"
        )
        pass

    def align_raster_to_reference(
        self, raster, reference_raster, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Alinha o raster para ter mesma resolucao, extent e CRS de um raster referencia."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(
            f"align_raster_to_reference(raster={raster}, reference_raster={reference_raster})"
        )
        pass

    def get_raster_geotransform(self, raster, external_tool_key=ToolKey.UNTRACEABLE):
        """Obtem a transformacao geografica (georeferenciamento) do raster."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"get_raster_geotransform(raster={raster})")
        pass

    def set_raster_geotransform(
        self, raster, geotransform, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Define a transformacao geografica do raster."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"set_raster_geotransform(raster={raster}, geotransform={geotransform})")
        pass

    def validate_raster_alignment(
        self, raster1, raster2, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Verifica se dois rasters estao alinhados (mesma resolucao, origem, extent)."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(f"validate_raster_alignment(raster1={raster1}, raster2={raster2})")
        pass

    def convert_pixel_to_geographic_coordinates(
        self, raster, pixel_x, pixel_y, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Converte coordenadas de pixel para coordenadas geograficas."""
        logger = RasterLayerProjection._get_logger(external_tool_key)
        logger.debug(
            f"convert_pixel_to_geographic_coordinates(raster={raster}, pixel_x={pixel_x}, pixel_y={pixel_y})"
        )
        pass
