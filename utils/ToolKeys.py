# -*- coding: utf-8 -*-


class ToolKey:
    # all
    UNTRACEABLE = "untraceable"  # para logs genericos sem tool especifica
    # plugins/
    CADMUS_PLUGIN = "cadmus_plugin"
    EXPORT_ALL_LAYOUTS = "export_all_layouts"
    DRONE_COORDINATES = "drone_coordinates"
    REPORT_METADATA = "report_metadata"
    LOAD_FOLDER_LAYERS = "load_folder_layers"
    REPLACE_IN_LAYOUTS = "replace_in_layouts"
    RESTART_QGIS = "restart_qgis"
    GENERATE_TRAIL = "generate_trail"
    COORD_CLICK_TOOL = "coord_click_tool"
    COPY_ATTRIBUTES = "copy_attributes"
    DIVIDE_POINTS_BY_STRIPS = "divide_points_by_strips"
    CONVERTER_MULTIPART = "converter_multipart"
    REMOVE_KML_FIELDS = "remove_kml_fields"
    SETTINGS = "settings"
    SYSTEM = "SYSTEM"  # para logs genericos do sistema, sem tool especifica
    LOGCAT = "logcat"  # viewer de logs do plugin
    VECTOR_FIELDS = "vector_fields"
    ABOUT_DIALOG = "about_dialog"
    VECTOR_TO_SVG = "vector_to_svg"
    CREATE_PROJECT = "create_project"
    DIFFERENCE_BETWEEN_LINES = "difference_between_lines"
    SAVE_TEMPORARY_LAYER = "save_temporary_layer"
    PATH_EXTENSION_TOOL = "path_extension_tool"

    # model3 / panel tool
    # processing/
    ATTRIBUTE_STATISTICS = "attribute_statistics"
    DIFFERENCE_FIELDS = "difference_fields_algorithm"
    MY_ALGORITHM = "my_algorithm"
    PROVIDER = "provider"
    RASTER_MASS_SAMPLER = "raster_mass_sampler"
    ELEVATION_ANALISYS = "elevation_analisys"
    RASTER_MASS_CLIPPER = "raster_mass_clipper"
    GEOMETRY_LINE_FROM_POINTS = "geometry_line_from_points"
    RASTER_DIFERENCE_STATISTICS = "raster_diference_statistics"
    RASTER_WEIGHTED_AVERAGE = "raster_weighted_average"
    GRID_GENERATOR = "grid_generator"
    NDVI_CALCULATOR = "ndvi_calculator"
    RGB_MOSAIC_CREATOR = "rgb_mosaic_creator"
    RASTER_OPTIMIZER = "raster_optimizer"
    RGB_STYLE_STANDARDIZER = "rgb_style_standardizer"
    GLI_CALCULATOR = "gli_calculator"
    NDRE_CALCULATOR = "ndre_calculator"

    # Cores por tool_key (toolbar-first, semantica)
    TOOL_KEY_COLORS = {
        # === Toolbar / acoes principais ===
        CADMUS_PLUGIN: "#804E0A",  # laranja claro -> plugin principal
        EXPORT_ALL_LAYOUTS: "#4ECDC4",  # turquesa -> exportacao / layout
        DRONE_COORDINATES: "#45B7D1",  # azul -> coordenadas / espacial
        REPORT_METADATA: "#5DADE2",  # azul medio -> relatorios de metadata
        LOAD_FOLDER_LAYERS: "#96CEB4",  # verde -> carga de dados
        REPLACE_IN_LAYOUTS: "#F8C471",  # laranja -> alteracao / replace
        RESTART_QGIS: "#FF6B6B",  # vermelho -> acao critica
        GENERATE_TRAIL: "#82E0AA",  # verde limao -> geracao geometrica
        COORD_CLICK_TOOL: "#85C1E9",  # azul ceu -> map tool
        COPY_ATTRIBUTES: "#DDA0DD",  # plum -> dados / atributos
        DIVIDE_POINTS_BY_STRIPS: "#76D7C4",  # agua -> segmentacao de pontos em faixas
        CONVERTER_MULTIPART: "#F5A962",  # laranja-pessego -> conversao geometrica
        REMOVE_KML_FIELDS: "#58D68D",  # verde -> limpeza de atributos KML
        SETTINGS: "#95A5A6",  # cinza -> configuracoes / sistema
        VECTOR_FIELDS: "#C39BD3",  # purpura -> calculos vetoriais
        VECTOR_TO_SVG: "#7FB3D5",  # azul suave -> exportacao vetorial
        CREATE_PROJECT: "#73C6B6",  # verde agua -> criacao de projeto
        PATH_EXTENSION_TOOL: "#E67E22",  # laranja -> path extension
        SAVE_TEMPORARY_LAYER: "#3498DB",  # azul -> salvar temporárias
        # === Processing / analises ===
        ATTRIBUTE_STATISTICS: "#F7DC6F",  # amarelo -> estatistica
        DIFFERENCE_FIELDS: "#BB8FCE",  # roxo -> comparacao
        MY_ALGORITHM: "#98D8C8",  # verde agua -> generico
        PROVIDER: "#BFC9CA",  # cinza -> infraestrutura
        RASTER_MASS_SAMPLER: "#F1948A",  # coral -> raster pesado
        GRID_GENERATOR: "#F39C12",  # laranja forte -> gerador de grade
        ELEVATION_ANALISYS: "#5DADE2",  # azul medio -> relevo
        RASTER_OPTIMIZER: "#E67E22",  # laranja -> otimizacao raster
        NDVI_CALCULATOR: "#27AE60",  # verde -> ndvi / vegetacao
        RGB_MOSAIC_CREATOR: "#E74C3C",  # vermelho -> rgb / cor
        RGB_STYLE_STANDARDIZER: "#8E44AD",  # roxo -> padronizacao de estilo
        GLI_CALCULATOR: "#2ECC71",  # verde claro -> gli / vegetacao verde
    }
