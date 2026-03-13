class RasterLayerProcessing:
    """
    Responsável pelo processamento raster destrutivo e operações pixel a pixel.
    
    Escopo:
    - Aplicar operações pixel a pixel
    - Reclassificar valores raster
    - Aplicar máscaras e filtros
    - Combinar múltiplos rasters
    - Operações algébricas em bandas
    
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

    def apply_raster_algebra(self, raster1, raster2, operation, external_tool_key="untraceable"):
        """Aplica operação algébrica (+, -, *, /) entre dois rasters pixel a pixel."""
        pass

    def reclassify_raster_values(self, raster, classification_rules, external_tool_key="untraceable"):
        """Reclassifica valores do raster de acordo com regras de intervalo."""
        pass

    def apply_raster_mask(self, raster, mask_raster, external_tool_key="untraceable"):
        """Aplica uma máscara ao raster, mantendo apenas valores onde máscara é válida."""
        pass

    def apply_band_math_expression(self, raster, expression, external_tool_key="untraceable"):
        """Aplica expressão matemática customizada envolvendo múltiplas bandas."""
        pass

    def combine_rasters(self, rasters_list, combination_method, external_tool_key="untraceable"):
        """Combina múltiplos rasters usando método especificado (média, máximo, etc)."""
        pass

    def apply_focal_filter(self, raster, kernel_size, filter_type, external_tool_key="untraceable"):
        """Aplica filtro focal (média, mediana, etc) em janelas de vizinhança."""
        pass

    def normalize_raster_values(self, raster, min_value, max_value, external_tool_key="untraceable"):
        """Normaliza valores do raster para um intervalo especificado."""
        pass

    def stretch_raster_histogram(self, raster, min_percentile, max_percentile, external_tool_key="untraceable"):
        """Expande o histograma do raster cortando extremos."""
        pass

    def apply_threshold_classification(self, raster, lower_threshold, upper_threshold, external_tool_key="untraceable"):
        """Classifica raster em duas classes baseado em thresholds."""
        pass

    def invert_raster_values(self, raster, external_tool_key="untraceable"):
        """Inverte os valores do raster (valores altos viram baixos e vice-versa)."""
        pass

    def fill_raster_nodata(self, raster, fill_method, external_tool_key="untraceable"):
        """Preenche células de nodata usando método de interpolação."""
        pass

    def apply_raster_reclass_table(self, raster, reclass_table_file, external_tool_key="untraceable"):
        """Reclassifica raster usando tabela de reclassificação de um arquivo."""
        pass
