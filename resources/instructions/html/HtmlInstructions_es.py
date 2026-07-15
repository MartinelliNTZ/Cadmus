class HtmlInstructions:
    def __init__(self, provider):
        self.provider = provider

    def get_raster_difference_statistics_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para calcular diferencias entre múltiples rasters, con estadísticas automáticas y reporte HTML consolidado.
            {self.provider.transform_h('Objetivo')}
            Calcular diferencias entre todos los pares posibles de rasters.
            Identificar variaciones entre superficies.
            Generar estadísticas automáticas para cada comparación.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Informe una carpeta con rasters o seleccione rasters ya cargados en QGIS.
            3. Defina la salida si es necesario.
            4. Ejecute.
            {self.provider.transform_h('Salidas')}
            DIF_rasterA_rasterB.tif
            DIF_rasterA_rasterB_stats.html
            raster_difference_stats_summary.html
            {self.provider.transform_h('Atención')}
            El número de combinaciones crece rápidamente.
            Puede generar muchos archivos.
            Las diferencias usan solo la banda 1.
            {self.provider.author_info}
        """

    def get_difference_fields_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para generar campos de diferencia entre un campo base y otros campos numéricos de la capa.
            {self.provider.transform_h('Objetivo')}
            Calcular la diferencia entre varios atributos numéricos usando un campo base como referencia.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Seleccione la capa de puntos.
            3. Defina el campo base.
            4. Elija campos a excluir si es necesario.
            5. Configure prefijo y precisión.
            6. Ejecute.
            {self.provider.transform_h('Salidas')}
            Nuevos campos creados con el prefijo definido.
            {self.provider.transform_h('Atención')}
            Los campos no numéricos se ignoran.
            Los valores nulos generan salida nula.
            {self.provider.author_info}
        """

    def get_raster_mass_clipper_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para recorte masivo de rasters usando una capa poligonal como máscara.
            {self.provider.transform_h('Objetivo')}
            Recortar múltiples rasters en una sola ejecución.
            Permitir recorte por capa completa o por entidad.
            Aplicar corrección automática de borde.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Defina la máscara poligonal.
            3. Seleccione los rasters.
            4. Configure el modo y la carpeta de salida.
            5. Ejecute.
            {self.provider.transform_h('Salidas')}
            raster_clip.tif
            raster_feat_1.tif
            {self.provider.transform_h('Atención')}
            El modo por entidad puede generar muchos archivos.
            El buffer amplía levemente el área recortada.
            {self.provider.author_info}
        """

    def get_geometry_difference_line_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para crear líneas entre puntos y calcular distancias.
            {self.provider.transform_h('Objetivo')}
            Generar líneas conectando puntos relacionados.
            Calcular distancia entre pares.
            Soportar comparación con una o dos capas.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Seleccione la capa A.
            3. Active la segunda capa si es necesario.
            4. Defina los campos de agrupación.
            5. Ejecute.
            {self.provider.transform_h('Salidas')}
            Capa de líneas con group_key, feature_a, feature_b y distance.
            {self.provider.transform_h('Atención')}
            El modo 2 requiere la capa B y un campo correspondiente.
            Las geometrías vacías se ignoran.
            {self.provider.author_info}
        """

    def get_grid_generator_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para generar una cuadrícula de puntos, líneas o polígonos dentro de un área poligonal.
            {self.provider.transform_h('Objetivo')}
            Generar una cuadrícula regular usando la extensión de una capa de entrada.
            Extraer solo las celdas que intersectan la capa de entrada.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Seleccione la capa de entrada poligonal.
            3. Defina el espaciamiento horizontal y vertical.
            4. Elija el tipo de cuadrícula.
            5. Active el registro detallado si desea detalles de ejecución.
            6. Ejecute.
            {self.provider.transform_h('Salidas')}
            Capa de cuadrícula con geometría de punto, línea o polígono.
            {self.provider.transform_h('Atención')}
            El espaciamiento controla la densidad de la cuadrícula.
            Las geometrías inválidas pueden reducir la cobertura de salida.
            {self.provider.author_info}
        """

    def get_raster_mass_sampler_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para muestreo masivo de múltiples rasters sobre puntos.
            {self.provider.transform_h('Objetivo')}
            Extraer valores de varios rasters en ubicaciones puntuales.
            Generar una nueva capa con los valores muestreados.
            {self.provider.transform_alert('Los nombres de los rasters deben ser claros y únicos porque serán usados como nombres de campos de salida.')}
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Seleccione los puntos de entrada.
            3. Seleccione los rasters.
            4. Defina CRS de salida si es necesario.
            5. Ejecute.
            {self.provider.transform_h('Salidas')}
            Nueva capa de puntos con un campo adicional por raster.
            {self.provider.transform_h('Atención')}
            Los valores fuera de la extensión retornan nulo.
            Las diferencias de CRS pueden afectar la precisión.
            {self.provider.author_info}
        """

    def get_attribute_statistics_help(self):
        return f"""
            {self.provider.logo}
            Herramienta de Cadmus para calcular estadísticas descriptivas de atributos numéricos y exportar CSV.
            {self.provider.transform_h('Objetivo')}
            Calcular media, mediana, desviación estándar, percentiles y otras estadísticas.
            Exportar resultados a CSV.
            {self.provider.transform_h('Cómo usar')}
            1. Abra la herramienta.
            2. Seleccione la capa de entrada.
            3. Defina campos a excluir si es necesario.
            4. Ajuste la precisión decimal.
            5. Elija las estadísticas deseadas.
            6. Configure la salida y ejecute.
            {self.provider.transform_h('Salidas')}
            Archivo CSV con una fila por campo analizado.
            {self.provider.transform_h('Atención')}
            Solo se consideran campos numéricos.
            Los valores nulos se ignoran.
            {self.provider.author_info}
        """
