class HtmlInstructions:
    def __init__(self, provider):
        self.provider = provider

    def get_raster_difference_statistics_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para cálculo de diferença entre múltiplos rasters, com geração automática de estatísticas e relatório consolidado em HTML.
            {self.provider.transform_h('Objetivo')}
            Calcular diferenças entre todos os pares possíveis de rasters.
            Identificar variações entre superfícies.
            Gerar estatísticas automáticas para cada comparação.
            Consolidar resultados em relatório único.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Informe uma pasta com rasters ou selecione rasters já carregados no QGIS.
            3. Defina a saída, se quiser.
            4. Execute.
            {self.provider.transform_h('Saídas')}
            DIF_rasterA_rasterB.tif
            DIF_rasterA_rasterB_stats.html
            raster_difference_stats_summary.html
            {self.provider.transform_h('Atenções')}
            O número de combinações cresce rapidamente.
            Pode gerar muitos arquivos.
            Diferenças usam apenas a banda 1.
            {self.provider.author_info}
        """

    def get_difference_fields_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para gerar campos de diferença entre um campo base e outros campos numéricos da camada.
            {self.provider.transform_h('Objetivo')}
            Calcular a diferença entre vários atributos numéricos usando um campo base como referência.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Selecione a camada de pontos.
            3. Defina o campo base.
            4. Escolha os campos a excluir, se necessário.
            5. Configure prefixo e precisão.
            6. Execute.
            {self.provider.transform_h('Saídas')}
            Novos campos com o prefixo definido.
            {self.provider.transform_h('Atenções')}
            Campos não numéricos são ignorados.
            Valores nulos geram saída nula.
            {self.provider.author_info}
        """

    def get_raster_mass_clipper_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para recorte em lote de rasters usando uma camada poligonal como máscara.
            {self.provider.transform_h('Objetivo')}
            Recortar múltiplos rasters em uma única execução.
            Permitir recorte por camada inteira ou por feição.
            Aplicar correção automática de borda.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Defina a máscara poligonal.
            3. Selecione os rasters.
            4. Configure o modo e a pasta de saída.
            5. Execute.
            {self.provider.transform_h('Saídas')}
            raster_clip.tif
            raster_feat_1.tif
            {self.provider.transform_h('Atenções')}
            O modo por feição pode gerar muitos arquivos.
            O buffer amplia levemente a área recortada.
            {self.provider.author_info}
        """

    def get_geometry_difference_line_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para criação de linhas entre pontos com cálculo de distância.
            {self.provider.transform_h('Objetivo')}
            Gerar linhas conectando pontos relacionados.
            Calcular distância entre pares.
            Suportar comparação entre uma ou duas camadas.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Selecione a camada A.
            3. Ative a segunda camada se necessário.
            4. Defina os campos de agrupamento.
            5. Execute.
            {self.provider.transform_h('Saídas')}
            Camada de linhas com group_key, feature_a, feature_b e distance.
            {self.provider.transform_h('Atenções')}
            O modo 2 exige camada B e campo correspondente.
            Geometrias vazias são ignoradas.
            {self.provider.author_info}
        """

    def get_grid_generator_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para gerar uma grade de pontos, linhas ou polígonos dentro de uma área poligonal.
            {self.provider.transform_h('Objetivo')}
            Gerar uma grade regular usando a extensão de uma camada de entrada.
            Extrair a grade somente onde ela intersecta a camada de entrada.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Selecione a camada de entrada de polígonos.
            3. Defina o espaçamento horizontal e vertical.
            4. Selecione o tipo de grade.
            5. Ative o log detalhado se desejar acompanhar a execução.
            6. Execute.
            {self.provider.transform_h('Saídas')}
            Camada de grade com geometria de ponto, linha ou polígono.
            {self.provider.transform_h('Atenções')}
            O espaçamento define a densidade da grade.
            Se a camada de entrada tiver geometrias inválidas, a extração pode produzir uma grade menor.
            {self.provider.author_info}
        """

    def get_raster_mass_sampler_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para amostragem massiva de múltiplos rasters em pontos.
            {self.provider.transform_h('Objetivo')}
            Extrair valores de vários rasters em pontos.
            Gerar nova camada com valores amostrados.
            {self.provider.transform_alert('O nome do raster deve ser claro e único, pois será usado para nomear os campos de saída.')}
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Selecione os pontos.
            3. Selecione os rasters.
            4. Defina CRS de saída, se necessário.
            5. Execute.
            {self.provider.transform_h('Saídas')}
            Nova camada de pontos com atributos adicionais de cada raster.
            {self.provider.transform_h('Atenções')}
            Valores fora da extensão retornam nulo.
            Diferenças de CRS podem impactar a precisão.
            {self.provider.author_info}
        """

    def get_raster_optimizer_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para criar ou reconstruir pirâmides (overviews) em rasters TIFF, otimizando a visualização e o desempenho em grandes mosaicos.
            {self.provider.transform_h('Objetivo')}
            Criar overviews (gdaladdo) em lote para acelerar o carregamento de rasters.
            Suportar seleção por pasta ou camadas existentes no projeto.
            Oferecer compressão LZW, DEFLATE ou ZSTD com controle de predictor e zlevel.
            {self.provider.transform_h('Como usar')}
            1. Selecione camadas raster do projeto OU informe uma pasta com rasters TIFF.
            2. Ative "Incluir subpastas" se a pasta tiver subdiretórios.
            3. Escolha os níveis de overview desejados (2, 4, 8, 16, 32, 64, 128, 256).
            4. Configure o método de reamostragem (average, nearest, cubic, etc).
            5. Escolha a compressão (LZW, DEFLATE ou ZSTD) e ajuste predictor/zlevel.
            6. Marque "Deletar overviews existentes" se quiser recriar do zero.
            7. Execute.
            {self.provider.transform_h('Saídas')}
            Os próprios rasters de entrada são modificados in-place com as novas overviews.
            {self.provider.transform_h('Atenções')}
            A operação modifica os arquivos TIFF originais (in-place).
            O processo usa gdaladdo, que deve estar disponível no PATH do sistema.
            Níveis muito altos para rasters pequenos podem ser ignorados pelo GDAL.
            {self.provider.author_info}
        """

    def get_ndvi_calculator_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para calculo do NDVI (Normalized Difference Vegetation Index) a partir de dois rasters (NIR e RED).
            {self.provider.transform_h('Objetivo')}
            Calcular o indice de vegetacao NDVI entre dois rasters.
            Suportar selecao individual de bandas NIR e RED.
            Informar automaticamente as bandas recomendadas por satelite.
            {self.provider.transform_alert('As bandas padrao sao definidas como banda 1. Ajuste conforme o satelite de origem dos dados.')}
            {self.provider.transform_h('Bandas Recomendadas')}
            Sentinel-2: Banda 8 (NIR) e Banda 4 (Red)
            Landsat 8/9:  Banda 5 (NIR) e Banda 4 (Red)
            Landsat 5/7:  Banda 4 (NIR) e Banda 3 (Red)
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta no Processing Toolbox (Cadmus > Raster).
            2. Selecione o raster NIR (Infravermelho Proximo).
            3. Selecione a banda NIR (padrao: banda 1).
            4. Selecione o raster RED (Vermelho).
            5. Selecione a banda RED (padrao: banda 1).
            6. Defina o caminho de saida para o raster NDVI.
            7. Execute.
            {self.provider.transform_h('Interpretacao dos Valores')}
            -1.0 a 0.0 : Agua, superficies nao vegetadas
             0.0 a 0.2 : Solo exposto, vegetacao esparsa
             0.2 a 0.5 : Vegetacao moderada
             0.5 a 1.0 : Vegetacao densa e saudavel
            {self.provider.transform_h('Saidas')}
            Raster NDVI (GeoTIFF) com valores entre -1 e 1.
            {self.provider.transform_h('Atencoes')}
            Os rasters NIR e RED precisam ter extensoes sobrepostas.
            Se as extensoes nao se sobrepuserem, o NDVI resultante pode ser nulo.
            Ambos os rasters devem estar no mesmo CRS para resultados precisos.
            {self.provider.author_info}
        """

    def get_rgb_mosaic_creator_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para criar um mosaico RGB a partir de 3 rasters individuais (bandas R, G, B), com opcao de criar banda alpha para valores NoData.
            {self.provider.transform_h('Objetivo')}
            Combinar 3 rasters de banda unica em um mosaico RGB de 3 ou 4 bandas.
            Suportar selecao individual de banda para cada canal (R, G, B).
            Criar banda alpha (transparencia) para valores NoData especificos.
            {self.provider.transform_alert('As bandas padrao sao definidas como banda 1. Ajuste conforme o numero da banda real nos rasters de entrada.')}
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta no Processing Toolbox (Cadmus > Raster).
            2. Selecione o raster da banda Vermelha (R) e informe o numero da banda.
            3. Selecione o raster da banda Verde (G) e informe o numero da banda.
            4. Selecione o raster da banda Azul (B) e informe o numero da banda.
            5. Ative "Criar banda alpha para NoData" se desejar transparencia nos pixeis nulos.
            6. Defina o valor NoData (ex: 0 ou -9999) que sera tratado como transparente.
            7. Defina o caminho de saida e execute.
            {self.provider.transform_h('Banda Alpha')}
            Quando ativada, uma 4a banda (alpha) e adicionada ao mosaico.
            Pixeiis com o valor NoData especificado recebem alpha = 0 (transparente).
            Demais pixeis recebem alpha = 255 (opaco).
            A banda alpha usa o raster da banda R como referencia espacial.
            {self.provider.transform_h('Saidas')}
            Raster GeoTIFF com 3 bandas (RGB) ou 4 bandas (RGBA) se alpha ativado.
            Compressao LZW, TILED=YES.
            {self.provider.transform_h('Atencoes')}
            Os 3 rasters de entrada precisam ter a mesma extensao e resolucao.
            Se as extensoes divergirem, o mosaico usara a extensao da banda R como referencia.
            A banda alpha e opcional e controlada por checkbox salva em preferencias.
            {self.provider.author_info}
        """

    def get_rgb_style_standardizer_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para padronizar o estilo de visualizacao de um raster RGB (multibanda) usando percentis.
            {self.provider.transform_h('Objetivo')}
            Calcular percentis 2%-98% de cada banda de um raster RGB.
            Gerar um estilo QML com contraste esticado (StretchToMinimumMaximum).
            Salvar o estilo como sidecar (arquivo .qml) e aplicar DIRETAMENTE na camada de entrada.
            Nao gera um novo raster, apenas ajusta o estilo da camada atual.
            Esta ferramenta equivale as fases 6.1 e 6.2 do Criador de Mosaico RGB, mas como algoritmo independente.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta no Processing Toolbox (Cadmus > Raster).
            2. Selecione o raster RGB multibanda de entrada (ja carregado no projeto).
            3. Configure os indices das bandas R (padrao: 1), G (padrao: 2), B (padrao: 3).
            4. Se houver banda alpha, informe o indice (ex: 4). Senao, deixe -1.
            5. Ajuste os percentis inferior (padrao: 2%) e superior (padrao: 98%) se desejar.
            6. Execute.
            {self.provider.transform_h('Saidas')}
            Arquivo QML sidecar salvo ao lado do raster original.
            Backup do QML em temp/styles.
            Estilo aplicado diretamente na camada de entrada no projeto.
            {self.provider.transform_h('Atencoes')}
            O raster de entrada precisa ser multibanda (pelo menos 3 bandas).
            Nao gera um novo raster - o estilo e aplicado na camada existente.
            Os percentis sao calculados sobre o raster original.
            Se a banda alpha for definida como -1, nenhuma banda alpha sera configurada no QML.
            {self.provider.author_info}
        """

    def get_attribute_statistics_help(self):
        return f"""
            {self.provider.logo}
            Ferramenta do pacote Cadmus para calcular estatísticas descritivas de atributos numéricos e exportar CSV.
            {self.provider.transform_h('Objetivo')}
            Calcular média, mediana, desvio padrão, percentis e outras estatísticas.
            Exportar resultados para CSV.
            {self.provider.transform_h('Como usar')}
            1. Abra a ferramenta.
            2. Selecione a camada de entrada.
            3. Defina campos a excluir, se necessário.
            4. Ajuste a precisão decimal.
            5. Escolha as estatísticas desejadas.
            6. Configure a saída e execute.
            {self.provider.transform_h('Saídas')}
            Arquivo CSV com uma linha por campo analisado.
            {self.provider.transform_h('Atenções')}
            Apenas campos numéricos são considerados.
            Valores nulos são ignorados.
            {self.provider.author_info}
        """
