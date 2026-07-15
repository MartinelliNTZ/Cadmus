# -*- coding: utf-8 -*-
import os
import tempfile

from typing import List, Optional

from ..ToolKeys import ToolKey
from ...core.config.LogUtils import LogUtils


class RasterLayerProcessing:
    """
    Responsável pelo processamento raster destrutivo e operações pixel a pixel.

    Escopo:
    - Aplicar operações pixel a pixel
    - Reclassificar valores raster
    - Aplicar máscaras e filtros
    - Combinar múltiplos rasters
    - Operações algébricas em bandas
    - Extração de bandas
    - Criação de máscaras alpha

    Responsabilidade Principal:
    - Orquestrar processamento que ALTERA valores de pixels
    - Garantir coerência de resultados
    - Manter integridade estrutural do raster

    NÃO é Responsabilidade:
    - Reprojetar (use RasterLayerProjection)
    - Calcular estatísticas (use RasterLayerMetrics)
    - Alterar visualização (use RasterLayerRendering)
    - Carregar ou salvar (use RasterLayerSource)
    """

    # ------------------------------------------------------------------
    # Extração de bandas
    # ------------------------------------------------------------------

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="RasterLayerProcessing")

    @staticmethod
    def extract_band(
        raster_path: str,
        band_num: int,
        output_path: Optional[str] = None,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> str:
        """
        Extrai uma banda específica de um raster para um arquivo GeoTIFF.

        Args:
            raster_path: Caminho do raster de origem
            band_num: Número da banda a extrair (1-indexed)
            output_path: Caminho de saída. Se None, cria em tempdir.
            tool_key: Chave da ferramenta para logging

        Returns:
            Caminho do arquivo GeoTIFF com a banda extraída

        Raises:
            ValueError: Se raster_path for inválido ou band_num < 1
            RuntimeError: Se falhar ao abrir/extrair com GDAL
        """
        logger = RasterLayerProcessing._get_logger(tool_key)
        logger.debug(
            f"extract_band: inicio raster={raster_path}, band={band_num}"
        )

        if not raster_path:
            raise ValueError("raster_path nao pode ser vazio")
        if band_num < 1:
            raise ValueError(f"band_num deve ser >= 1, recebido {band_num}")

        from osgeo import gdal

        if output_path is None:
            temp_dir = tempfile.mkdtemp(prefix="cadmus_band_")
            output_path = os.path.join(temp_dir, f"band_{band_num}.tif")

        src_ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
        if src_ds is None:
            raise RuntimeError(
                f"Nao foi possivel abrir o raster: {raster_path}"
            )

        try:
            gdal.Translate(output_path, src_ds, format="GTiff", bandList=[band_num])
        except Exception as e:
            raise RuntimeError(
                f"Falha ao extrair banda {band_num} de {raster_path}: {e}"
            )
        finally:
            src_ds = None

        logger.debug(f"extract_band: concluido -> {output_path}")
        return output_path

    # ------------------------------------------------------------------
    # Criação de máscara alpha
    # ------------------------------------------------------------------

    @staticmethod
    def create_alpha_mask(
        raster_path: str,
        nodata_value: float,
        output_path: Optional[str] = None,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> str:
        """
        Cria uma máscara alpha (byte: 0/255) a partir de um valor NoData.

        Pixels com valor == nodata_value viram 0 (transparente).
        Demais pixels viram 255 (opaco).

        Args:
            raster_path: Caminho do raster de referência (banda 1)
            nodata_value: Valor considerado NoData
            output_path: Caminho do GeoTIFF alpha. Se None, cria em tempdir.
            tool_key: Chave da ferramenta para logging

        Returns:
            Caminho do arquivo GeoTIFF com 1 banda Byte (0/255)

        Raises:
            RuntimeError: Se falhar ao abrir/criar/escrever
        """
        logger = RasterLayerProcessing._get_logger(tool_key)
        logger.debug(
            f"create_alpha_mask: raster={raster_path}, nodata={nodata_value}"
        )

        import numpy as np
        from osgeo import gdal

        if output_path is None:
            temp_dir = tempfile.mkdtemp(prefix="cadmus_alpha_")
            output_path = os.path.join(temp_dir, "alpha.tif")

        ds_ref = gdal.Open(raster_path, gdal.GA_ReadOnly)
        if ds_ref is None:
            raise RuntimeError(
                f"Nao foi possivel abrir raster para criar alpha: {raster_path}"
            )

        try:
            driver = gdal.GetDriverByName("GTiff")
            ds_alpha = driver.Create(
                output_path,
                ds_ref.RasterXSize,
                ds_ref.RasterYSize,
                1,
                gdal.GDT_Byte,
            )
            ds_alpha.SetGeoTransform(ds_ref.GetGeoTransform())
            ds_alpha.SetProjection(ds_ref.GetProjection())

            band_data = ds_ref.GetRasterBand(1).ReadAsArray()
            nodata_mask = np.isclose(band_data, nodata_value, atol=1e-6)
            alpha_data = np.where(nodata_mask, 0, 255).astype(np.uint8)

            ds_alpha.GetRasterBand(1).WriteArray(alpha_data)
            ds_alpha.FlushCache()
        except Exception as e:
            raise RuntimeError(
                f"Falha ao criar mascara alpha para {raster_path}: {e}"
            )
        finally:
            ds_alpha = None
            ds_ref = None

        logger.debug(f"create_alpha_mask: concluido -> {output_path}")
        return output_path

    # ------------------------------------------------------------------
    # Composição de raster multibanda (VRT + Translate)
    # ------------------------------------------------------------------

    @staticmethod
    def compose_multiband_raster(
        band_files: List[str],
        output_path: str,
        create_alpha: bool = False,
        alpha_band_path: Optional[str] = None,
        creation_options: Optional[List[str]] = None,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> str:
        """
        Compõe múltiplos arquivos GeoTIFF de banda única em um raster multibanda.

        Usa GDAL BuildVRT (separate) + Translate para gerar GeoTIFF.

        Args:
            band_files: Lista de caminhos de arquivos .tif de banda única
            output_path: Caminho do GeoTIFF de saída
            create_alpha: Se True, adiciona banda alpha ao final (deve vir de alpha_band_path)
            alpha_band_path: Caminho do GeoTIFF de máscara alpha (ignorado se create_alpha=False)
            creation_options: Opções de criação GDAL (ex: ["COMPRESS=LZW"])
            tool_key: Chave da ferramenta para logging

        Returns:
            output_path (mesmo do parâmetro)

        Raises:
            ValueError: Se band_files estiver vazio
            RuntimeError: Se falhar ao compor
        """
        logger = RasterLayerProcessing._get_logger(tool_key)
        logger.debug(
            f"compose_multiband_raster: {len(band_files)} bandas, "
            f"alpha={create_alpha}, output={output_path}"
        )

        if not band_files:
            raise ValueError("Nenhum arquivo de banda informado para composicao")

        from osgeo import gdal

        if creation_options is None:
            creation_options = ["COMPRESS=LZW", "BIGTIFF=IF_NEEDED", "TILED=YES"]

        temp_dir = tempfile.mkdtemp(prefix="cadmus_vrt_")
        vrt_path = os.path.join(temp_dir, "composite.vrt")

        all_bands = list(band_files)
        num_bands = len(all_bands)

        if create_alpha and alpha_band_path:
            all_bands.append(alpha_band_path)
            num_bands += 1

        vrt_options = gdal.BuildVRTOptions(separate=True)
        ds_vrt = gdal.BuildVRT(vrt_path, all_bands, options=vrt_options)
        if ds_vrt is None:
            raise RuntimeError("Falha ao criar VRT do mosaico RGB.")
        ds_vrt = None

        translate_options = gdal.TranslateOptions(
            format="GTiff",
            bandList=list(range(1, num_bands + 1)),
            creationOptions=creation_options,
        )
        gdal.Translate(output_path, vrt_path, options=translate_options)

        logger.debug(f"compose_multiband_raster: concluido -> {output_path}")
        return output_path

    # ------------------------------------------------------------------
    # Métodos pré-existentes (stubs)
    # ------------------------------------------------------------------

    def apply_raster_algebra(
        self, raster1, raster2, operation, external_tool_key="untraceable"
    ):
        """Aplica operação algébrica (+, -, *, /) entre dois rasters pixel a pixel."""
        pass

    def reclassify_raster_values(
        self, raster, classification_rules, external_tool_key="untraceable"
    ):
        """Reclassifica valores do raster de acordo com regras de intervalo."""
        pass

    def apply_raster_mask(self, raster, mask_raster, external_tool_key="untraceable"):
        """Aplica uma máscara ao raster, mantendo apenas valores onde máscara é válida."""
        pass

    def apply_band_math_expression(
        self, raster, expression, external_tool_key="untraceable"
    ):
        """Aplica expressão matemática customizada envolvendo múltiplas bandas."""
        pass

    def combine_rasters(
        self, rasters_list, combination_method, external_tool_key="untraceable"
    ):
        """Combina múltiplos rasters usando método especificado (média, máximo, etc)."""
        pass

    def apply_focal_filter(
        self, raster, kernel_size, filter_type, external_tool_key="untraceable"
    ):
        """Aplica filtro focal (média, mediana, etc) em janelas de vizinhança."""
        pass

    def normalize_raster_values(
        self, raster, min_value, max_value, external_tool_key="untraceable"
    ):
        """Normaliza valores do raster para um intervalo especificado."""
        pass

    def stretch_raster_histogram(
        self, raster, min_percentile, max_percentile, external_tool_key="untraceable"
    ):
        """Expande o histograma do raster cortando extremos."""
        pass

    def apply_threshold_classification(
        self, raster, lower_threshold, upper_threshold, external_tool_key="untraceable"
    ):
        """Classifica raster em duas classes baseado em thresholds."""
        pass

    def invert_raster_values(self, raster, external_tool_key="untraceable"):
        """Inverte os valores do raster (valores altos viram baixos e vice-versa)."""
        pass

    def fill_raster_nodata(self, raster, fill_method, external_tool_key="untraceable"):
        """Preenche células de nodata usando método de interpolação."""
        pass

    def apply_raster_reclass_table(
        self, raster, reclass_table_file, external_tool_key="untraceable"
    ):
        """Reclassifica raster usando tabela de reclassificação de um arquivo."""
        pass
