# -*- coding: utf-8 -*-
from ..model.Tool import Tool
from ...resources.IconManager import IconManager as im
from .LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey
from ...utils.QgisMessageUtil import QgisMessageUtil
from ...i18n.TranslationManager import STR
from ...utils.StringManager import StringManager
from ...utils.Preferences import Preferences
from ..enum import ToolTypeEnum


class ToolRegistry:
    # Tipos de ferramenta (não usar enum separado conforme requisito)
    SYSTEM, LAYOUTS, FOLDER, VECTOR, AGRICULTURE, RASTER = (
        StringManager.MENU_CATEGORIES.keys()
    )

    _instance = None  # Singleton instance

    @classmethod
    def get_instance(cls):
        """Retorna a instância singleton do ToolRegistry."""
        return cls._instance

    def __init__(self, iface):
        self.iface = iface
        self.logger = LogUtils(tool=ToolKey.SYSTEM, class_name="ToolRegistry")

        self.logger.info(
            "[ToolRegistry.__init__] Inicializando ToolRegistry (singleton)"
        )

        # Inicializar vazio, será carregado
        self._main_action_prefs = {}

        # Criar ToolList lendo Preferences UMA ÚNICA VEZ
        self.tools = self._create_tool_list()

        # Salvar metadata
        self._save_tool_metadata()

        # Validar e atualizar main_actions
        self._main_action_prefs = self._load_and_validate_main_actions_strict()

        # Recriar tools com main_actions validadas
        self.tools = self._create_tool_list()

        # Filtrar ferramentas por nível de licença
        self._filter_tools_by_reg()

        self.logger.info(
            f"[ToolRegistry.__init__] ✓ Inicializado com {len(self.tools)} ferramentas"
        )

        # Armazenar como singleton
        ToolRegistry._instance = self
        self._package = __package__

    def _save_tool_metadata(self):
        """
        Salva category e tool_type nas preferências de cada ferramenta.
        Isso permite que Preferences filtre por categoria posteriormente.
        """
        for tool in self.tools:
            try:
                prefs = Preferences.load_tool_prefs(tool.tool_key)
                prefs["category"] = tool.category
                prefs["tool_type"] = tool.tool_type
                Preferences.save_tool_prefs(tool.tool_key, prefs)
            except Exception as e:
                self.logger.error(
                    f"Erro ao salvar metadata do tool '{tool.tool_key}': {e}"
                )

    def _load_and_validate_main_actions_strict(self):
        """
        Valida `main_action` usando a lista canÃ´nica do registry.

        Para cada categoria, garante exatamente uma ferramenta com `True` e
        todas as demais com `False`. Qualquer valor salvo fora desse padrÃ£o
        tambÃ©m Ã© normalizado para booleano estrito.
        """
        all_prefs = Preferences.load_prefs()
        main_action_prefs = {}
        tools_by_category = {}

        self.logger.info(
            f"[_load_and_validate_main_actions_strict] Iniciando validaÃ§Ã£o. "
            f"Total de ferramentas do registry: {len(self.tools)}"
        )

        for tool in sorted(self.tools, key=lambda t: (t.category, t.order, t.tool_key)):
            tool_prefs = all_prefs.get(tool.tool_key, {})
            if not isinstance(tool_prefs, dict):
                tool_prefs = {}

            raw_main_action = tool_prefs.get("main_action", tool.main_action)
            normalized_main_action = raw_main_action is True

            main_action_prefs[tool.tool_key] = normalized_main_action
            tools_by_category.setdefault(tool.category, []).append(tool)

            self.logger.debug(
                f"[_load_and_validate_main_actions_strict] Tool '{tool.tool_key}': "
                f"category={tool.category}, raw_main_action={raw_main_action}, "
                f"normalized_main_action={normalized_main_action}"
            )

        for category, category_tools in tools_by_category.items():
            true_tools = [
                tool
                for tool in category_tools
                if main_action_prefs.get(tool.tool_key) is True
            ]

            if len(true_tools) == 1:
                selected_tool = true_tools[0]
            elif len(true_tools) > 1:
                selected_tool = true_tools[0]
                self.logger.warning(
                    f"[_load_and_validate_main_actions_strict] Categoria '{category}': "
                    f"{len(true_tools)} ferramentas com main_action=True. "
                    f"Mantendo apenas '{selected_tool.tool_key}'."
                )
            else:
                selected_tool = next(
                    (tool for tool in category_tools if tool.main_action is True),
                    category_tools[0],
                )
                self.logger.warning(
                    f"[_load_and_validate_main_actions_strict] Categoria '{category}': "
                    f"nenhuma com main_action=True. ForÃ§ando '{selected_tool.tool_key}'."
                )

            for tool in category_tools:
                validated_value = tool.tool_key == selected_tool.tool_key
                main_action_prefs[tool.tool_key] = validated_value
                self.logger.debug(
                    f"[_load_and_validate_main_actions_strict] Corrigido '{tool.tool_key}': "
                    f"main_action={validated_value}"
                )

        for tool_key, is_main in main_action_prefs.items():
            prefs = Preferences.load_tool_prefs(tool_key)
            prefs["main_action"] = is_main
            Preferences.save_tool_prefs(tool_key, prefs)

        self.logger.info(
            f"[_load_and_validate_main_actions_strict] ValidaÃ§Ã£o concluÃ­da: "
            f"{main_action_prefs}"
        )
        return main_action_prefs

    def _create_tool_list(self):
        tools = []

        # =====================================================
        # LAYOUTS (Ordem: Export=10, Replace=20)
        # =====================================================

        export_layouts = Tool(
            tool_key=ToolKey.EXPORT_ALL_LAYOUTS,
            name=STR.EXPORT_ALL_LAYOUTS_TITLE,
            icon=im.icon(im.EXPORT_ALL_LAYOUTS),
            category=self.LAYOUTS,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.EXPORT_ALL_LAYOUTS, True),
            executor=self._make_plugin_executor("...plugins.ExportAllLayouts"),
            tooltip=STR.EXPORT_ALL_LAYOUTS_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(export_layouts)

        replace_layouts = Tool(
            tool_key=ToolKey.REPLACE_IN_LAYOUTS,
            name=STR.REPLACE_IN_LAYOUTS_TITLE,
            icon=im.icon(im.REPLACE_IN_LAYOUTS),
            category=self.LAYOUTS,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.REPLACE_IN_LAYOUTS, False),
            executor=self._make_plugin_executor("...plugins.ReplaceInLayouts"),
            tooltip=STR.REPLACE_IN_LAYOUTS_TOOLTIP,
            order=20,
            show_in_toolbar=True,
        )
        tools.append(replace_layouts)

        # =====================================================
        # SYSTEM (Ordem: Restart=10, Logcat=20, Settings=30, About=40)
        # =====================================================

        restart_qgis = Tool(
            tool_key=ToolKey.RESTART_QGIS,
            name=STR.RESTART_QGIS_TITLE,
            icon=im.icon(im.RESTART_QGIS),
            category=self.SYSTEM,
            tool_type=ToolTypeEnum.INSTANT,
            main_action=self._main_action_prefs.get(ToolKey.RESTART_QGIS, False),
            executor=self._make_plugin_executor("...plugins.RestartQgis"),
            tooltip=STR.RESTART_QGIS_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(restart_qgis)

        logcat = Tool(
            tool_key=ToolKey.LOGCAT,
            name=STR.LOGCAT_TITLE,
            icon=im.icon(im.LOGCAT),
            category=self.SYSTEM,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.LOGCAT, False),
            executor=self._make_plugin_executor("...plugins.logcat.logcat_plugin"),
            tooltip=STR.LOGCAT_TOOLTIP,
            order=20,
            show_in_toolbar=True,
            registry_level=3,
        )
        tools.append(logcat)

        settings = Tool(
            tool_key=ToolKey.SETTINGS,
            name=STR.SETTINGS_TITLE,
            icon=im.icon(im.SETTINGS),
            category=self.SYSTEM,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.SETTINGS, True),
            executor=self._make_plugin_executor("...plugins.SettingsPlugin"),
            tooltip=STR.SETTINGS_TOOLTIP,
            order=30,
            show_in_toolbar=True,
        )
        tools.append(settings)

        about = Tool(
            tool_key=ToolKey.ABOUT_DIALOG,
            name=STR.ABOUT_CADMUS,
            icon=im.icon(im.ABOUT),
            category=self.SYSTEM,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.ABOUT_DIALOG, False),
            executor=self._make_plugin_executor("...plugins.AboutDialog"),
            tooltip=STR.ABOUT_DIALOG_TOOLTIP,
            order=40,
            show_in_toolbar=True,
        )
        tools.append(about)

        # =====================================================
        # FOLDER (Ordem: Load=10)
        # =====================================================

        load_folder = Tool(
            tool_key=ToolKey.LOAD_FOLDER_LAYERS,
            name=STR.LOAD_FOLDER_LAYERS_TITLE,
            icon=im.icon(im.LOAD_FOLDER_LAYER),
            category=self.FOLDER,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.LOAD_FOLDER_LAYERS, False),
            executor=self._make_plugin_executor("...plugins.LoadFolderLayers"),
            tooltip=STR.LOAD_FOLDER_LAYERS_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(load_folder)

        create_project = Tool(
            tool_key=ToolKey.CREATE_PROJECT,
            name=STR.CREATE_PROJECT_TITLE,
            icon=im.icon(im.CREATE_PROJECT),
            category=self.FOLDER,
            tool_type=ToolTypeEnum.INSTANT,
            main_action=self._main_action_prefs.get(ToolKey.CREATE_PROJECT, True),
            executor=self._make_plugin_executor("...plugins.CreateProjectPlugin"),
            tooltip=STR.CREATE_PROJECT_TOOLTIP,
            order=15,
            show_in_toolbar=True,
        )
        tools.append(create_project)

        vector_to_svg = Tool(
            tool_key=ToolKey.VECTOR_TO_SVG,
            name=STR.VECTOR_TO_SVG_TITLE,
            icon=im.icon(im.VECTOR_TO_SVG),
            category=self.FOLDER,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.VECTOR_TO_SVG, False),
            executor=self._make_plugin_executor("...plugins.VectorToSvgPlugin"),
            tooltip=STR.VECTOR_TO_SVG_TOOLTIP,
            order=20,
            show_in_toolbar=True,
        )
        tools.append(vector_to_svg)

        # =====================================================
        # VECTOR (Ordem: Fields=10, Coords=20, Pasta=30, Multipart=40, Copy=50)
        # =====================================================

        vector_fields = Tool(
            tool_key=ToolKey.VECTOR_FIELDS,
            name=STR.VECTOR_FIELDS_TITLE,
            icon=im.icon(im.VECTOR_FIELD),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.INSTANT,
            main_action=self._main_action_prefs.get(ToolKey.VECTOR_FIELDS, True),
            executor=self._make_plugin_executor(
                "...plugins.VectorFieldsCalculationPlugin"
            ),
            tooltip=STR.VECTOR_FIELDS_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(vector_fields)

        remove_kml_fields = Tool(
            tool_key=ToolKey.REMOVE_KML_FIELDS,
            name=STR.REMOVE_KML_FIELDS_TITLE,
            icon=im.icon(im.REMOVE_KML_FIELDS),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.INSTANT,
            main_action=self._main_action_prefs.get(ToolKey.REMOVE_KML_FIELDS, False),
            executor=self._make_plugin_executor("...plugins.RemoveKmlFieldsPlugin"),
            tooltip=STR.REMOVE_KML_FIELDS_TOOLTIP,
            order=15,
            show_in_toolbar=True,
        )
        tools.append(remove_kml_fields)

        coord_click = Tool(
            tool_key=ToolKey.COORD_CLICK_TOOL,
            name=STR.COORD_CLICK_TOOL_TITLE,
            icon=im.icon(im.COORD_CLICK_TOOL),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.MAP_TOOL,
            main_action=self._main_action_prefs.get(ToolKey.COORD_CLICK_TOOL, False),
            executor=self.run_coord_click,
            tooltip=STR.COORD_CLICK_TOOL_TOOLTIP,
            order=20,
            show_in_toolbar=True,
        )
        tools.append(coord_click)

        multipart = Tool(
            tool_key=ToolKey.CONVERTER_MULTIPART,
            name=STR.CONVERTER_MULTIPART_TITLE,
            icon=im.icon(im.VECTOR_MULTPART),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.INSTANT,
            main_action=self._main_action_prefs.get(ToolKey.CONVERTER_MULTIPART, False),
            executor=self._make_plugin_executor("...plugins.VectorMultipartPlugin"),
            tooltip=STR.CONVERTER_MULTIPART_TOOLTIP,
            order=40,
            show_in_toolbar=True,
        )
        tools.append(multipart)

        copy_attributes = Tool(
            tool_key=ToolKey.COPY_ATTRIBUTES,
            name=STR.COPY_ATTRIBUTES_TITLE,
            icon=im.icon(im.COPY_ATTRIBUTES),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.COPY_ATTRIBUTES, False),
            executor=self._make_plugin_executor("...plugins.CopyAttributesPlugin"),
            tooltip=STR.COPY_ATTRIBUTES_TOOLTIP,
            order=50,
            show_in_toolbar=True,
        )
        tools.append(copy_attributes)

        divide_points_by_strips = Tool(
            tool_key=ToolKey.DIVIDE_POINTS_BY_STRIPS,
            name=STR.DIVIDE_POINTS_BY_STRIPS_TITLE,
            icon=im.icon(im.DIVIDE_POINTS_BY_STRIPS),
            category=self.VECTOR,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(
                ToolKey.DIVIDE_POINTS_BY_STRIPS, False
            ),
            executor=self._make_plugin_executor(
                "...plugins.DividePointsByStripsPlugin"
            ),
            tooltip=STR.DIVIDE_POINTS_BY_STRIPS_TOOLTIP,
            order=60,
            show_in_toolbar=True,
            registry_level=1,
        )
        tools.append(divide_points_by_strips)

        save_temporary_layer = Tool(
            tool_key=ToolKey.SAVE_TEMPORARY_LAYER,
            name=STR.SAVE_TEMPORARY_LAYER_TITLE,
            icon=im.icon(im.SAVE_TEMPORARY_LAYER),
            category=self.FOLDER,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(
                ToolKey.SAVE_TEMPORARY_LAYER, False
            ),
            executor=self._make_plugin_executor("...plugins.SaveTemporaryLayersPlugin"),
            tooltip=STR.SAVE_TEMPORARY_LAYER_TOOLTIP,
            order=70,
            show_in_toolbar=True,
        )
        tools.append(save_temporary_layer)

        path_extension = Tool(
            tool_key=ToolKey.PATH_EXTENSION_TOOL,
            name=STR.PATH_EXTENSION_TITLE,
            icon=im.icon(im.PATH_EXTENSION),
            category=self.AGRICULTURE,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.PATH_EXTENSION_TOOL, False),
            executor=self._make_plugin_executor("...plugins.PathExtensionPlugin"),
            tooltip=STR.PATH_EXTENSION_TOOLTIP,
            order=70,
            show_in_toolbar=True,
            registry_level=3,
        )
        tools.append(path_extension)

        # =====================================================
        # AGRICULTURE (Ordem: Drone=10, Trail=20, Report=30)
        # =====================================================

        drone_coords = Tool(
            tool_key=ToolKey.DRONE_COORDINATES,
            name=STR.DRONE_COORDINATES_TITLE,
            icon=im.icon(im.DRONE_COORDINATES),
            category=self.AGRICULTURE,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.DRONE_COORDINATES, True),
            executor=self._make_plugin_executor("...plugins.DroneCoordinates"),
            tooltip=STR.DRONE_COORDINATES_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(drone_coords)

        gerar_rastro = Tool(
            tool_key=ToolKey.GENERATE_TRAIL,
            name=STR.GENERATE_TRAIL_TITLE,
            icon=im.icon(im.GENERATE_TRAIL),
            category=self.AGRICULTURE,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.GENERATE_TRAIL, False),
            executor=self._make_plugin_executor("...plugins.GenerateTrailPlugin"),
            tooltip=STR.GENERATE_TRAIL_TOOLTIP,
            order=20,
            show_in_toolbar=True,
        )
        tools.append(gerar_rastro)
        report_metadata = Tool(
            tool_key=ToolKey.REPORT_METADATA,
            name=STR.REPORT_METADATA_TITLE,
            icon=im.icon(im.REPORT_METADATA),
            category=self.AGRICULTURE,
            tool_type=ToolTypeEnum.DIALOG,
            main_action=self._main_action_prefs.get(ToolKey.REPORT_METADATA, False),
            executor=self._make_plugin_executor("...plugins.ReportMetadataPlugin"),
            tooltip=STR.REPORT_METADATA_TOOLTIP,
            order=30,
            show_in_toolbar=True,
            registry_level=1,
        )
        tools.append(report_metadata)

        # =====================================================
        # RASTER (Ordem: Mass Clipper=10)
        # =====================================================

        raster_mass_clipper = Tool(
            tool_key=ToolKey.RASTER_MASS_CLIPPER,
            name=STR.RASTER_MASS_CLIPPER_TITLE,
            icon=im.icon(im.RASTER_MASS_CLIPPER),
            category=self.RASTER,
            tool_type=ToolTypeEnum.PROCESSING,
            main_action=self._main_action_prefs.get(
                ToolKey.RASTER_MASS_CLIPPER, True
            ),  # Alterado para False para que o Sampler seja o principal por padrão
            executor=self._make_provider_executor(
                "cadmus:raster_mass_clipper", STR.RASTER_MASS_CLIPPER_TITLE
            ),
            tooltip=STR.RASTER_MASS_CLIPPER_TOOLTIP,
            order=10,
            show_in_toolbar=True,
        )
        tools.append(raster_mass_clipper)

        raster_mass_sampler = Tool(
            tool_key=ToolKey.RASTER_MASS_SAMPLER,
            name=STR.RASTER_MASS_SAMPLER_TITLE,
            icon=im.icon(im.RASTER_MASS_SAMPLER),
            category=self.RASTER,
            tool_type=ToolTypeEnum.PROCESSING,
            main_action=self._main_action_prefs.get(
                ToolKey.RASTER_MASS_SAMPLER, False
            ),  # Alterado para True para ser o principal por padrão
            executor=self._make_provider_executor(
                "cadmus:raster_mass_sampler", STR.RASTER_MASS_SAMPLER_TITLE
            ),
            tooltip=STR.RASTER_MASS_SAMPLER_TOOLTIP,
            order=20,
            show_in_toolbar=True,
        )
        tools.append(raster_mass_sampler)

        return tools

    def get_tools(self):
        return list(self.tools)

    def update_tool_main_action(self, tool_key, category=None):
        """
        Atualiza main_action de uma ferramenta quando ela abre/fecha.

        Operações:
        1. Encontra ferramenta na ToolList
        2. Reseta main_action em categoria
        3. Seta main_action=True para ferramenta
        4. Persiste em Preferences

        Args:
            tool_key (str): Identificador da ferramenta
            category (str, optional): Categoria (auto-detectada se omitida)

        Returns:
            str or None: Categoria da ferramenta (para reconstrução de toolbar)
        """
        try:
            # 1. Encontrar ferramenta
            tool_found = None
            for tool in self.tools:
                if tool.tool_key == tool_key:
                    tool_found = tool
                    category = tool.category
                    break

            if tool_found is None:
                self.logger.warning(
                    f"[update_tool_main_action] Ferramenta '{tool_key}' não encontrada"
                )
                return None

            # 2. Resetar main_action em categoria
            for tool in self.tools:
                if tool.category == category and tool.tool_key != tool_key:
                    tool.main_action = False

            # 3. Setar main_action=True para esta ferramenta
            tool_found.main_action = True

            # 4. Persistir em Preferences
            Preferences.set_value_for_all_tools(
                "main_action", False, filter_by={"category": category}
            )
            tool_prefs = Preferences.load_tool_prefs(tool_key)
            tool_prefs["main_action"] = True
            Preferences.save_tool_prefs(tool_key, tool_prefs)

            self.logger.info(
                f"[update_tool_main_action] '{tool_key}' definido como main_action (categoria: {category})"
            )
            return category

        except Exception as e:
            self.logger.error(f"[update_tool_main_action] Erro: {e}", exc_info=True)
            return None

    def _filter_tools_by_reg(self):

        try:
            from .RegistryManager import RegistryManager

            lic_mgr = RegistryManager(ToolKey.SYSTEM)
            is_valid = lic_mgr.is_registry_valid()
            lic_info = lic_mgr.get_registry_info()
            current_level = lic_info.get("nivel", 0)
        except Exception:
            # RegistryManager não existe (versão sem módulo de licença)
            # → assume licença inválida e filtra premium
            is_valid = False
            current_level = 0

        before = len(self.tools)

        if not is_valid:
            # Sem licença válida → só ferramentas gratuitas
            self.tools = [tool for tool in self.tools if tool.registry_level is None]
        else:
            # Com licença válida → respeita o nível
            self.tools = [
                tool
                for tool in self.tools
                if tool.registry_level is None or current_level >= tool.registry_level
            ]

        filtered = before - len(self.tools)
        if filtered > 0:
            self.logger.info(
                f"{filtered} ferramentas  {is_valid}nível atual={current_level})"
            )
        else:
            self.logger.info("Nenhuma ferramenta filtrada")

    def _make_plugin_executor(self, module_path: str, run_func: str = "run"):
        """
        Gera um executor para ferramentas do tipo DIALOG.
        attr_name e log_name são inferidos automaticamente do module_path.

        Ex: '...plugins.ExportAllLayouts'
            → attr_name = 'export_all_layouts_dlg'
            → log_name  = 'Export All Layouts'
        """
        import re

        module_name = module_path.split(".")[-1]  # 'ExportAllLayouts'

        # CamelCase → snake_case para attr_name
        snake = re.sub(
            r"(?<!^)(?=[A-Z])", "_", module_name
        ).lower()  # 'export_all_layouts'
        attr_name = f"{snake}_dlg"  # 'export_all_layouts_dlg'

        # CamelCase → palavras separadas para log
        log_name = re.sub(r"(?<!^)(?=[A-Z])", " ", module_name)  # 'Export All Layouts'

        def executor():
            try:
                import importlib

                module = importlib.import_module(module_path, package=self._package)
                fn = getattr(module, run_func)
                self.logger.info(f"Abrindo diálogo: {log_name}")
                result = fn(self.iface)
                setattr(self, attr_name, result)
                self.logger.info(f"Diálogo {log_name} aberto com sucesso")
            except Exception as e:
                self.logger.error(f"Erro ao executar {log_name}: {str(e)}")
                QgisMessageUtil.bar_critical(
                    self.iface, f"Erro no plugin {log_name}:\n{str(e)}"
                )

        return executor

    def _make_provider_executor(self, algorithm_id: str, log_name: str):
        """
        Gera um executor para ferramentas do tipo PROCESSING.
        """

        def executor():
            try:
                import processing

                self.logger.info(
                    f"Abrindo diálogo do Processing para algoritmo: {log_name} ({algorithm_id})"
                )
                processing.execAlgorithmDialog(algorithm_id, {})
                self.logger.info(
                    f"Diálogo do {log_name} aberto com sucesso pelo provider"
                )
            except Exception as e:
                self.logger.error(
                    f"Erro ao executar {log_name} ({algorithm_id}): {str(e)}"
                )
                QgisMessageUtil.bar_critical(
                    self.iface, f"Erro ao abrir {log_name} no Processing:\n{str(e)}"
                )

        return executor

    # =====================================================
    # EXECUTAR: Obter Coordenadas ao Clicar no Mapa
    # =====================================================
    def run_coord_click(self):
        try:
            from ...plugins.CoordClickTool import CoordClickTool

            self.logger.info("Ativando ferramenta: Capturar Coordenadas")
            self.coord_click_tool = CoordClickTool(self.iface)
            self.iface.mapCanvas().setMapTool(self.coord_click_tool)
            self.logger.info("Ferramenta Capturar Coordenadas ativada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao ativar Capturar Coordenadas: {str(e)}")
            QgisMessageUtil.bar_critical(
                self.iface, f"Erro na ferramenta Capturar Coordenadas:{str(e)}"
            )
