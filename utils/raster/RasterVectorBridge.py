class RasterVectorBridge:
    """
    Responsável pela integração entre rasters e vetores.
    
    Escopo:
    - Converter rasters para vetores (poligonização)
    - Converter vetores para rasters (rasterização)
    - Extrair estatísticas de raster em feições (zonal statistics)
    - Recortar raster usando geometrias vetoriais
    - Validar e sincronizar entre domínios
    
    Responsabilidade Principal:
    - Orquestrar conversões bidirecionais entre raster e vetor
    - Garantir coerência e acurácia nas conversões
    - Facilitar análises que combinam ambos os domínios
    
    NÃO é Responsabilidade:
    - Processar rasters (use RasterLayerProcessing)
    - Transformar vetores (use VectorLayerGeometry)
    - Calcular estatísticas isoladas (use RasterLayerMetrics/VectorLayerMetrics)
    - Carregar ou salvar (use RasterLayerSource/VectorLayerSource)
    """

    def rasterize_vector_layer(self, vector_layer, attribute_field, output_raster_path, pixel_size, external_tool_key="untraceable"):
        """Converte camada vetorial em raster usando atributo como valores de célula."""
        pass

    def polygonize_raster(self, raster, band_index, output_vector_path, external_tool_key="untraceable"):
        """Converte raster em camada vetorial de polígonos por valor de classe."""
        pass

    def extract_zonal_statistics(self, raster, vector_layer, statistics_type, external_tool_key="untraceable"):
        """Extrai estatísticas do raster dentro de cada feição vetorial."""
        pass

    def clip_raster_by_vector(self, raster, vector_layer, output_raster_path, external_tool_key="untraceable"):
        """Recorta raster usando geometrias da camada vetorial como máscara."""
        pass

    def sample_raster_at_points(self, raster, point_layer, output_field_name, external_tool_key="untraceable"):
        """Amostra valores do raster nos pontos da camada vetorial."""
        pass

    def calculate_raster_value_within_polygon(self, raster, polygon_geometry, aggregation_method, external_tool_key="untraceable"):
        """Calcula valor agregado do raster dentro de um polígono específico."""
        pass

    def convert_raster_to_point_cloud(self, raster, sample_density, external_tool_key="untraceable"):
        """Converte raster em camada vetorial de pontos amostrados."""
        pass

    def validate_raster_vector_alignment(self, raster, vector_layer, external_tool_key="untraceable"):
        """Verifica se raster e vetor têm CRS e alinhamento compatível."""
        pass

    def create_vector_from_raster_edges(self, raster, band_index, output_vector_path, external_tool_key="untraceable"):
        """Cria linhas vetoriais nas bordas entre valores diferentes do raster."""
        pass

    def intersect_raster_with_vector_buffer(self, raster, vector_layer, buffer_distance, external_tool_key="untraceable"):
        """Calcula estatísticas do raster no buffer ao redor de geometrias vetoriais."""
        pass

    def export_zonal_statistics_table(self, zonal_results, output_table_path, external_tool_key="untraceable"):
        """Exporta resultados de estatísticas zonais para tabela."""
        pass

    def blend_multiple_rasters_by_vector_mask(self, rasters_list, vector_mask_layer, external_tool_key="untraceable"):
        """Combina múltiplos rasters usando geometrias vetoriais como pesos."""
        pass
