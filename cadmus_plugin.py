# -*- coding: utf-8 -*-
from qgis.core import QgsApplication
from pathlib import Path
from .utils.ToolKeys import ToolKey
from .core.config.LogUtils import LogUtils
from .i18n.TranslationManager import STR
from .core.config.PluginBootstrap import PluginBootstrap
from .core.config.ToolRegistry import ToolRegistry
from .core.config.MenuManager import MenuManager

from .core.services.MrkDropHandler import MrkDropHandler


class CadmusPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = None
        self.logger = None
        self.tool_registry = None
        self.menu_manager = None
        self.mrk_drop_handler = None
        self.pyqt_signal_manager = None
        self.TOOL_KEY = ToolKey.SYSTEM

    # =====================================================
    # INICIAR GUI E PROCESSING
    # =====================================================
    def initGui(self):

        locale = QgsApplication.locale()  # ex: 'pt_BR'
        plugin_root = Path(__file__).resolve().parent

        # Inicializar componentes críticos via PluginBootstrap
        bootstrap = PluginBootstrap(self.iface)
        self.provider = bootstrap.bootstrap(plugin_root)

        # Criar logger para CadmusPlugin
        self.logger = LogUtils(
            tool=self.TOOL_KEY, class_name="Cadmus", level=LogUtils.DEBUG
        )

        self.logger.info("Plugin inicializado")
        self.logger.info(f"Locale: {locale}. TM.STR: {STR.APP_NAME}")

        self.mrk_drop_handler = MrkDropHandler(self.iface)
        self.iface.registerCustomDropHandler(self.mrk_drop_handler)
        self.logger.info("MRK drop handler registrado com sucesso")

        # Inicializar PyQtSignalManager para escutar sinais
        try:
            from .core.config.PyQtSignalManager import PyQtSignalManager

            self.pyqt_signal_manager = PyQtSignalManager(tool_key=self.TOOL_KEY)
            self.pyqt_signal_manager.start()
            self.logger.info("PyQtSignalManager inicializado e escutando sinais")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar PyQtSignalManager: {str(e)}")
            self.pyqt_signal_manager = None

        # -------------------------------
        # INTEGRAÇÃO COM NOVA ARQUITETURA
        # -------------------------------
        try:
            # Criar ToolRegistry com todas as ferramentas
            self.tool_registry = ToolRegistry(self.iface)
            tools = self.tool_registry.tools

            # Criar MenuManager para gerenciar menus e toolbar
            self.menu_manager = MenuManager(self.iface, tools, self.logger)

            # Criar menu principal e submenus
            self.menu_manager.create_menu()

            # Criar toolbar com botões dropdown
            self.logger.debug("Criando toolbar para o plugin")
            self.menu_manager.create_toolbar()

            # Popular menus com ferramentas ordenadas
            self.menu_manager.populate_menus()

            self.logger.info(
                f"Nova arquitetura integrada com sucesso. {self.menu_manager}. Registry{self.tool_registry.tools}."
            )
        except Exception as e:
            self.logger.error(f"Erro ao integrar nova arquitetura: {str(e)}")
            return

        # -------------------------

    # =====================================================
    # DESCARREGAR PLUGIN
    # =====================================================
    def unload(self):
        try:
            # Remover provider do Processing
            if self.provider:
                QgsApplication.processingRegistry().removeProvider(self.provider)
                self.logger.info("Processing Provider removido com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao remover Processing Provider: {str(e)}")

        try:
            if self.pyqt_signal_manager:
                self.pyqt_signal_manager.stop()
                self.logger.info("PyQtSignalManager descarregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao descarregar PyQtSignalManager: {str(e)}")

        try:
            if self.mrk_drop_handler:
                self.iface.unregisterCustomDropHandler(self.mrk_drop_handler)
                self.logger.info("MRK drop handler removido com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao remover MRK drop handler: {str(e)}")

        try:
            # Descarregar MenuManager (remove menus e toolbar)
            if self.menu_manager:
                self.menu_manager.unload()
                self.logger.info("MenuManager descarregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao descarregar MenuManager: {str(e)}")

        self.logger.info("Plugin Cadmus descarregado")
