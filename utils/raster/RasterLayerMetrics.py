# -*- coding: utf-8 -*-
from typing import List, Tuple

from ..ToolKeys import ToolKey
from ...core.config.LogUtils import LogUtils


class RasterLayerMetrics:
    """
    Responsável pelas estatísticas e cálculos analíticos de rasters.

    Escopo:
    - Calcular estatísticas descritivas (min, max, média, desvio padrão)
    - Gerar histogramas
    - Calcular áreas por classe
    - Analisar distribuição de valores
    - Cálculos de correlação e índices espaciais
    - Cálculo de percentis de bandas

    Responsabilidade Principal:
    - Fornecer análises estatísticas precisas de rasters
    - Quantificar características dos dados raster
    - NÃO alterar dados

    NÃO é Responsabilidade:
    - Processar pixels (use RasterLayerProcessing)
    - Reprojetar (use RasterLayerProjection)
    - Modificar visualização (use RasterLayerRendering)
    - Carregar ou salvar (use RasterLayerSource)
    """

    # ------------------------------------------------------------------
    # Percentis de banda
    # ------------------------------------------------------------------

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="RasterLayerMetrics")

    @staticmethod
    def get_band_percentiles(
        raster_path: str,
        band_index: int = 1,
        lower_pct: float = 2.0,
        upper_pct: float = 98.0,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Tuple[float, float]:
        """
        Calcula percentis de uma banda raster usando numpy.

        Simula o corte acumulativo que o QGIS aplica por padrão,
        ignorando pixels extremos (outliers).

        Args:
            raster_path: Caminho do arquivo raster
            band_index: Índice da banda (1-indexed)
            lower_pct: Percentil inferior (ex: 2.0 = 2%)
            upper_pct: Percentil superior (ex: 98.0 = 98%)
            tool_key: Chave da ferramenta para logging

        Returns:
            Tuple (p_lower, p_upper) com os valores dos percentis

        Raises:
            ValueError: Se lower_pct >= upper_pct ou band_index < 1
            RuntimeError: Se falhar ao abrir/ler o raster
        """
        logger = RasterLayerMetrics._get_logger(tool_key)
        logger.debug(
            f"get_band_percentiles: raster={raster_path}, band={band_index}, "
            f"lower={lower_pct}%, upper={upper_pct}%"
        )

        if lower_pct >= upper_pct:
            raise ValueError(
                f"lower_pct ({lower_pct}) deve ser < upper_pct ({upper_pct})"
            )
        if band_index < 1:
            raise ValueError(f"band_index deve ser >= 1, recebido {band_index}")

        import numpy as np
        from osgeo import gdal

        ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
        if ds is None:
            raise RuntimeError(
                f"Falha ao abrir raster para calcular percentis: {raster_path}"
            )

        try:
            band = ds.GetRasterBand(band_index)
            data = band.ReadAsArray()
            if data is None or data.size == 0:
                raise RuntimeError(
                    f"Dados vazios na banda {band_index} de {raster_path}"
                )

            p_low = float(np.percentile(data, lower_pct))
            p_high = float(np.percentile(data, upper_pct))
        finally:
            ds = None

        logger.debug(
            f"get_band_percentiles: {lower_pct}%={p_low:.7f}, {upper_pct}%={p_high:.7f}"
        )
        return p_low, p_high

    # ------------------------------------------------------------------
    # Min/Max global entre múltiplos rasters/valores
    # ------------------------------------------------------------------

    @staticmethod
    def get_global_min_max(
        values: List[Tuple[float, float]],
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Tuple[float, float]:
        """
        Calcula o valor mínimo global e máximo global a partir de tuplas (min, max).

        Args:
            values: Lista de tuplas (min, max), uma por banda/raster.
                    Ex: [(0.1, 0.9), (0.2, 0.8), (0.15, 0.95)]
            tool_key: Chave da ferramenta para logging

        Returns:
            Tuple (global_min, global_max)

        Raises:
            ValueError: Se a lista estiver vazia
        """
        logger = RasterLayerMetrics._get_logger(tool_key)

        if not values:
            raise ValueError("Lista de valores vazia para calcular global min/max")

        global_min = min(v[0] for v in values)
        global_max = max(v[1] for v in values)

        logger.debug(
            f"get_global_min_max: global_min={global_min:.7f}, global_max={global_max:.7f}"
        )
        return global_min, global_max

    # ------------------------------------------------------------------
    # Extrair min/max de múltiplos rasters via percentis
    # ------------------------------------------------------------------

    @staticmethod
    def get_global_min_max_from_rasters(
        raster_band_tuples: List[Tuple[str, int]],
        lower_pct: float = 2.0,
        upper_pct: float = 98.0,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Tuple[float, float]:
        """
        Calcula min/max global a partir de múltiplos pares (raster_path, band_index).

        Útil para composições RGB onde R, G, B vêm de rasters diferentes.

        Args:
            raster_band_tuples: Lista de tuplas (raster_path, band_index)
            lower_pct: Percentil inferior
            upper_pct: Percentil superior
            tool_key: Chave da ferramenta para logging

        Returns:
            Tuple (global_min, global_max)
        """
        logger = RasterLayerMetrics._get_logger(tool_key)
        logger.debug(
            f"get_global_min_max_from_rasters: {len(raster_band_tuples)} bandas, "
            f"percentis {lower_pct}%-{upper_pct}%"
        )

        if not raster_band_tuples:
            raise ValueError("Nenhum raster informado para calcular global min/max")

        percentiles = []
        for raster_path, band_index in raster_band_tuples:
            p_low, p_high = RasterLayerMetrics.get_band_percentiles(
                raster_path, band_index, lower_pct, upper_pct, tool_key
            )
            percentiles.append((p_low, p_high))

        return RasterLayerMetrics.get_global_min_max(percentiles, tool_key)

    # ------------------------------------------------------------------
    # Métodos pré-existentes (stubs)
    # ------------------------------------------------------------------

    def get_raster_min_max_values(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula o valor mínimo e máximo de uma banda raster."""
        pass

    def calculate_raster_mean(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula a média dos valores de uma banda raster."""
        pass

    def calculate_raster_standard_deviation(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula o desvio padrão dos valores de uma banda raster."""
        pass

    def generate_raster_histogram(
        self, raster, band_index, histogram_bins, external_tool_key="untraceable"
    ):
        """Gera histograma com número de bins especificado para uma banda."""
        pass

    def calculate_area_by_class(
        self, raster, pixel_size, external_tool_key="untraceable"
    ):
        """Calcula a área ocupada por cada classe única no raster."""
        pass

    def get_unique_values_count(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Retorna a quantidade de valores únicos em uma banda."""
        pass

    def calculate_percentage_by_class(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula a percentagem de cada valor único no raster."""
        pass

    def analyze_raster_correlation(
        self, raster1, raster2, band_index, external_tool_key="untraceable"
    ):
        """Calcula correlação entre duas bandas raster (de diferentes rasters ou bandas)."""
        pass

    def calculate_nodata_percentage(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula a percentagem de células com valor nodata."""
        pass

    def get_raster_median_value(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula o valor mediano de uma banda raster."""
        pass

    def calculate_raster_variance(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Calcula a variância dos valores de uma banda raster."""
        pass

    def generate_statistical_summary(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """Gera um sumário completo de estatísticas para uma banda."""
        pass
