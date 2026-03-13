class RasterLayerMetrics:
    """
    Responsável pelas estatísticas e cálculos analíticos de rasters.
    
    Escopo:
    - Calcular estatísticas descritivas (min, max, média, desvio padrão)
    - Gerar histogramas
    - Calcular áreas por classe
    - Analisar distribuição de valores
    - Cálculos de correlação e índices espaciais
    
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

    def get_raster_min_max_values(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula o valor mínimo e máximo de uma banda raster."""
        pass

    def calculate_raster_mean(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula a média dos valores de uma banda raster."""
        pass

    def calculate_raster_standard_deviation(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula o desvio padrão dos valores de uma banda raster."""
        pass

    def generate_raster_histogram(self, raster, band_index, histogram_bins, external_tool_key="untraceable"):
        """Gera histograma com número de bins especificado para uma banda."""
        pass

    def calculate_area_by_class(self, raster, pixel_size, external_tool_key="untraceable"):
        """Calcula a área ocupada por cada classe única no raster."""
        pass

    def get_unique_values_count(self, raster, band_index, external_tool_key="untraceable"):
        """Retorna a quantidade de valores únicos em uma banda."""
        pass

    def calculate_percentage_by_class(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula a percentagem de cada valor único no raster."""
        pass

    def analyze_raster_correlation(self, raster1, raster2, band_index, external_tool_key="untraceable"):
        """Calcula correlação entre duas bandas raster (de diferentes rasters ou bandas)."""
        pass

    def calculate_nodata_percentage(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula a percentagem de células com valor nodata."""
        pass

    def get_raster_median_value(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula o valor mediano de uma banda raster."""
        pass

    def calculate_raster_variance(self, raster, band_index, external_tool_key="untraceable"):
        """Calcula a variância dos valores de uma banda raster."""
        pass

    def generate_statistical_summary(self, raster, band_index, external_tool_key="untraceable"):
        """Gera um sumário completo de estatísticas para uma banda."""
        pass
