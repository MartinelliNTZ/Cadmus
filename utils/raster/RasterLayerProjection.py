class RasterLayerProjection:
    """
    Responsável pelo CRS, resolução, alinhamento e extent de rasters.
    
    Escopo:
    - Gerenciar sistemas de referência de coordenadas de rasters
    - Reprojetar rasters entre CRS diferentes
    - Ajustar resolução e tamanho de pixel
    - Alinhar rasters a uma grade ou extent
    - Gerenciar transformações espaciais
    
    Responsabilidade Principal:
    - Orquestrar operações de reprojeção e ajuste espacial
    - Garantir consistência espacial entre rasters
    - Validar e ajustar parâmetros de resolução
    
    NÃO é Responsabilidade:
    - Alterar valores de pixels (use RasterLayerProcessing)
    - Calcular estatísticas (use RasterLayerMetrics)
    - Carregar ou salvar (use RasterLayerSource)
    - Modificar visualização (use RasterLayerRendering)
    """

    def get_raster_crs(self, raster, external_tool_key="untraceable"):
        """Obtém o CRS atual do raster."""
        pass

    def set_raster_crs(self, raster, target_crs, external_tool_key="untraceable"):
        """Define o CRS do raster sem reprojetar (apenas muda a definição)."""
        pass

    def reproject_raster_to_crs(self, raster, target_crs, resampling_method, external_tool_key="untraceable"):
        """Reprojeta o raster para um CRS diferente usando método de reamostragem."""
        pass

    def get_raster_resolution(self, raster, external_tool_key="untraceable"):
        """Obtém a resolução do raster (tamanho do pixel em X e Y)."""
        pass

    def set_raster_resolution(self, raster, new_resolution_x, new_resolution_y, external_tool_key="untraceable"):
        """Altera a resolução do raster reamostrando os pixels."""
        pass

    def get_raster_extent(self, raster, external_tool_key="untraceable"):
        """Obtém a extensão geográfica do raster (bounds)."""
        pass

    def align_raster_to_grid(self, raster, grid_origin_x, grid_origin_y, grid_size, external_tool_key="untraceable"):
        """Alinha o raster a uma grade regular com origem e tamanho de célula especificados."""
        pass

    def align_raster_to_reference(self, raster, reference_raster, external_tool_key="untraceable"):
        """Alinha o raster para ter mesma resolução, extent e CRS de um raster referência."""
        pass

    def get_raster_geotransform(self, raster, external_tool_key="untraceable"):
        """Obtém a transformação geográfica (georeferenciamento) do raster."""
        pass

    def set_raster_geotransform(self, raster, geotransform, external_tool_key="untraceable"):
        """Define a transformação geográfica do raster."""
        pass

    def validate_raster_alignment(self, raster1, raster2, external_tool_key="untraceable"):
        """Verifica se dois rasters estão alinhados (mesma resolução, origem, extent)."""
        pass

    def convert_pixel_to_geographic_coordinates(self, raster, pixel_x, pixel_y, external_tool_key="untraceable"):
        """Converte coordenadas de pixel para coordenadas geográficas."""
        pass
