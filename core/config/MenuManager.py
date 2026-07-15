# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QMenu, QAction, QToolBar
from ...resources.IconManager import IconManager as im
from ...resources.widgets.system.DropdownToolButton import DropdownToolButton
from .LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey
from ...utils.Preferences import Preferences
from ...utils.StringManager import StringManager


class MenuManager:
    TOOLBAR_VISIBILITY_PREF_KEY = "toolbar_category_visibility"
    _instance = None  # Instância única para acesso global interno

    @classmethod
    def toolbar_category_options(cls):
        """Retorna as categorias configuráveis da toolbar."""
        return dict(StringManager.MENU_CATEGORIES)

    @classmethod
    def get_instance(cls):
        """Retorna a instância ativa do MenuManager."""
        return cls._instance

    @classmethod
    def default_toolbar_category_visibility(cls):
        """Retorna o estado padrão da toolbar por categoria."""
        return {category: True for category in cls.toolbar_category_options()}

    @classmethod
    def normalize_toolbar_category_visibility(cls, visibility):
        """Normaliza o estado salvo para o conjunto atual de categorias."""
        merged = cls.default_toolbar_category_visibility()
        if not isinstance(visibility, dict):
            return merged

        for category in merged:
            if category in visibility:
                merged[category] = bool(visibility.get(category))

        return merged

    def __init__(self, iface, tools=None, logger=None):
        self.iface = iface
        self.menu = None
        self.submenus = {}
        self.toolbar = None
        self.tools = tools if tools is not None else []
        self.TOOLKEY = ToolKey.SYSTEM
        self.logger = LogUtils(tool=self.TOOLKEY, class_name="MenuManager")
        self._create_actions_for_tools()
        self.prefs = Preferences.load_tool_prefs(self.TOOLKEY)
        self.toolbar_category_visibility = self.normalize_toolbar_category_visibility(
            self.prefs.get(self.TOOLBAR_VISIBILITY_PREF_KEY)
        )
        self.logger.debug(
            f"MenuManager: {self.menu}. Tools: {self.tools}. "
            f"Toolbar: {self.toolbar}. "
            f"Toolbar categories: {self.toolbar_category_visibility}."
        )
        # Armazenar referência da instância para reconstrução dinâmica
        MenuManager._instance = self

    def _create_actions_for_tools(self):
        """Cria QActions para todas as ferramentas e conecta executores."""
        for tool in self.tools:
            tool.action = QAction(tool.icon, tool.name, self.iface.mainWindow())
            tool.action.setToolTip(tool.tooltip or tool.name)
            tool.action.setData(tool)
            if tool.executor is not None:
                tool.action.triggered.connect(tool.executor)
        self.logger.debug("Actions criadas para todas as ferramentas")

    def create_menu(self):
        self.logger.debug("Iniciando criação do menu")
        self.menu = QMenu("Cadmus", self.iface.mainWindow())
        self.menu.setObjectName("Cadmus")
        standard_menu = self.iface.firstRightStandardMenu()
        self.iface.mainWindow().menuBar().insertMenu(
            standard_menu.menuAction(), self.menu
        )

        # Mapeamento de categoria para ícone
        category_icons = {
            "SYSTEM": im.icon(im.SYSTEM),
            "LAYOUTS": im.icon(im.LAYOUT),
            "FOLDER": im.icon(im.LAYER),  # Usar ícone de layer para folder
            "VECTOR": im.icon(im.VECTOR),
            "AGRICULTURE": im.icon(im.AGRICULTURE),
            "RASTER": im.icon(im.RASTER),
        }
        self.logger.debug(
            f"Criando submenus para cada categoria: {list(category_icons.keys())}"
        )
        for category, label in StringManager.MENU_CATEGORIES.items():
            submenu = QMenu(label, self.menu)
            if category in category_icons:
                submenu.setIcon(category_icons[category])
            self.submenus[category] = submenu
            self.menu.addMenu(submenu)
            self.logger.debug(
                f"Submenu '{category}' criado com ícone: {category_icons.get(category)}"
            )

        self.logger.debug("Menus principais criados")

    def create_toolbar(self):
        self.logger.debug(f"Iniciando toolbar:Total de ferramentas: {len(self.tools)}")

        existing_toolbar = self.iface.mainWindow().findChild(QToolBar, "Cadmus_Toolbar")
        if existing_toolbar:
            self.logger.warning(
                "Toolbar Cadmus existente encontrada antes de criar nova toolbar; removendo para evitar duplicação"
            )
            try:
                self.iface.mainWindow().removeToolBar(existing_toolbar)
                existing_toolbar.hide()
                existing_toolbar.setParent(None)
                existing_toolbar.deleteLater()
            except Exception as e:
                self.logger.error(f"Erro ao remover toolbar existente: {e}")

        self.toolbar = QToolBar("Cadmus", self.iface.mainWindow())
        self.toolbar.setObjectName("Cadmus_Toolbar")
        self.iface.addToolBar(self.toolbar)
        self.logger.debug(
            f"Toolbar criada e adicionada ao QGIS: {self.toolbar.objectName()}"
        )

        # Coletar todos os dropdown buttons por categoria
        dropdown_buttons = []

        for category in StringManager.MENU_CATEGORIES:
            self.logger.debug(f"Verificando categoria {category}")
            if not self.toolbar_category_visibility.get(category, True):
                self.logger.debug(
                    f"Categoria {category} desabilitada nas preferências da toolbar"
                )
                continue

            all_tools_in_category = [t for t in self.tools if t.category == category]
            self.logger.debug(
                f"Total de ferramentas na categoria {category}: {len(all_tools_in_category)}"
            )

            main_tools = [
                t
                for t in self.tools
                if t.category == category and t.main_action and t.show_in_toolbar
            ]
            self.logger.debug(f"Main tools na categoria {category}: {len(main_tools)}")

            secondary_tools = [
                t
                for t in self.tools
                if t.category == category and not t.main_action and t.show_in_toolbar
            ]
            self.logger.debug(
                f"Secondary tools na categoria {category}: {len(secondary_tools)}"
            )

            if not main_tools:
                self.logger.debug(
                    f"Pulando categoria {category} - nenhum main_tool encontrado"
                )
                continue

            main_tool = main_tools[0]
            self.logger.debug(
                f"Criando dropdown para categoria {category} com main_tool: {main_tool.name}"
            )
            secondary_actions = [
                t.action for t in sorted(secondary_tools, key=lambda x: x.order)
            ]
            self.logger.debug(f"Secondary actions: {len(secondary_actions)}")

            dropdown = DropdownToolButton(
                iface=self.iface,
                title=main_tool.name,
                main_action=main_tool.action,
                secondary_actions=secondary_actions,
                icon=main_tool.icon,  # Adicionado ícone
            )
            self.logger.debug(
                f"Dropdown criado com text: {dropdown.text() if hasattr(dropdown, 'text') else 'None'}"
            )
            dropdown_buttons.append(dropdown)

        # TESTE: Adicionar main_actions diretamente sem DropdownToolButton
        if dropdown_buttons:
            self.logger.debug(
                f"Adicionando {len(dropdown_buttons)} botões dropdown à toolbar"
            )
            for button in dropdown_buttons:
                self.logger.debug(f"Adicionando botão: {button.text()}")
                self.toolbar.addWidget(button)
                self.logger.debug(f"Botão '{button.text()}' adicionado à toolbar")
                # Adicionar separador após cada botão, exceto o último
                if button != dropdown_buttons[-1]:
                    self.toolbar.addSeparator()
        else:
            # Fallback: adicionar main_actions diretamente
            self.logger.warning(
                "Nenhum botão dropdown criado, tentando adicionar main_actions diretamente"
            )
            for category in StringManager.MENU_CATEGORIES:
                if not self.toolbar_category_visibility.get(category, True):
                    continue
                main_tools = [
                    t
                    for t in self.tools
                    if t.category == category and t.main_action and t.show_in_toolbar
                ]
                if main_tools:
                    main_tool = main_tools[0]
                    self.logger.debug(
                        f"Adicionando main_action diretamente: {main_tool.name}"
                    )
                    self.toolbar.addAction(main_tool.action)
                    self.toolbar.addSeparator()

    def populate_menus(self):
        # Ordenar ferramentas por order dentro de cada categoria
        for category in StringManager.MENU_CATEGORIES:
            if category not in self.submenus:
                continue
            sorted_tools = sorted(
                [t for t in self.tools if t.category == category], key=lambda x: x.order
            )
            for tool in sorted_tools:
                self.submenus[category].addAction(tool.action)
        self.logger.debug("Submenus populados com ferramentas (ordenadas)")

    def _refresh_tool_main_actions(self):
        """
        Sincroniza main_action das tools com ToolRegistry.
        Requisita ToolList (não Preferences).
        """
        from .ToolRegistry import ToolRegistry

        tool_registry = ToolRegistry.get_instance()
        if tool_registry is None:
            self.logger.error(
                "[_refresh_tool_main_actions] ToolRegistry não inicializado!"
            )
            return

        # Requisitar ToolList atualizada
        updated_tools = tool_registry.get_tools()
        updated_tools_dict = {t.tool_key: t for t in updated_tools}

        # Sincronizar main_action
        for tool in self.tools:
            updated_tool = updated_tools_dict.get(tool.tool_key)
            if updated_tool:
                tool.main_action = updated_tool.main_action

        self.logger.debug("[_refresh_tool_main_actions] ✓ Main_actions sincronizados")

    def reconstruct_toolbar(self):
        """Remove e reconstrói toolbar com estados atualizados."""
        self.logger.debug("[reconstruct_toolbar] Reconstruindo toolbar")

        # Remover toolbar anterior se existe
        if self.toolbar:
            try:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.hide()
                self.toolbar.setParent(None)
                self.toolbar.deleteLater()
            except Exception as e:
                self.logger.error(
                    f"Erro ao remover toolbar anterior durante reconstrução: {e}"
                )
            finally:
                self.toolbar = None

        # Recarregar visibilidade de categorias
        self.prefs = Preferences.load_tool_prefs(self.TOOLKEY)
        self.toolbar_category_visibility = self.normalize_toolbar_category_visibility(
            self.prefs.get(self.TOOLBAR_VISIBILITY_PREF_KEY)
        )

        # Sincronizar states das tools com ToolRegistry
        self._refresh_tool_main_actions()

        # Recriar toolbar
        self.create_toolbar()
        self.logger.info("[reconstruct_toolbar] ✓ Toolbar reconstruída")

    def unload(self):
        # Remover ações do menu
        for tool in self.tools:
            if tool.action:
                self.iface.removePluginMenu("Cadmus", tool.action)

        # Remover menu principal
        if self.menu:
            self.iface.mainWindow().menuBar().removeAction(self.menu.menuAction())
            # Importante: deletar o menu após remover
            self.menu.deleteLater()
            self.menu = None

        # Remover toolbar - MÉTODO CORRETO
        if self.toolbar:
            try:
                self.iface.mainWindow().removeToolBar(self.toolbar)
                self.toolbar.hide()
                self.toolbar.setParent(None)
                self.toolbar.deleteLater()
            except Exception as e:
                self.logger.error(f"Erro ao remover toolbar durante unload: {e}")
            finally:
                self.toolbar = None

        self.submenus.clear()
        self.logger.debug("MenuManager unloaded")
