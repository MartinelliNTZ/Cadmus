# -*- coding: utf-8 -*-
from .Strings_pt_BR import Strings_pt_BR


class Strings_es(Strings_pt_BR):
    """Strings for Spanish (es)"""

    # General
    APP_NAME = "Cadmus"
    PLUGIN_LANGUAGE = "Idioma del plugin"

    # About
    ABOUT_CADMUS = "Acerca de Cadmus"
    VERSION = "Versión"
    UPDATED_ON = "Actualizado el"
    CREATED_ON = "Creado el"
    CREATOR = "Autor"
    LOCATION = "Ubicación"

    # Buttons
    CLOSE = "Cerrar"
    SAVE = "Guardar"
    LOAD_FILES = "Cargar archivos"
    EXPORT = "Exportar"
    CANCEL = "Cancelar"
    EXECUTE = "Ejecutar"
    COPIED = "Copiado"
    COPY = "Copiar"
    SELECT = "Seleccionar"
    REMOVE = "Quitar"
    INVERT = "Invertir"
    ENABLE = "Activar"
    INFO = "Info"
    INSTRUCTIONS = "Instrucciones"
    AUTO_DETECT = "Auto-detectar"

    # Common labels
    PRECISION = "Precisión"
    CONTINUE_ANYWAY = "Continuar de todas formas"
    MENU_SYSTEM = "Sistema"
    MENU_LAYOUTS = "Layouts"
    MENU_FOLDER = "Carpeta"
    MENU_VECTOR = "Vector"
    MENU_AGRICULTURE = "Agricultura"
    MENU_RASTER = "Raster"
    OPTIONS = "Opciones"
    SAVING = "Guardando"
    STYLES = "Estilos"
    WARNING = "Advertencia"
    ERROR = "Error"
    ADVANCED_PARAMETERS = "Parámetros avanzados"
    APP_PREFERENCES = "Preferencias de la aplicación"
    OPEN_PREFERENCES_FOLDER = "Abrir carpeta de preferencias"
    FILE_TYPES = "Tipos de archivo"
    ROOT_FOLDER = "Carpeta raíz:"
    OUTPUT_FOLDER = "Carpeta de salida:"
    INPUT_LINE_LAYER = "Capa de líneas (INPUT):"
    SOURCE_LAYER = "Capa de origen:"
    TARGET_LAYER = "Capa de destino:"
    IMPLEMENT_SIZE = "Ancho del implemento (metros):"
    VECTOR_CALCULATION_METHOD = "Método de cálculo vectorial"
    VECTOR_FIELDS_PRECISION = "Precisión de campos vectoriales (decimales):"
    ASYNC_THRESHOLD = "Umbral asíncrono (nº de entidades):"
    CALCULATION_METHOD_LABEL = "Método de cálculo vectorial:"
    SEARCH_TEXT = "Texto a buscar:"
    REPLACE_WITH_NEW_TEXT = "Reemplazar por:"
    SOURCE_LAYER_ATTRIBUTES = "Atributos de la capa de origen"
    ATTRIBUTES = "Atributos"
    USE_ALL_ATTRIBUTES = "Usar todos los atributos"
    EXPORT_OPTIONS = "Opciones de exportación"
    MAX_WIDTH_PNG = "Ancho máximo PNG (px):"
    USE_PROJECT_FOLDER = "Usar carpeta del proyecto"
    EXPORT_PDF = "Exportar como PDF"
    EXPORT_PNG = "Exportar como PNG"
    MERGE_PDFS_FINAL = "Unir PDFs en archivo final"
    MERGE_PNGS_FINAL = "Convertir PNGs a PDF"
    REPLACE_EXISTING_FILES = "Sobrescribir archivos existentes"
    WGS84_EPSG4326 = "WGS 84 (EPSG:4326)"
    UTM_SIRGAS_2000 = "UTM SIRGAS 2000"
    ALTIMETRY_OPENTOPO = "Altimetría (OpenTopoData)"
    APPROX_ALTITUDE_METERS = "Altitud aprox. (m)"
    LATITUDE_DECIMAL = "Latitud (decimal)"
    LONGITUDE_DECIMAL = "Longitud (decimal)"
    LATITUDE_DMS = "Latitud (DMS)"
    LONGITUDE_DMS = "Longitud (DMS)"
    EASTING_X = "Este (X)"
    NORTHING_Y = "Norte (Y)"
    ADDRESS_OSM = "Dirección (OSM):"
    COPY_WGS84_FULL = "Copiar WGS84 (completo)"
    COPY_UTM_FULL = "Copiar UTM (completo)"
    COPY_LOCATION_FULL = "Copiar ubicación (completa)"
    POINT_COORDINATES = "Coordenadas del punto"
    ZONE = "Zona"
    HEMISPHERE = "Hemisferio"
    CITY = "Municipio"
    FILE_NOT_FOUND = "Archivo no encontrado"
    INTERMEDIATE_REGION = "Región intermedia"
    STATE = "Estado"
    REGION = "Región"
    COUNTRY = "País"
    LOADING = "Cargando..."
    LOADING_LOWER = "cargando..."
    UNAVAILABLE = "No disponible"
    NO_PATH_SELECTED = "Ninguna ruta seleccionada"
    FILES_SELECTED = "archivo(s) seleccionado(s)"
    ITEMS_SELECTED = "elemento(s)"
    ONLY_SELECTED_FEATURES = "Solo entidades seleccionadas"
    APPLY_QML_STYLE = "Aplicar estilo QML"
    QML_LABEL = "QML:"
    SAVE_TO_FILE = "Guardar en archivo:"
    SELECT_PATH = "Seleccionar Ruta"
    BUTTON = "Botón"
    SAVE_FILE = "Guardar archivo"
    SELECT_FILE = "Seleccionar archivo"
    POINTS = "Puntos"
    TRACK = "Rastro"

    # Common option labels
    CASE_SENSITIVE = "Distinguir mayúsculas/minúsculas"
    FULL_LABEL_REPLACE = "Reemplazar todo el texto del label al encontrar coincidencia"
    LOAD_ONLY_MISSING_FILES = "Cargar solo archivos que aún no estén en el proyecto"
    PRESERVE_FOLDER_STRUCTURE = "Agrupar según la estructura de carpetas/subcarpetas"
    DO_NOT_GROUP_LAST_FOLDER = "No agrupar el último nivel de carpeta"
    CREATE_PROJECT_BACKUP_IF_SAVED = (
        "Crear copia de seguridad antes de cargar (si el proyecto está guardado)"
    )

    # Common messages
    SUCCESS_MESSAGE = "Proceso ejecutado con éxito."
    ERROR_LAYER_NOT_FOUND = "Error: capa no encontrada."
    SELECT_VALID_FOLDER = "Seleccione una carpeta válida."
    SELECT_AT_LEAST_ONE_FILE_TYPE = "Seleccione al menos un tipo de archivo."
    SELECT_AT_LEAST_ONE_EXPORT_FORMAT = "Seleccione al menos un formato (PDF o PNG)"
    SELECT_VALID_LINE_LAYER = "Seleccione una capa de líneas válida."
    INVALID_SOURCE_LAYER = "Capa de origen inválida"
    INVALID_TARGET_LAYER = "Capa de destino inválida"
    INVALID_INPUT_LAYER = "Capa de entrada inválida."
    FINAL_LAYER_NOT_FOUND = "Error: capa final no encontrada en el contexto."
    BUFFER_CANNOT_BE_ZERO = "El buffer no puede ser 0"
    ASYNC_STARTED = (
        "Ejecución en segundo plano iniciada. Revise el log para ver el progreso."
    )
    ASYNC_START_ERROR = "Error al iniciar la ejecución asíncrona:"
    ASYNC_FINISHED = "Ejecución asíncrona finalizada."
    ASYNC_EXECUTION_ERROR = "Error durante la ejecución asíncrona:"
    FILES_LOADED_PREFIX = "Se cargaron"
    FILES_SUFFIX = "archivos."
    SETTINGS_SAVED_TITLE = "Configuraciones guardadas"
    SETTINGS_SAVED_MESSAGE = "Las configuraciones se guardaron correctamente."
    PREFERENCES_FOLDER_NOT_FOUND = "Carpeta de preferencias no encontrada:"
    ENTER_TEXT_TO_SEARCH = "Ingrese el texto a buscar."
    CONFIRM_REPLACEMENTS = "Confirmar reemplazos"
    SEARCH_LABEL = "Buscar:"
    REPLACE_WITH_LABEL = "Reemplazar por:"
    DESTRUCTIVE_OPERATION_WARNING = "Advertencia - operación destructiva"
    LAYOUTS_ANALYZED = "Layouts analizados:"
    CHANGES_APPLIED = "Reemplazos aplicados:"
    REPLACEMENT_COMPLETED_TITLE = "Reemplazo completado"
    PROJECT_BACKUP_INFO = "Copia de seguridad: se creará una copia del proyecto (.qgz) en la carpeta backup junto al archivo del proyecto."
    LAYER_MUST_BE_EDITABLE = "La capa debe estar en modo edición"
    NO_ATTRIBUTE_SELECTED = "Ningún atributo seleccionado"
    ATTRIBUTES_COPIED_SUCCESS = (
        "Atributos copiados correctamente (cambios no guardados)"
    )
    REQUIRED_LIBRARY = "Biblioteca requerida"
    PYPDF2_REQUIRED_MESSAGE = "Para unir PDFs es necesario instalar el paquete PyPDF2.\n\n¿Desea instalarlo ahora?"
    PILLOW_REQUIRED_MESSAGE = "Para convertir PNGs a PDF es necesario instalar el paquete Pillow.\n\n¿Desea instalarlo ahora?"
    EXPORTING_LAYOUTS = "Exportando layouts..."
    FAILED_EXPORT_PDF = "Error al exportar PDF:"
    FAILED_EXPORT_PNG = "Error al exportar PNG:"
    ERROR_EXPORTING = "Error durante la exportación"
    FAILED_MERGE_PDFS = "Error al unir PDFs:"
    FAILED_MERGE_PNGS = "Error al unir PNGs:"
    ERRORS_FOUND = "Errores encontrados:"
    LAYOUTS_EXPORTED_SUCCESS = "¡Layout(s) exportado(s) correctamente!"
    PDFS_MERGED = "PDFs unidos"
    PNGS_MERGED = "PNGs unidos"
    EXPORT_LAYOUTS_COMPLETED = "Exportación de layouts completada"
    LOCATION_COPIED_TO_CLIPBOARD = "Ubicación copiada al portapapeles"
    ADDRESS_COPIED_TO_CLIPBOARD = "Dirección copiada al portapapeles"

    SELECT_VECTOR_LAYER = "Seleccione una capa vectorial"
    SELECT_EDITABLE_VECTOR_LAYER = "Seleccione una capa vectorial editable"
    LAYER_HAS_NO_FEATURES = "La capa no tiene entidades"
    OPERATION_CANCELLED_BY_USER = "Operación cancelada por el usuario"
    GEOMETRY_TYPE_NOT_SUPPORTED = "Tipo de geometría no soportado"
    ERROR_IN_PREPARATION = "Error en la preparación:"
    KML_FILES_ARE_NOT_EDITABLE = "Los archivos KML no son editables."
    CONVERT_LAYER_TO_GPKG_OR_SHP_BEFORE_USING = "Convierta la capa a GeoPackage (.gpkg) o Shapefile (.shp) antes de usar esta herramienta."
    LAYER_USES_GEOGRAPHIC_CRS = "La capa usa CRS geográfico"
    CARTESIAN_MODE_RESULTS_IN_DEGREES2 = (
        "El modo 'Cartesiano' resultaría en valores en grados²."
    )
    CALCULATING_BOTH_MODES_AUTOMATICALLY = "Calculando ambos modos automáticamente."
    XY_FIELDS_CALCULATED_SUCCESS = "Campos X/Y calculados correctamente"
    LINE_LENGTH_CALCULATED_SUCCESS = "Longitud de líneas calculada correctamente"
    POLYGON_AREA_CALCULATED_SUCCESS = "Área de polígonos calculada correctamente"
    ERROR_STARTING_CALCULATION = "Error al iniciar el cálculo:"
    UNKNOWN_ERROR = "Error desconocido"
    CALCULATION_FAILED = "Fallo en el cálculo:"
    GEOMETRIES_CONVERTED_TO_MULTIPART_NOT_SAVED = (
        "Geometrías convertidas a multipart (no guardadas)"
    )
    CONVERT_SELECTED_FEATURES_TO_MULTIPART = (
        "¿Convertir solo las entidades seleccionadas a multipart?"
    )
    CONVERT_ALL_FEATURES_TO_MULTIPART = "¿Convertir todas las entidades a multipart?"

    # Dependencies
    INSTALLING_DEPENDENCY = "Instalando dependencia..."
    INSTALLING_DEPENDENCIES = "Instalando dependencias"
    DEPENDENCY = "Dependencia"
    INSTALLED_SUCCESSFULLY = "instalada correctamente."
    SUCCESS = "Éxito"
    INSTALL_DEPENDENCY_FAILED = "No se pudo iniciar la instalación de la biblioteca."
    KML_FIELDS_REMOVED_SUCCESS = "Campos KML eliminados correctamente"
    NO_KML_FIELDS_FOUND = "No se encontraron campos KML para eliminar"
    ERROR_REMOVING_KML_FIELDS = "Error al eliminar campos KML:"
    RANGE = "Rango"
    RASTERS = "Rasters"
    INPUT_POINTS = "Puntos de entrada"
    REPROJECT_OUTPUT_LAYER_OPTIONAL = "Reproyectar capa de salida (opcional)"
    SAMPLED_VALUES = "Valores_Muestreados"
    OPEN_OUTPUT_FOLDER = "Abrir carpeta de salida"
    DISPLAY_HELP_FIELD = "Mostrar campo de ayuda (es necesario ejecutar y reiniciar)"
    OUTPUT_CRS_LABEL = "CRS de salida:"
    NONE = "None"
    FILE_SAVED_IN = "Archivo guardado en:"
    RASTER_MASS_SAMPLER_TITLE = "Muestreo Masivo de Rasters"
    RASTER_WEIGHTED_AVERAGE_TITLE = "Media Ponderada de Rasters"
    RASTER_MASS_CLIPPER_TITLE = "Recorte Masivo de Rasters"
    RASTER_MASS_SAMPLER_TOOLTIP = (
        "Ejecuta el muestreo por lotes de varios rasters sobre una capa vectorial.\n"
        "Abre el algoritmo del provider de Cadmus en Processing,\n"
        "permitiendo configurar entradas, campos y salidas en la interfaz estandar."
    )
    RASTER_MASS_CLIPPER_TOOLTIP = (
        "Recorta por lotes varios rasters usando una capa poligonal como mascara.\n"
        "Abre el algoritmo del provider de Cadmus en Processing,\n"
        "con soporte para recorte por entidad, buffer de correccion y carpeta de salida."
    )
    RASTER_DIFFERENCE_STATISTICS_TITLE = "Procesar Diferencia de Rasters"
    VECTOR_TO_SVG_TITLE = "Conversor de Vector a SVG"
    VECTOR_TO_SVG_TOOLTIP = (
        "Exporta una capa vectorial del proyecto a SVG.\n"
        "Permite configurar fondo, borde y etiqueta,\n"
        "además de generar un único archivo o un SVG\n"
        "separado por cada entidad."
    )
    VECTOR_LAYER_LABEL = "Capa Vectorial"
    BACKGROUND_COLOR = "Color de Fondo"
    BORDER_COLOR = "Color del Borde"
    BORDER_WIDTH = "Grosor del Borde"
    LABEL_COLOR = "Color de la Etiqueta"
    LABEL_SIZE = "Tamaño de la Etiqueta"
    SELECT_FILL_COLOR = "Seleccione el color de relleno"
    SELECT_BORDER_COLOR = "Seleccione el color del borde"
    SELECT_LABEL_COLOR = "Seleccione el color de la etiqueta"
    TRANSPARENT_BACKGROUND = "Fondo transparente"
    SHOW_BORDER = "Mostrar borde"
    SHOW_LABEL = "Mostrar etiqueta"
    GENERATE_SVG_FOR_EACH_FEATURE = "Generar SVG para cada entidad"
    SVGS_GENERATED_SUCCESS = "SVG(s) generado(s) con éxito."
    INPUT_MASK_POLYGON_LAYER = "Capa máscara (polígono)"
    CLIP_PER_EACH_POLYGON = "Recortar por cada polígono"
    APPLY_CORRECTION_BUFFER_PIXEL_1_1 = "Aplicar buffer de corrección (pixel * 1.1)"
    RASTER_FOLDER_OR_SELECT_RASTER_LAYERS = (
        "Carpeta de rasters o seleccione capas raster"
    )
    QGIS_RASTER_LAYERS_OR_SELECT_RASTER_FOLDER = (
        "Capas raster de QGIS o seleccione carpeta de rasters"
    )
    OUTPUT_FOLDER_FOR_GENERATED_RASTERS = "Carpeta de salida para rasters generados"
    NO_OUTPUT_FOLDER_PROVIDED_USING_TEMP = (
        "No se informó carpeta de salida. Usando temporal:"
    )
    INVALID_FOLDER = "Carpeta inválida"
    NO_RASTER_FOUND_IN_SPECIFIED_FOLDER = (
        "No se encontró ningún raster en la carpeta especificada."
    )
    INVALID_RASTER_IGNORED = "Raster inválido ignorado"
    PROCESSING_RASTER_DIFFERENCE_BY_FOLDER_OR_LAYERS = (
        "Procesando diferencia de rasters por carpeta/capas..."
    )
    INFORM_RASTER_FOLDER_OR_SELECT_LAYER = (
        "Informe una carpeta de rasters o seleccione al menos una capa raster."
    )
    AT_LEAST_2_RASTERS_REQUIRED = (
        "Se requieren al menos 2 rasters para calcular diferencias."
    )
    FOUND_RASTER_COMBINATIONS_FOR_DIFFERENCE = (
        "Combinaciones de rasters encontradas para diferencia:"
    )
    PROCESSING = "Procesando"
    NO_OVERLAP_BETWEEN = "Sin superposición entre"
    AND = "y"
    SKIPPING = "Saltando"
    CALCULATION_ERROR_FOR = "Error en el cálculo para"
    DIFFERENCE_RASTER_CREATED = "Raster de diferencia creado:"
    STATS_GENERATED_FOR = "Estadísticas generadas para"
    FAILED_TO_GENERATE_STATS_FOR = "Error al generar estadísticas para"
    CONSOLIDATED_REPORT_GENERATED = "Reporte consolidado generado:"
    DIFFERENCE_STATISTICS_SUMMARY_TITLE = (
        "Resumen de Estadísticas de Diferencia de Rasters"
    )
    TOTAL_PROCESSED_PAIRS = "Total de pares procesados:"
    RASTER = "Raster"
    STATISTICS = "Estadísticas"
    VECTOR = "Vector"
    INTERVAL = "Intervalo"
    GEOMETRY_LINE_FROM_POINTS_TITLE = "Línea de Diferencia entre Puntos"
    POINT_LAYER_MODE1_FIRST_LAYER_MODE2 = (
        "Capa de Puntos (Modo 1) / Primera Capa (Modo 2)"
    )
    BASE_ATTRIBUTE_LAYER_A = "Atributo base - capa A"
    USE_SECOND_LAYER_MODE2 = "Usar segunda capa (modo 2)"
    SECOND_POINT_LAYER_MODE2_OPTIONAL = "Segunda Capa de Puntos (Modo 2 - opcional)"
    BASE_ATTRIBUTE_LAYER_B_MODE2 = "Atributo base - capa B (modo 2)"
    DIFFERENCE_LINES = "Líneas de diferencias"
    INVALID_LAYER_A = "Capa A inválida."
    MODE2_REQUIRES_SECOND_POINT_LAYER = "El modo 2 requiere una segunda capa de puntos."
    MODE2_INFORM_GROUP_FIELD_LAYER_B = (
        "En el modo 2 informe el campo de agrupación de la capa B."
    )
    ERROR_CREATING_OUTPUT_LAYER = "Error al crear la capa de salida."
    PROCESS_COMPLETED_LINES_GENERATED_SUCCESS = (
        "Proceso completado: líneas generadas correctamente."
    )
    GRID_GENERATOR_TITLE = "Generador de Cuadrícula"
    GRID_GENERATOR_INPUT_LAYER = "Capa de Entrada (Polígono)"
    HORIZONTAL_SPACING = "Espaciado Horizontal"
    VERTICAL_SPACING = "Espaciado Vertical"
    GRID_TYPE = "Tipo de Cuadrícula"
    OUTPUT_GRID = "Cuadrícula de Salida"
    VERBOSE_LOG = "Registro Detallado"
    ATTRIBUTE_STATISTICS_TITLE = "Estadísticas de Atributos"
    INPUT_LAYER = "Capa de entrada"
    EXCLUDE_FIELDS_OPTIONAL = "Campos a excluir (opcional)"
    PRECISION_DECIMAL_PLACES = "Precisión (decimales)"
    LOAD_CSV_AUTOMATICALLY_AFTER_EXECUTION = (
        "Cargar CSV automáticamente después de la ejecución"
    )
    FORCE_CSV_PTBR_FORMAT = "Forzar CSV en formato PT-BR (usar ; y ,)"
    CALCULATE = "Calcular"
    OUTPUT_CSV_FILE = "Archivo CSV de salida"
    INVALID_LAYER = "Capa inválida."
    NO_NUMERIC_FIELD_FOUND = "No se encontró ningún campo numérico."
    FIELD = "Campo"
    COUNT = "Conteo"
    ERROR_SAVING_CSV = "Error al guardar CSV:"
    FILE_LOADED_AS_LAYER = "Archivo cargado como capa:"
    CSV_FILE_GENERATED = "Archivo CSV generado:"
    MEAN = "Media"
    MEAN_ABSOLUTE = "Media Absoluta"
    STD_POP = "Desviación Estándar (Pob.)"
    STD_SAMPLE = "Desviación Estándar (Muestra)"
    MINIMUM = "Mínimo"
    MAXIMUM = "Máximo"
    MEDIAN = "Mediana"
    PERCENTILE_5 = "Percentil 5%"
    PERCENTILE_95 = "Percentil 95%"
    MODE = "Moda"
    VARIANCE = "Varianza"
    SUM = "Suma"
    COEFFICIENT_OF_VARIATION = "Coeficiente de Variación"
    SKEWNESS = "Asimetría"
    KURTOSIS = "Curtosis"
    DIFFERENCE_FIELDS_TITLE = "Generador de Diferencias entre Campos"
    POINT_LAYER = "Capa de Puntos"
    BASE_FIELD_SUBTRAHEND = "Campo Base (sustraendo)"
    FIELDS_TO_EXCLUDE_FROM_CALCULATION = "Campos a EXCLUIR del cálculo"
    PREFIX_FOR_NEW_FIELDS = "Prefijo para nuevos campos"
    DIFFERENCE = "Diferencia"
    NO_EXCLUDED_FIELD_USING_ALL_NUMERIC = (
        "Ningún campo excluido -> usando todos los campos numéricos."
    )
    BASE = "Base"
    EXCLUDED_FIELDS = "Campos EXCLUIDOS"
    FIELDS_USED_IN_CALCULATION = "Campos utilizados en el cálculo"
    PREFIX = "Prefijo"
    PROCESS_FINISHED_SUCCESS = "Proceso finalizado con éxito."

    # plugins/DroneCoordinates.py
    DRONE_COORDINATES_TITLE = "DJI Coordenadas de dron"
    DRONE_COORDINATES_TOOLTIP = (
        "Lee archivos MRK de dron para generar puntos de fotos y la ruta de vuelo.\n"
        "Puede cruzar los puntos con metadatos de imágenes,\n"
        "guardar los resultados en archivo y aplicar estilos QML\n"
        "a los puntos y a la trayectoria generada."
    )
    RECURSIVE_SEARCH = "Buscar en subcarpetas"
    USE_MRK_DATA = "Obtener datos MRK"
    PHOTOS_METADATA = "Cruzar con metadatos de fotos"
    PHOTOS_METADATA_REQUIRED_MESSAGE = "Para cruzar con metadatos de fotos es necesario instalar el paquete Pillow.\n\n¿Desea instalarlo ahora?"
    GENERATE_REPORT = "Generar informe"
    MRK_FOLDER = "Carpeta MRK:"
    SAVE_POINTS_CHECKBOX = "¿Guardar puntos MRK en archivo?"
    SAVE_IN = "Guardar en:"
    SAVE_TRACK_CHECKBOX = "¿Guardar trayectoria en archivo?"
    USE_LOGO = "¿Usar logotipo?"
    LOGO_LABEL = "Logotipo:"
    PROJECT_TITLE = "Título del Proyecto"
    PROJECT_TITLE_HINT = "Ej: Finca Esperanza"
    APPLY_STYLE_POINTS = "¿Aplicar estilo (QML) a los puntos?"
    QML_POINTS = "QML puntos:"
    APPLY_STYLE_TRACK = "¿Aplicar estilo (QML) a la trayectoria?"
    QML_TRACK = "QML:"
    MRK_DROP_START = "Archivo MRK detectado. Iniciando conversion."
    CONVERT_FILE_SUCCESS = "Archivo convertido con exito."
    LOADED_EXISTING_GPKG = "Salidas GPKG existentes cargadas con exito."
    CONVERT_FILE_ERROR = "No fue posible convertir el archivo."
    REPORT_METADATA_TITLE = "Informe de Metadatos"
    REPORT_METADATA_TOOLTIP = (
        "Lista JSON temporales de metadatos y permite regenerar el informe HTML.\n"
        "Tambien ofrece un acceso rapido a la carpeta de informes."
    )
    REFRESH_JSON_LIST = "Actualizar lista JSON"
    OPEN_REPORTS_FOLDER = "Abrir carpeta de informes"
    OPEN_JSONS_FOLDER = "Abrir carpeta de JSON"
    VECTOR_WITHOUT_MRK_BLOCK_TITLE = "Generar Vector Sin MRK"
    VETORIZE_FLIGHT = "Vectorizar vuelo"
    VETORIZE_FLIGHT_TOOLTIP = (
        "Genera capas vectoriales de puntos y trayectoria a partir del JSON de metadatos seleccionado.\n"
        "Equivalente a ejecutar el pipeline de coordenadas de dron solo con el JSON."
    )
    NO_JSON_FOUND = "No se encontraron JSON temporales."

    # plugins/SettingsPlugin.py
    SETTINGS_TITLE = "Configuraciones de Cadmus"
    SETTINGS_TOOLTIP = (
        "Abre las configuraciones globales de Cadmus.\n"
        "Permite definir el método predeterminado de cálculo vectorial,\n"
        "la precisión de los campos y el umbral de entidades\n"
        "para el procesamiento asíncrono."
    )
    GENERAL = "General"
    DEFAULT_CRS = "SRC por defecto"
    PROJECTS_FOLDER = "Carpeta de proyectos"
    TOOLBAR_VISIBLE_CATEGORIES = "Barra de herramientas - Categorías visibles"
    VECTOR_CALCULATIONS_PLUGIN = "Plugin de Cálculos Vectoriales"
    CARTESIAN_SUFFIX = "Sufijo Cartesiano"
    ELLIPSOIDAL_SUFFIX = "Sufijo Elipsoidal"
    AREA_SUFFIXES_CANNOT_MATCH = (
        "Los sufijos cartesiano y elipsoidal no pueden ser iguales."
    )
    ELLIPSOIDAL = "Elipsoidal"
    CARTESIAN = "Cartesiano"
    BOTH = "Ambos"

    # plugins/ReplaceInLayouts.py
    REPLACE_IN_LAYOUTS_TITLE = "Reemplazar texto en layouts"
    REPLACE_IN_LAYOUTS_TOOLTIP = (
        "Busca textos en los labels de los layouts del proyecto\n"
        "y los reemplaza por el nuevo valor indicado.\n"
        "Permite reemplazo parcial o total del contenido\n"
        "cuando se encuentra coincidencia."
    )
    REPLACE_IN_LAYOUTS_SWAP = "Invertir"
    REPLACE_IN_LAYOUTS_RUN = "Ejecutar reemplazo"

    # plugins/LoadFolderLayers.py
    LOAD_FOLDER_LAYERS_TITLE = "Cargar carpeta de archivos"
    CREATE_PROJECT_TITLE = "Nuevo Proyecto"
    CREATE_PROJECT_TOOLTIP = (
        "Crea una nueva estructura de proyecto en una carpeta dedicada.\n"
        "Si aún no hay carpeta predeterminada, solicita esa ruta,\n"
        "luego crea la carpeta del proyecto, el archivo .qgz\n"
        "y las subcarpetas vectors y rasters."
    )
    DEFAULT_PROJECTS_FOLDER_TITLE = "Carpeta predeterminada de proyectos"
    DEFAULT_PROJECTS_FOLDER_PROMPT = "Defina la carpeta predeterminada donde se crearán los nuevos proyectos de Cadmus."
    PROJECT_NAME_TITLE = "Nuevo proyecto"
    PROJECT_NAME_PROMPT = "Ingrese el nombre del proyecto. Si se deja en blanco, se usará el nombre sugerido."
    PROJECT_NAME_LABEL = "Nombre del proyecto"
    PROJECTS_DEFAULT_FOLDER_MISSING = (
        "No se ha definido ninguna carpeta predeterminada para proyectos.\n\n"
        "¿Desea definir una carpeta predeterminada ahora?"
    )
    PROJECTS_DEFAULT_FOLDER_MISSING_TITLE = "Carpeta predeterminada no definida"
    PROJECT_FOLDER_ALREADY_EXISTS = "La carpeta del proyecto ya existe:"
    PROJECT_FOLDER_CREATE_ERROR = "No se pudo crear la estructura del proyecto:"
    PROJECT_FILE_CREATE_ERROR = "No se pudo crear el proyecto QGIS:"
    PROJECT_DEFAULT_FOLDER_PREPARE_ERROR = (
        "No se pudo preparar la carpeta predeterminada:"
    )
    PROJECT_DEFAULT_FOLDER_ACCESS_ERROR = (
        "No se pudo acceder a la carpeta predeterminada:"
    )
    CURRENT_PROJECT_SAVE_TO_NEW_DESTINATION_ERROR = (
        "QGIS no pudo guardar el proyecto actual en el nuevo destino."
    )
    NEW_PROJECT_FILE_WRITE_ERROR = "QGIS no pudo escribir el nuevo archivo .qgz."
    OPEN_NEW_QGIS_WINDOW_ERROR = (
        "El proyecto fue creado, pero no se pudo abrir otra ventana de QGIS."
    )
    PROJECT_CREATED_TITLE = "Proyecto creado"
    PROJECT_CREATED_SUCCESS = "Proyecto '{project_name}' creado con éxito"
    PROJECT_CREATED_OPENED_NEW_WINDOW = (
        "Proyecto '{project_name}' creado y abierto en otra ventana"
    )
    LOAD_FOLDER_LAYERS_TOOLTIP = (
        "Carga en lote archivos vectoriales y raster desde una carpeta\n"
        "y sus subcarpetas en el proyecto QGIS.\n"
        "Permite filtrar por tipo de archivo, evitar duplicados\n"
        "y organizar capas según la estructura de carpetas."
    )

    # plugins/GenerateTrailPlugin.py
    GENERATE_TRAIL_TITLE = "Generar rastro de máquinas"
    GENERATE_TRAIL_TOOLTIP = (
        "Genera el área cubierta por un implemento a partir de una capa de líneas.\n"
        "Convierte el ancho informado a la unidad de la capa,\n"
        "aplica un buffer con la mitad del valor y crea\n"
        "una nueva capa con el rastro resultante."
    )

    # plugins/CopyAttributesPlugin.py
    COPY_ATTRIBUTES_TITLE = "Copiar atributos vectoriales"
    COPY_ATTRIBUTES_TOOLTIP = (
        "Copia la estructura de campos de una capa vectorial de origen\n"
        "a una capa vectorial de destino.\n"
        "Permite seleccionar qué atributos crear y manejar conflictos\n"
        "de nombre cuando ya existen campos en la capa destino."
    )

    # plugins/ExportAllLayouts.py
    EXPORT_ALL_LAYOUTS_TITLE = "Exportar todos los layouts"
    EXPORT_ALL_LAYOUTS_TOOLTIP = (
        "Exporta todos los layouts del proyecto a PDF, PNG o ambos.\n"
        "Puede unir los PDFs en un solo archivo,\n"
        "convertir PNGs a PDF y controlar la sobrescritura\n"
        "de archivos en la carpeta de salida."
    )

    # plugins/VectorMultipartPlugin.py
    CONVERTER_MULTIPART_TITLE = "Convertir multipart"
    CONVERTER_MULTIPART_TOOLTIP = (
        "Procesa entidades multipart de la capa activa\n"
        "y las divide en entidades simples.\n"
        "Puede aplicarse solo a las entidades seleccionadas\n"
        "o a toda la capa, preservando atributos."
    )

    # plugins/CoordClickTool.py
    COORD_CLICK_TOOL_TITLE = "Capturar coordenadas"
    COORD_CLICK_TOOL_TOOLTIP = (
        "Permite hacer clic en el mapa para obtener coordenadas.\n"
        "Abre un diálogo con WGS84, UTM, altitud aproximada\n"
        "y dirección estimada, además de opciones de copia\n"
        "al portapapeles."
    )

    # core/ToolRegistry.py
    RESTART_QGIS_TITLE = "Guardar, cerrar y reabrir proyecto"
    RESTART_QGIS_TOOLTIP = (
        "Guarda el proyecto actual, cierra QGIS y lo vuelve a abrir.\n"
        "Útil para recuperar la sesión tras fallos\n"
        "o problemas visuales sin perder el trabajo."
    )
    LOGCAT_TITLE = "Visor de logs"
    LOGCAT_TOOLTIP = (
        "Abre el visor de logs del plugin.\n"
        "Permite inspeccionar mensajes, errores y eventos internos\n"
        "registrados por Cadmus."
    )
    ABOUT_DIALOG_TOOLTIP = (
        f"Abre la ventana {ABOUT_CADMUS} de {APP_NAME}.\n"
        "Muestra información general del plugin,\n"
        "como versión, autor y contexto del proyecto."
    )
    LAYER_NOT_EDITABLE_ASK = "La capa '{layer_name}' no está en modo edición.\n\n¿Desea activar la edición ahora?"
    LAYER_NOW_EDITABLE = "Capa puesta en modo edición automáticamente."
    VECTOR_FIELDS_TITLE = "Calcular campos vectoriales"
    VECTOR_FIELDS_TOOLTIP = (
        "Calcula automáticamente campos vectoriales como área,\n"
        "longitud o coordenadas X/Y en la capa activa.\n"
        "Útil para generar atributos técnicos\n"
        "sin edición manual campo por campo."
    )
    REMOVE_KML_FIELDS_TITLE = "Eliminar Campos KML"
    REMOVE_KML_FIELDS_TOOLTIP = (
        "Elimina de la capa activa los campos de atributos típicos de KML.\n"
        "La herramienta solo se ejecuta si la capa ya está en edición\n"
        "y no guarda ni cierra el modo de edición."
    )

    # plugins/PathExtensionPlugin.py
    PATH = "Path"
    PATH_EXTENSION_TITLE = "Quitar/Restaurar Extensión"
    PATH_EXTENSION_TOOLTIP = (
        "Quita o restaura la extensión de archivos en las rutas de las entidades"
    )
    MODE_REMOVE = "Quitar extensión"
    MODE_RESTORE = "Restaurar extensión"
    MODE_ZIP = "Comprimir archivos"
    MODE_UNZIP = "Descomprimir archivos"

    # Registry
    REG_TITLE = "Gestionar"
    REGISTRY_SAVED_SUCCESS = "Guardado y validado con éxito."
    REGISTRY_DELETED_SUCCESS = "Eliminado con éxito."
    REGISTRY_INVALID = "Inválido."
    REGISTRY_EMPTY = "Complete el campo."
    NO_KEY = "sin clave"
    EXPIRATION_DATE = "Vencimiento"
    REMAINING_DAYS = "días restantes"
    STATUS = "Estado"
    LEVEL = "Nivel"
    ACTIVE = "Activa"
    INACTIVE = "Inactiva"
    VALIDATE = "Validar"

    # plugins/SaveTemporaryLayersPlugin.py
    SAVE_TEMPORARY_LAYER_TITLE = "Guardar Temporales"
    SAVE_TEMPORARY_LAYER_TOOLTIP = "Guarda capas temporales (memory) del proyecto en archivos permanentes en el disco"
    EXTENSION_VECTOR = "Extensión Vector"
    EXTENSION_RASTER = "Extensión Raster"
    VECTORS_FOLDER = "Carpeta de Vectores"
    RASTERS_FOLDER = "Carpeta de Rasters"
    SEPARATOR = "Separador"
    VECTOR_EXTENSIONS = "Extensiones Vector"
    RASTER_EXTENSIONS = "Extensiones Raster"
    OUTPUT_CONFIG = "Configuración de Salida"
    CONVERTER_FILE_TYPE = "Tipo de Archivo"
    SELECT_OUTPUT_FOLDER = "Seleccionar Carpeta de Salida"

    # plugins/DividePointsByStripsPlugin.py
    DIVIDE_POINTS_BY_STRIPS_TITLE = "Dividir Vector de Puntos por Franjas"
    DIVIDE_POINTS_BY_STRIPS_TOOLTIP = (
        "Prepara la configuración para segmentar una capa de puntos en franjas.\n"
        "En esta primera etapa la herramienta registra la interfaz,\n"
        "organiza los parámetros operativos y de sensibilidad\n"
        "y deja la ejecución lista para la siguiente fase."
    )
    DIVIDE_POINTS_BY_STRIPS_INTRO = "Configure la capa de puntos y los parámetros iniciales de la división por franjas."
    OPERATIONAL_PARAMETERS = "Parámetros Operativos"
    SENSITIVITY_PARAMETERS = "Parámetros de Sensibilidad"
    UNIQUE_SEQUENTIAL_ID_FIELD = "Campo ID único/secuencial"
    TIMESTAMP_FIELD = "Campo de timestamp"
    EXPECTED_POINT_FREQUENCY_SECONDS = "Frecuencia esperada de puntos (s)"
    EXPECTED_LATERAL_WIDTH_METERS = "Ancho lateral esperado (m)"
    AZIMUTH_MOVING_WINDOW = "Ventana de media de azimut"
    LIGHT_AZIMUTH_DEVIATION_THRESHOLD = "Umbral leve de desvío de azimut (grados)"
    SEVERE_AZIMUTH_DEVIATION_THRESHOLD = "Umbral grave de desvío de azimut (grados)"
    MINIMUM_BREAK_SCORE = "Puntaje mínimo de corte"
    MINIMUM_POINT_COUNT = "Número mínimo de puntos"
    TIME_TOLERANCE_MULTIPLIER = "Tolerancia de tiempo (multiplicador)"
    SELECT_POINT_VECTOR_LAYER = "Seleccione una capa vectorial de puntos."
    SELECT_FILE_BASED_POINT_LAYER = "Seleccione una capa de puntos basada en archivo."
    SELECT_REQUIRED_FIELDS = "Seleccione los campos obligatorios de ID y timestamp."
    SAVE_AND_STOP_EDITING_LAYER = (
        "Guarde y cierre la edición de la capa antes de ejecutar esta herramienta."
    )
    SHOT_SEGMENTATION_COMPLETED = "Segmentación finalizada. Puntos: {total_points} | Tiros: {total_shots} | Válidos: {valid_shots} | Inválidos: {invalid_shots}"
    SHOT_SEGMENTATION_BUFFER_COMPLETED = "Segmentación finalizada en el buffer de edición. Puntos: {total_points} | Tiros: {total_shots} | Válidos: {valid_shots} | Inválidos: {invalid_shots}"
    DIVIDE_POINTS_BY_STRIPS_UI_ONLY_MESSAGE = "La interfaz está lista. La rutina de división por franjas se implementará en la siguiente etapa."

    # processing/RasterOptimizer.py
    RASTER_OPTIMIZER_TITLE = "Optimizar Raster (Overviews)"
    RASTER_OPTIMIZER_TOOLTIP = (
        "Crea o reconstruye pirámides (overviews) en rasters TIFF.\n"
        "Permite seleccionar carpeta con rasters o capas individuales,\n"
        "elegir los niveles de overview, método de remuestreo\n"
        "y algoritmo de compresión (LZW, DEFLATE, ZSTD)."
    )
    INPUT_RASTER_LAYERS = "Capas Raster de Entrada"
    INPUT_RASTER_FOLDER = "Carpeta con Rasters"
    OVERVIEW_LEVELS = "Niveles de Overview"
    RESAMPLING_METHOD = "Método de Remuestreo"
    COMPRESS_OVERVIEW = "Compresión de Overviews"
    PREDICTOR = "Predictor"
    ZLEVEL = "ZLevel (compresión)"
    DELETE_EXISTING_OVERVIEWS = "Eliminar overviews existentes antes de recrear"
    OVERVIEWS_CREATED_SUCCESS = "Overviews creadas/actualizadas con éxito."
    OVERVIEWS_ERROR = "Error al crear overviews: {error}"
    RASTER_OPTIMIZER_COMPLETED = "Optimización de rasters completada."
    USE_RECURSIVE_SEARCH = "Incluir subcarpetas"
    SEARCHING_RASTERS = "Buscando rasters..."
    BIGTIFF_YES = "Forzar BIGTIFF (necesario para archivos >4GB)"
    RGB_MOSAIC_CREATOR_TITLE = "Creador de Mosaico RGB"
    INPUT_RASTER_RED_BAND = "Raster Banda Roja (R)"
    INPUT_RASTER_GREEN_BAND = "Raster Banda Verde (G)"
    INPUT_RASTER_BLUE_BAND = "Raster Banda Azul (B)"
    BAND_RED_LABEL = "Banda R"
    BAND_GREEN_LABEL = "Banda G"
    BAND_BLUE_LABEL = "Banda B"
    CREATE_ALPHA_BAND = "Crear banda alfa para NoData"
    ALPHA_NODATA_VALUE = "Valor NoData para alfa"
    RGB_COMPOSITE = "Composición RGB"
    NDVI_CALCULATOR_TITLE = "Calculadora NDVI"
    INPUT_RASTER_NIR = "Raster Infrarrojo Cercano (NIR)"
    INPUT_RASTER_RED = "Raster Rojo (RED)"
    BAND_NIR = "Banda NIR"
    BAND_RED = "Banda RED"
    SENTINEL_BANDS_INFO = "Sentinel-2: Banda 8 (NIR) y Banda 4 (Rojo)"
    LANDSAT_BANDS_INFO = (
        "Landsat 8/9: Banda 5 (NIR) y Banda 4 (Rojo) | "
        "Landsat 5/7: Banda 4 (NIR) y Banda 3 (Rojo)"
    )
    NDVI = "NDVI"
    NDRE_CALCULATOR_TITLE = "Calculadora NDRE (Red Edge)"
    INPUT_RASTER_NIR_NDRE = "Raster Infrarrojo Cercano (NIR) para NDRE"
    INPUT_RASTER_REDEDGE = "Raster Borde Rojo (RedEdge)"
    BAND_REDEDGE = "Banda RedEdge"
    NDRE = "NDRE"
    GLI_CALCULATOR_TITLE = "Calculadora GLI (Green Leaf Index)"
    INPUT_RASTER_RGB_GLI = "Raster RGB de entrada (3 o 4 bandas)"
    GLI = "GLI"
    GLI_STYLE_PATH = "Ruta del estilo QML GLI"
    GLI_INTERPRETATION = (
        "Interpretación de valores GLI:\n"
        "  -1.0 a 0.0  : Suelo desnudo, agua, superficies no vegetadas\n"
        "   0.0 a 0.2  : Vegetación escasa o estresada\n"
        "   0.2 a 0.5  : Vegetación moderada\n"
        "   0.5 a 1.0  : Vegetación densa y saludable"
    )
    RGB_STYLE_STANDARDIZER_TITLE = "Estandarizar Estilo RGB (Percentil)"
    INPUT_RASTER_RGB = "Raster RGB de entrada"
    RGB_STANDARDIZER_OUTPUT = "Raster RGB estandarizado"
    SEGMENTATION_MODE = "Modo de Segmentación"
    CURVE = "Curva"
    STRAIGHT = "Recta"
    BOTH_PATH = "Ambas"
