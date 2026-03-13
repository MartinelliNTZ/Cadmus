class RasterLayerRendering:
    """
    Responsável pela simbologia e visualização de rasters.
    
    Escopo:
    - Definir estilos de renderização raster
    - Aplicar rampas de cor (color ramps)
    - Configurar transparência e contraste
    - Gerenciar simbologia por banda
    - Criar legendas e paletas
    
    Responsabilidade Principal:
    - Orquestrar configuração visual de rasters
    - Aplicar estilos e rampas de cor
    - Garantir coerência de visualização
    
    NÃO é Responsabilidade:
    - Processar pixels (use RasterLayerProcessing)
    - Salvar ou carregar rasters (use RasterLayerSource)
    - Calcular estatísticas (use RasterLayerMetrics)
    - Alterar dados raster (qualquer modificação)
    """

    def apply_single_band_renderer(self, raster, band_index, color_ramp_name, external_tool_key="untraceable"):
        """Aplica renderizador de banda única com rampa de cores especificada."""
        pass

    def apply_multiband_renderer(self, raster, red_band, green_band, blue_band, external_tool_key="untraceable"):
        """Aplica renderizador RGB usando três bandas especificadas."""
        pass

    def apply_paletted_renderer(self, raster, color_table, external_tool_key="untraceable"):
        """Aplica renderizador com paleta de cores discreta para classificações."""
        pass

    def set_raster_opacity(self, raster, opacity_percentage, external_tool_key="untraceable"):
        """Define a transparência/opacidade global do raster."""
        pass

    def set_band_opacity(self, raster, band_index, opacity_percentage, external_tool_key="untraceable"):
        """Define a transparência de uma banda específica."""
        pass

    def apply_color_ramp(self, raster, band_index, color_ramp_name, invert_ramp, external_tool_key="untraceable"):
        """Aplica rampa de cores a uma banda com opção de inversão."""
        pass

    def set_raster_contrast_enhancement(self, raster, enhancement_type, min_max_method, external_tool_key="untraceable"):
        """Aplica enhançamento de contraste usando método especificado."""
        pass

    def create_color_table_from_values(self, unique_values, color_list, external_tool_key="untraceable"):
        """Cria tabela de cores customizada para valores específicos."""
        pass

    def apply_hillshade_effect(self, raster, azimuth, altitude, external_tool_key="untraceable"):
        """Aplica efeito de hillshade (sombra de terreno) com parâmetros de iluminação."""
        pass

    def generate_legend_for_raster(self, raster, legend_format, external_tool_key="untraceable"):
        """Gera legenda visual baseada na simbologia atual do raster."""
        pass

    def apply_discrete_color_scheme(self, raster, band_index, num_classes, external_tool_key="untraceable"):
        """Aplica esquema de cores discreto dividindo valores em n classes."""
        pass

    def export_rendering_style_to_file(self, raster, output_style_file, external_tool_key="untraceable"):
        """Exporta configuração de renderização do raster para arquivo QML."""
        pass
