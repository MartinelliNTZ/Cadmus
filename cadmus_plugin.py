# -*- coding: utf-8 -*-
import os
import sys
import traceback
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton, QWidgetAction
from pathlib import Path

from .utils.ToolKeys import ToolKey
from .utils.QgisMessageUtil import QgisMessageUtil
from .processing.provider import MTLProvider
from .core.config.LogCleanupUtils import LogCleanupUtils
from .core.config.LogUtils import LogUtils



# ========================================================================
# PROTEÇÃO GLOBAL CONTRA CRASHES
# ========================================================================
# Sistema para capturar e registrar erros não capturados em todo o plugin
_original_excepthook = sys.excepthook
_logger_global = None

def _install_global_error_handler():
    """Instala handler global para capturar exceções não tratadas."""
    global _logger_global
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Log em arquivo de sistema se possível
        try:
            if _logger_global is None:
                from .core.config.LogUtils import LogUtils
                _logger_global = LogUtils(tool="system", class_name="GlobalErrorHandler")
            
            error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            _logger_global.critical(
                f"UNCAUGHT EXCEPTION (possibly crash): {exc_type.__name__}: {str(exc_value)}",
                error_type=exc_type.__name__,
                traceback=error_msg
            )
        except Exception as log_error:
            # Se falhar em logar, apenas print
            print(f"GLOBAL ERROR HANDLER FAILED: {log_error}", file=sys.stderr)
            print(error_msg, file=sys.stderr)
        
        # Chamar handler original
        _original_excepthook(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception


class CadmusPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.menu = None
        self.toolbar = None
        self.actions = []
        self.provider = None
        self.logger = None
        self.TOOL_KEY = ToolKey.SYSTEM
    # =====================================================
    # INICIAR GUI E PROCESSING
    # =====================================================
    def initGui(self):
        # Instalar proteção global contra crashes
        #QgisMessageUtil.bar_info(self.iface, "Iniciando Cadmus...")
        _install_global_error_handler()
        
        plugin_root = Path(__file__).resolve().parent
        LogUtils.init(plugin_root)
        # mantém só os últimos 15 logs
        LogCleanupUtils.keep_last_n(plugin_root, keep=15)
        # Inicializar logger UMA VEZ como atributo da classe
        self.logger = LogUtils(tool=self.TOOL_KEY, class_name="Cadmus")
        self.logger.info("Plugin inicializado")
        self.logger.info("SYSTEM: Global error handler instalado para capturar crashes")
        # -------------------------
        # 1) ATIVAR PROCESSING PROVIDER
        # -------------------------
        try:
            self.provider = MTLProvider()
            QgsApplication.processingRegistry().addProvider(self.provider)
            self.logger.info("Processing Provider carregado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar Processing Provider: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface,f"Erro ao carregar provider. Erro: {e}")
        # -------------------------
        # 2) CRIAR TOOLBAR EXCLUSIVA
        # -------------------------
        try:
            self.toolbar = self.iface.addToolBar("Cadmus")
            self.toolbar.setObjectName("Cadmus_Toolbar")
            self.logger.debug("Toolbar Cadmus criada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar toolbar: {str(e)}")
            return

        # -------------------------
        # 3) MENU PRINCIPAL E SUBMENUS
        # -------------------------
        try:
            self.menu = QMenu("Cadmus", self.iface.mainWindow())
            self.menu.setObjectName("Cadmus")
            standard_menu = self.iface.firstRightStandardMenu()
            self.iface.mainWindow().menuBar().insertMenu(standard_menu.menuAction(), self.menu)
            self.menu.clear()
            self.logger.debug("Menu Cadmus criado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar menu principal: {str(e)}")
            return
        

    
     

        # Submenus        
        try:
            self.agriculture_menu = QMenu("Agricultura de Precisão", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "agriculture.ico"))
            self.agriculture_menu.setIcon(icon)
            self.layers_menu = QMenu("Camadas", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "layer.ico"))
            self.layers_menu.setIcon(icon)
            self.layouts_menu = QMenu("Layouts", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "layout.ico"))
            self.layouts_menu.setIcon(icon)
            self.raster_menu = QMenu("Raster", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "raster.ico"))
            self.raster_menu.setIcon(icon)
            self.system_menu = QMenu("Sistema", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "system.ico"))
            self.system_menu.setIcon(icon)
            self.vectors_menu = QMenu("Vetores", self.menu)
            icon = QIcon(os.path.join(os.path.dirname(__file__),"resources", "icons", "vector.ico"))
            self.vectors_menu.setIcon(icon)

            # Adiciona submenus ao menu principal
            self.menu.addMenu(self.agriculture_menu)
            self.menu.addMenu(self.layers_menu)
            self.menu.addMenu(self.layouts_menu)
            self.menu.addMenu(self.raster_menu)
            self.menu.addMenu(self.vectors_menu)
            self.menu.addMenu(self.system_menu)
            self.logger.debug("Submenus criados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar submenus: {str(e)}")
            return

        # -------------------------
        # 4) CONFIGURAÇÃO DAS AÇÕES (ORDEM NUMÉRICA)
        # -------------------------
        try:
            # 1-Export All Layouts
            export_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "export_icon.ico")
            self.action_export_all = QAction(QIcon(export_icon), "Exportar todos os Layouts", self.iface.mainWindow())
            self.action_export_all.triggered.connect(self.run_export_layouts)

            # 2-Replace in Layouts
            replace_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "replace_in_layouts.ico")
            self.action_replace_layouts = QAction(QIcon(replace_icon), "Substituir textos nos Layouts", self.iface.mainWindow())
            self.action_replace_layouts.triggered.connect(self.run_replace_layouts)

            # 3-Restart QGIS
            restart_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "restart_qgis.ico")
            self.action_restart_qgis = QAction(QIcon(restart_icon), "Salvar, Fechar e Reabrir Projeto", self.iface.mainWindow())
            self.action_restart_qgis.triggered.connect(self.run_restart_qgis)

            # 4-Carregar pasta de arquivos
            load_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "load_folder.ico")
            self.action_load_folder = QAction(QIcon(load_icon), "Carregar pasta de arquivos", self.iface.mainWindow())
            self.action_load_folder.triggered.connect(self.run_load_folder)

            # 5-Gerar Rastro Implemento
            gerar_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "gerar_rastro.ico")
            self.action_gerar_rastro = QAction(QIcon(gerar_icon), "Gerar Rastro Implemento", self.iface.mainWindow())
            self.action_gerar_rastro.triggered.connect(self.run_gerar_rastro)

            # 6-About Dialog
            about_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "about.ico")
            self.action_about_dialog = QAction(QIcon(about_icon), "Sobre o Cadmus", self.iface.mainWindow())
            self.action_about_dialog.triggered.connect(self.run_about_dialog)
            
            # 12-Logcat Tool
            logcat_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "logcat.ico")
            self.action_logcat = QAction(QIcon(logcat_icon), "Logcat - Viewer de Logs", self.iface.mainWindow())
            self.action_logcat.triggered.connect(self.run_logcat)
            
            # 13-Settings
            settings_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "system.ico")
            self.action_settings = QAction(QIcon(settings_icon), "Configurações", self.iface.mainWindow())
            self.action_settings.triggered.connect(self.run_settings)
            
            # 7-Capturar Coordenadas
            coord_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "coord.ico")
            self.action_coord_click = QAction(QIcon(coord_icon), "Capturar Coordenadas", self.iface.mainWindow())
            self.action_coord_click.triggered.connect(self.run_coord_click)
            
            
            # 8-Calcular campos vetoriais
            vector_field_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "vector_field.ico")
            self.action_vector_fields = QAction(QIcon(vector_field_icon), "Calcular Campos Vetoriais", self.iface.mainWindow())
            self.action_vector_fields.triggered.connect(self.run_vector_fields)      


            # 09-Obter coordenadas de drone
            drone_coord_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "drone_cordinates.ico")
            self.action_drone_coords = QAction(QIcon(drone_coord_icon), "Obter Coordenadas de Drone", self.iface.mainWindow())
            self.action_drone_coords.triggered.connect(self.run_drone_coords)
            
            # 10-Realizar multipart de todas as feições
            multipart_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "vector_multpart.ico")
            self.action_multpart = QAction(QIcon(multipart_icon), "Promover a multiparte", self.iface.mainWindow())
            self.action_multpart.triggered.connect(self.run_multpart)

            # 11-Copiar atributos entre camadas
            copy_atributes_icon = os.path.join(os.path.dirname(__file__),"resources", "icons", "copy_attributes.ico")
            self.action_copy_atributes = QAction(QIcon(copy_atributes_icon), "Copiar Atributos", self.iface.mainWindow())
            self.action_copy_atributes.triggered.connect(self.run_copy_atributes)
            
            self.logger.debug("Todas as ações criadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar ações: {str(e)}")
            return

        # -------------------------
        # 5) ADICIONAR AÇÕES AO MENU (ORDEM ALFABÉTICA)
        # -------------------------
        try:
            # Agricultura de Precisão
            self.agriculture_menu.addAction(self.action_gerar_rastro)
            self.agriculture_menu.addAction(self.action_drone_coords)

            # Camadas
            self.layers_menu.addAction(self.action_load_folder)

            # Layouts
            self.layouts_menu.addAction(self.action_export_all)
            self.layouts_menu.addAction(self.action_replace_layouts)

            # Sistema
            self.system_menu.addAction(self.action_restart_qgis)
            self.system_menu.addAction(self.action_logcat)
            self.system_menu.addAction(self.action_settings)

            # Vetores
            self.vectors_menu.addAction(self.action_coord_click)
            self.vectors_menu.addAction(self.action_vector_fields)

            # Menu principal
            self.menu.addAction(self.action_about_dialog)
            
            self.logger.debug("Ações adicionadas aos menus com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao adicionar ações aos menus: {str(e)}")
            return

        # -------------------------
        # 6) TOOLBAR
        # -------------------------
        try:
            # ==================================================
            # BOTÃO SISTEMA NA TOOLBAR (com dropdown)
            # ==================================================
            self._add_toolbar_dropdown(
                title="Sistema",
                main_action=self.action_restart_qgis,
                secondary_actions=[self.action_restart_qgis,
                                   self.action_logcat,
                                   self.action_settings,
                                   self.action_about_dialog]
            )       

            # ==================================================
            # BOTÃO LAYOUTS NA TOOLBAR (com dropdown)
            # ==================================================
            self._add_toolbar_dropdown(
                title="Layouts",

                main_action=self.action_export_all,#STARD
                #main_action=self.action_replace_layouts, #DEBUG
                secondary_actions=[ self.action_export_all,
                                    self.action_replace_layouts,
                                    ]
            )

            # ==================================================
            # BOTÃO CAMADAS NA TOOLBAR (com dropdown)
            # ==================================================
            self._add_toolbar_dropdown(
                title="Vetores",
                main_action=self.action_load_folder,
                secondary_actions=[self.action_load_folder]
            )
            # ==================================================
            # BOTÃO "VETORES" NA TOOLBAR (com dropdown)
            # ==================================================
            self._add_toolbar_dropdown(
                title="Vetores",
                main_action=self.action_vector_fields,#padrao
                #main_action=self.action_coord_click,#editavel para debug
                secondary_actions=[     self.action_vector_fields,
                                        self.action_coord_click,    
                                        self.action_copy_atributes,                                                         
                                        self.action_multpart,]
            )
            # ==================================================
            # BOTÃO "AGRICULTURA DE PRECISÃO" NA TOOLBAR (com dropdown)
            # ==================================================
            self._add_toolbar_dropdown(
                title="Agricultura de Precisão",
                main_action=self.action_drone_coords,
                #main_action=self.action_gerar_rastro,
                secondary_actions=[
                    self.action_drone_coords,
                    self.action_gerar_rastro]
            )        
            # ==================================================
            # BOTÃO "RASTER" NA TOOLBAR (com dropdown)
            # ==================================================

            self.toolbar.addSeparator()
            self.logger.debug("Botões de toolbar criados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar botões da toolbar: {str(e)}")
            return

        # Salva todas as ações para cleanup
        try:
            self.actions.extend([
                self.action_export_all,
                self.action_replace_layouts,
                self.action_restart_qgis,
                self.action_load_folder,
                self.action_gerar_rastro,
                self.action_about_dialog,
                self.action_logcat,
                self.action_settings,
                self.action_coord_click,
                self.action_vector_fields,
                self.action_drone_coords,
                self.action_multpart,
                self.action_copy_atributes
            ])
            self.logger.info("Cadmus: GUI inicializada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao salvar ações para cleanup: {str(e)}")


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
            # Remover ações do menu e toolbar
            for act in self.actions:
                self.iface.removePluginMenu("Cadmus", act)
                self.iface.removeToolBarIcon(act)
            self.logger.info("Ações removidas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao remover ações: {str(e)}")

        try:
            # Remover toolbar
            if self.toolbar:
                del self.toolbar
                self.logger.info("Toolbar removida com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao remover toolbar: {str(e)}")
        
        self.logger.info("Plugin Cadmus descarregado")
            
            
#===========================FERRAMENTAS INSTANTANEAS DE SISTEMA===================================================================
    # =====================================================
    # EXECUTAR: Restart QGIS
    # =====================================================
    def run_restart_qgis(self):
        try:
            from .plugins.RestartQgis import run_restart_qgis
            self.logger.info("Iniciando plugin: Restart QGIS")
            run_restart_qgis(self.iface)
            self.logger.info("Plugin Restart QGIS executado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Restart QGIS: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Restart QGIS:\n{str(e)}")

#===========================FERRAMENTAS INSTANTANEAS===================================================================
    # =====================================================
    # EXECUTAR: Calcular Campos Vetoriais
    # =====================================================
    def run_vector_fields(self):
        try:
            from .plugins.VectorFieldsCalculationPlugin import VectorFieldsCalculationPlugin
            self.logger.info("Iniciando plugin: Calcular Campos Vetoriais")
            # manter referência viva
            self.vector_field_plugin = VectorFieldsCalculationPlugin(self.iface)
            self.vector_field_plugin.run_vector_field()
            self.logger.info("Plugin Calcular Campos Vetoriais executado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Calcular Campos Vetoriais: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Calcular Campos Vetoriais:\n{str(e)}")
        
    # =====================================================
    # EXECUTAR: Converter para Multipart
    # =====================================================
    def run_multpart(self):
        try:
            from .plugins.VectorMultipartPlugin import VectorMultipartPlugin
            self.logger.info("Iniciando plugin: Converter para Multipart")
            # manter referência viva
            self.vector_multpart_plugin = VectorMultipartPlugin(self.iface)
            self.vector_multpart_plugin.run_multpart()
            self.logger.info("Plugin Converter para Multipart executado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Converter para Multipart: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Converter para Multipart:\n{str(e)}")
 
#===========================FERRAMENTAS INSTANTANEA COM JANELA DE RESULTADOS=======================================================================
       
    # =====================================================
    # EXECUTAR: Obter Coordenadas ao Clicar no Mapa
    # =====================================================
    def run_coord_click(self):
        try:
            from .plugins.coord_click_tool import CoordClickTool
            self.logger.info("Ativando ferramenta: Capturar Coordenadas")
            self.coord_click_tool = CoordClickTool(self.iface)
            self.iface.mapCanvas().setMapTool(self.coord_click_tool)
            self.logger.info("Ferramenta Capturar Coordenadas ativada com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao ativar Capturar Coordenadas: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro na ferramenta Capturar Coordenadas:\n{str(e)}")
        

#===========================FERRAMENTAS DE JANELA COM SAIDA QGIS=======================================================================
    # =====================================================
    # EXECUTAR: Export All Layouts
    # =====================================================
    def run_export_layouts(self):
        try:
            from .plugins.ExportAllLayouts import run_export_all_layouts
            self.logger.info("Abrindo diálogo: Exportar todos os Layouts")
            self.export_dlg = run_export_all_layouts(self.iface)
            self.logger.info("Diálogo Exportar Layouts fechado")
        except Exception as e:
            self.logger.error(f"Erro ao executar Exportar Layouts: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Exportar Layouts:\n{str(e)}")

    # =====================================================
    # EXECUTAR: Gerar Rastro Implemento (painel)
    # =====================================================
    def run_gerar_rastro(self):
        try:
            from .plugins.GenerateTrailPlugin import run_gerar_rastro
            self.logger.info("Abrindo diálogo: Gerar Rastro Implemento")
            self.gerar_rastro_dlg = run_gerar_rastro(self.iface)
            self.logger.info("Diálogo Gerar Rastro Implemento aberto com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Gerar Rastro Implemento: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Gerar Rastro Implemento:\n{str(e)}")
    # =====================================================
    # EXECUTAR: Logcat Tool
    # =====================================================
    def run_logcat(self):
        """
        Abre o Logcat com proteção MÁXIMA contra crashes.
        Qualquer erro será capturado e registrado em arquivo de log.
        """
        try:
            self.logger.info("=" * 60)
            self.logger.info("LOGCAT: Iniciando abertura de diálogo (PROTEGIDO)")
            
            # Import isolado
            try:
                from .plugins.logcat.logcat_plugin import run
                self.logger.info("LOGCAT: Módulo logcat_plugin importado")
            except ImportError as import_err:
                error_msg = f"LOGCAT: Erro ao importar logcat_plugin: {str(import_err)}"
                self.logger.critical(error_msg)
                QgisMessageUtil.bar_critical(self.iface, f"Erro de importação:\n{str(import_err)}")
                return
            
            self.logger.info("Abrindo diálogo: Logcat - Viewer de Logs")
            
            # Execução com proteção adicional
            try:
                self.logcat_dlg = run(self.iface)
                self.logger.info("LOGCAT: Diálogo aberto com sucesso (sem crashes detectados)")
                self.logger.info("=" * 60)
            except Exception as run_error:
                # Erro na execução do Logcat
                error_msg = f"LOGCAT: Erro ao executar logcat_plugin.run(): {str(run_error)}"
                self.logger.critical(error_msg)
                error_trace = traceback.format_exc()
                self.logger.critical(f"Stack trace:\n{error_trace}")
                QgisMessageUtil.bar_critical(self.iface, f"Erro ao abrir Logcat:\n{str(run_error)}")
                self.logger.info("=" * 60)
                
        except Exception as outer_error:
            # Erro na própria função run_logcat
            error_msg = f"LOGCAT: Erro CRÍTICO em run_logcat(): {str(outer_error)}"
            try:
                self.logger.critical(error_msg)
                error_trace = traceback.format_exc()
                self.logger.critical(f"Stack trace:\n{error_trace}")
                self.logger.info("=" * 60)
            except:
                print(error_msg, file=sys.stderr)
            
            # Mensagem ao usuário
            try:
                QgisMessageUtil.bar_critical(self.iface, f"Erro crítico no Logcat:\n{str(outer_error)}")
            except:
                pass



   
    # =====================================================
    # EXECUTAR: Obter Coordenadas de Drone
    # =====================================================
    def run_drone_coords(self):
        try:
            from .plugins.DroneCoordinates import run_drone_cordinates
            self.logger.info("Abrindo diálogo: Obter Coordenadas de Drone")
            self.drone_cordinates_dlg = run_drone_cordinates(self.iface)
            self.logger.info("Diálogo Obter Coordenadas de Drone aberto com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Obter Coordenadas de Drone: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Obter Coordenadas de Drone:\n{str(e)}")


       


#===========================FERRAMENTAS DE JANELA SEM SAIDAS=======================================================================
    # =====================================================
    # EXECUTAR: Replace Text in Layouts
    # =====================================================
    def run_replace_layouts(self):
        try:
            from .plugins.ReplaceInLayouts import run_replace_in_layouts
            self.logger.info("Abrindo diálogo: Substituir textos nos Layouts")
            self.replace_layouts_dlg = run_replace_in_layouts(self.iface)
            self.logger.info("Diálogo Substituir Layouts aberto com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Substituir Layouts: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Substituir Layouts:\n{str(e)}")


    # =====================================================
    # EXECUTAR: Load Folder Layers
    # =====================================================
    def run_load_folder(self):
        try:
            from .plugins.LoadFolderLayers import run_load_folder_layers
            self.logger.info("Iniciando plugin: Carregar pasta de arquivos")
            self.load_folder_dlg = run_load_folder_layers(self.iface)
            self.logger.info("Plugin Carregar pasta de arquivos executado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Carregar pasta de arquivos: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Carregar pasta:\n{str(e)}")

 
    # =====================================================
    # EXECUTAR: About Dialog
    # =====================================================
    def run_about_dialog(self):
        try:
            from .plugins.about_dialog import run_about_dialog
            self.logger.info("Abrindo diálogo: Sobre o Cadmus")
            run_about_dialog(self.iface)
            self.logger.info("Diálogo Sobre Cadmus fechado")
        except Exception as e:
            self.logger.error(f"Erro ao executar Sobre o Cadmus: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro ao abrir Sobre Cadmus:\n{str(e)}")
        
    # =====================================================
    # EXECUTAR: Copiar Atributos entre Camadas
    # =====================================================
    def run_copy_atributes(self):
        try:
            from .plugins.CopyAttributesPlugin import run_copy_attributes
            self.logger.info("Abrindo diálogo: Copiar Atributos")
            self.copy_attributes_dlg = run_copy_attributes(self.iface)
            self.logger.info("Diálogo Copiar Atributos aberto com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Copiar Atributos: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no plugin Copiar Atributos:\n{str(e)}")

        


        
    
        
        
    def _add_toolbar_dropdown(self, title, main_action, secondary_actions=None, icon=None, separator=True):
        """
        Cria um botão dropdown na toolbar com ações principais e secundárias.
        
        :param title: Texto do botão
        :param main_action: QAction que será a ação principal (clicando no botão)
        :param secondary_actions: lista de QActions adicionais no menu dropdown
        :param icon: QIcon opcional para o botão (se None, usa ícone da ação principal)
        :param separator: bool, adiciona separador após o botão
        :return: QWidgetAction criado e adicionado à toolbar
        """
        if secondary_actions is None:
            secondary_actions = []

        # 1️⃣ Criar o botão principal
        button = QToolButton()
        button.setText(title)
        button.setIcon(icon or main_action.icon())

        # 2️⃣ Criar menu dropdown
        menu = QMenu(self.iface.mainWindow())
        menu.addAction(main_action)  # ação principal no topo
        for act in secondary_actions:
            menu.addAction(act)

        # 3️⃣ Configurar o botão
        button.setMenu(menu)
        button.setDefaultAction(main_action)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        #button.clicked.connect(main_action.trigger)

        # 4️⃣ Transformar em widgets e adicionar à toolbar
        widget_action = QWidgetAction(self.toolbar)
        widget_action.setDefaultWidget(button)
        self.toolbar.addAction(widget_action)

        # 5️⃣ Separador opcional
        if separator:
            self.toolbar.addSeparator()

    # =====================================================
    # EXECUTAR: Configurações
    # =====================================================
    def run_settings(self):
        try:
            from .plugins.SettingsPlugin import run_settings
            self.logger.info("Abrindo diálogo: Configurações")
            self.settings_dlg = run_settings(self.iface)
            self.logger.info("Diálogo de configurações aberto com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao executar Configurações: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro no diálogo de Configurações:\n{str(e)}")
