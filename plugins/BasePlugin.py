from .BaseDialog import BaseDialog
from qgis.PyQt.QtWidgets import (
    QDialog, QAction,QFileDialog, QLineEdit,QSizeGrip
)
from qgis.core import QgsVectorLayer, QgsWkbTypes, QgsApplication, QgsProject,QgsFeatureRequest
from qgis.PyQt.QtGui import QDesktopServices, QIcon, QCursor
from qgis.PyQt.QtCore import QUrl, Qt, QRect, QPoint

import os
from pathlib import Path
from typing import Optional
import time
from ..utils.FormatUtils import FormatUtils
from ..utils.vector.VectorLayerSource import VectorLayerSource
from ..core.config.LogUtils import LogUtils
from ..core.ui.WidgetFactory import WidgetFactory
from ..core.ui.info_dialog import InfoDialog
from ..utils.Preferences import load_tool_prefs, save_tool_prefs
from ..utils.ToolKeys import ToolKey
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ProjectUtils import  ProjectUtils
from ..utils.StringUtils import StringUtils




# -------------------------------------------------------------
#  PLUGIN BasePluginMTL
# -------------------------------------------------------------
class BasePluginMTL(BaseDialog):
    APP_NAME = StringUtils.APP_NAME
    TOOL_KEY = "base_plugin"  # Identificador padrão
    PLUGIN_NAME = ""
    prefs = None
    preferences = {}
    """Dicionario de status"""
    settings_preferences = {}
    """Preferências globais do aplicativo (Cadmus Settings)"""



    def init(self, tool_key="base_plugin", class_name="BasePluginMTL", load_settings_prefs=False, build_ui=True):
        """Inicializa o plugin base.    
        
        Parameters
        ----------
        tool_key : str
            Identificador único da ferramenta (padrão: base_plugin)
        class_name : str
            Nome da classe para logging (padrão: BasePluginMTL)
        load_settings_prefs : bool
            Se True, carrega preferências globais do Cadmus Settings (padrão: False)
        build_ui : bool
            Se True, constrói a interface de usuário (padrão: True)
        """
        self.TOOL_KEY = tool_key
        self.logger = LogUtils(tool=self.TOOL_KEY, class_name=class_name, level=LogUtils.DEBUG)
        self.preferences = {}
        self.preferences.clear()
        self.preferences = load_tool_prefs(self.TOOL_KEY)
        
        # Carregar preferências globais do Settings se solicitado
        if load_settings_prefs:
            self.logger.debug("Carregando preferências globais do Cadmus Settings")
            self.settings_preferences = load_tool_prefs(ToolKey.SETTINGS)
            self.logger.debug(f"Preferências globais carregadas: {list(self.settings_preferences.keys())}")
        else:
            self.settings_preferences = {}
        
        # Construir UI apenas se solicitado
        if build_ui:
            self.logger.debug("Construindo interface de usuário")
            self._build_ui()
            self.logger.debug("Carregando preferências do usuário")
            self._load_prefs()
            self.logger.info("Plugin inicializado com sucesso")
        else:
            self.logger.debug("Construção de UI desabilitada")

    """
    Classe base para plugins do Cadmus.

    Centraliza funcionalidades comuns aos plugins, como:
    - Criação de ações de menu
    - Recuperação da camada vetorial ativa
    - Validações básicas de edição e existência de feições

    Deve ser herdada por plugins específicos.
    """


    def _build_ui(
        self,
        title: Optional[str] = None,
        icon_path: Optional[str] = "cadmus_icon.ico",
        instructions_file: Optional[str] = "standard.md",
        enable_scroll: bool = True,
        **kwargs
    ):
        super()._build_ui(title=title, icon_path=icon_path, enable_scroll=enable_scroll)

        # instruções
        self.instructions_file = os.path.join(
            os.path.dirname(__file__),
            "..",
            "resources",
            "instructions",
            instructions_file
        )
        # Restaurar tamanho da janela se foi persistido
        self._restore_window_size()
        


    def _restore_window_size(self):
        """
        Restaura o tamanho da janela a partir das preferências.
        
        Se não houver tamanho persistido, usa 300x300 como padrão.
        """
        saved_width = self.preferences.get("window_width", 300)
        saved_height = self.preferences.get("window_height", 300)
        
        try:
            self.resize(int(saved_width), int(saved_height))
            self.logger.debug(f"Tamanho da janela restaurado: {saved_width}x{saved_height}")
        except Exception as e:
            self.logger.warning(f"Erro ao restaurar tamanho da janela: {e}, usando padrão")
            self.resize(300 , 300)

    def _persist_window_size(self):
        """
        Persiste o tamanho atual da janela nas preferências.
        
        Deve ser chamado em closeEvent() ou ao finalizar a execução.
        """
        width = self.width()
        height = self.height()
        
        self.preferences["window_width"] = width
        self.preferences["window_height"] = height
        
        self.logger.debug(f"Tamanho da janela persistido: {width}x{height}")

    def closeEvent(self, event):
        """
        Override do evento de fechamento para persistir preferências.
        
        Salva tamanho da janela e demais preferências antes de fechar.
        """
        self._persist_window_size()
        self._save_prefs()
        super().closeEvent(event)



    def start_stats(self, input_obj=None,modal_info = "YES",total_files=None):
        try:
            self.preferences["t0"] = time.time()

            # Reset transient counters
            self.preferences.pop("current_size", None)
            self.preferences.pop("current_features", None)
            self.preferences.pop("current_files", None)
            self.preferences.pop("eta", None)
            self.preferences.pop("eta_files", None)

            # Aggregates (ensure exist)
            self.preferences["total_bytes"] = self.preferences.get("total_bytes", 0)
            self.preferences["total_time"] = self.preferences.get("total_time", 0)
            self.preferences["total_features"] = self.preferences.get("total_features", 0)
            self.preferences["total_files"] = self.preferences.get("total_files", 0)
            self.preferences["total_time_features"] = self.preferences.get("total_time_features", 0)
            self.preferences["total_time_files"] = self.preferences.get("total_time_files", 0)

            # Metrics: files-based, features-based, or bytes-based
            if total_files is not None:
                # files metric
                self.preferences["current_files"] = int(total_files)
                avg_files = self.preferences.get("avg_speed_files", 0)
                if avg_files > 0:
                    self.preferences["eta_files"] = time.time() + (self.preferences["current_files"] / avg_files)
                else:
                    self.preferences["eta_files"] = 0
                TAM = f"{self.preferences['current_files']} files"
                msg = f"Iniciando: total files={self.preferences['current_files']}"
                if modal_info == "YES":
                    QgisMessageUtil.bar_info(self.iface, msg, "Estatisticas", duration=5)
                self.logger.info(msg)

            else:
                # fallback: if vector-like, use features; else use size(bytes)
                if input_obj is not None and hasattr(input_obj, "featureCount"):
                    try:
                        self.preferences["current_features"] = input_obj.featureCount()
                    except Exception:
                        self.preferences["current_features"] = 0
                    avg_feat = self.preferences.get("avg_speed_features", 0)
                    if avg_feat > 0 and self.preferences["current_features"] > 0:
                        self.preferences["eta"] = time.time() + (self.preferences["current_features"] / avg_feat)
                    TAM = f"{self.preferences.get('current_features',0)} feats"
                    msg = f"Iniciando: features={self.preferences.get('current_features',0)}"
                    if modal_info == "YES":
                        QgisMessageUtil.bar_info(self.iface, msg, "Estatisticas", duration=5)
                    self.logger.info(msg)
                else:
                    # treat as raster/file
                    self.preferences["current_size"] = ProjectUtils.compute_size(input_obj) if input_obj else 0
                    avg_bytes = self.preferences.get("avg_speed", 0)
                    if avg_bytes > 0 and self.preferences["current_size"] > 0:
                        self.preferences["eta"] = time.time() + (self.preferences["current_size"] / avg_bytes)
                    TAM = FormatUtils.bytes(self.preferences.get("current_size", 0))
                    msg = f"Iniciando: size={TAM}"
                    if modal_info == "YES":
                        QgisMessageUtil.bar_info(self.iface, msg, "Estatisticas", duration=5)
                    self.logger.info(msg)
        except Exception as e:
            self.logger.error(e)

    def finish_stats(self, modal_info = "YES", input_obj=None, start_time=None, total_files=None):
        self.logger.debug("finish_stats")
        try:
            if start_time is None:
                start_time = self.preferences.get("t0", time.time())
            end_time = time.time()
            total_time = end_time - start_time

            # files-based completion
            if total_files is not None:
                self.preferences["total_files"] = self.preferences.get("total_files", 0) + int(total_files)
                self.preferences["total_time_files"] = self.preferences.get("total_time_files", 0) + total_time
                if self.preferences["total_time_files"] > 0:
                    self.preferences["avg_speed_files"] = self.preferences.get("total_files", 0) / self.preferences.get("total_time_files", 1)

            # features-based completion (if input supports it)
            current_features = 0
            if input_obj is not None and hasattr(input_obj, "featureCount"):
                try:
                    current_features = input_obj.featureCount()
                except Exception:
                    current_features = self.preferences.get("current_features", 0)
            self.preferences["total_features"] = self.preferences.get("total_features", 0) + current_features
            self.preferences["total_time_features"] = self.preferences.get("total_time_features", 0) + total_time
            if self.preferences["total_time_features"] > 0:
                self.preferences["avg_speed_features"] = self.preferences.get("total_features", 0) / self.preferences.get("total_time_features", 1)

            # bytes/size-based completion
            current_size = ProjectUtils.compute_size(input_obj) if input_obj else self.preferences.get("current_size", 0)
            self.preferences["total_time"] = self.preferences.get("total_time", 0) + total_time
            self.preferences["total_bytes"] = self.preferences.get("total_bytes", 0) + current_size
            if self.preferences["total_time"] > 0:
                self.preferences["avg_speed"] = self.preferences.get("total_bytes", 0) / self.preferences.get("total_time", 1)

            # Log summary
            try:
                msg = (
                    f"Tempo total: {FormatUtils.time_interval(total_time)}\n"
                    f"Tamanho: {FormatUtils.bytes(current_size)}\n"
                    f"Feições: {current_features}\n"
                    f"Velocidade média(bytes/s): {FormatUtils.speed(self.preferences.get('avg_speed',0))}\n"
                    f"Velocidade média(feats/s): {FormatUtils.pretty(self.preferences.get('avg_speed_features',0))}\n"
                    f"Velocidade média(files/s): {FormatUtils.pretty(self.preferences.get('avg_speed_files',0))}\n"
                )
                self.logger.info(msg)
                if modal_info == "YES":
                    QgisMessageUtil.bar_success(self.iface, f"Estatistivas: {msg} ")
            except Exception:
                pass

            # atualizar agregados de features e limpar dados transitórios antes de persistir
            self.preferences["total_features"] = self.preferences.get("total_features", 0)

            # campos que não devem ser salvos entre execuções
            for key in ("t0", "current_size", "current_features", "eta", "avg_speed", "current_files", "eta_files"):
                self.preferences.pop(key, None)
            try:
                save_tool_prefs(self.TOOL_KEY, self.preferences)
            except Exception as se:
                self.logger.debug(f"Falha ao salvar prefs estatísticas: {se}")
        except Exception as e:
            self.logger.error(f"Erro: {e} Preferences: {self.preferences}")


    #@abstractmethod
    def execute_tool(self):
        """
        Método principal a ser implementado por cada plugin específico.
        Ele é chamado quando o usuário aciona a funcionalidade do plugin (ex: clica em um botão).
        Deve conter a lógica de execução do plugin.
        """
        pass

    def _on_pipeline_finished(self, context):    
        """Callback para quando a pipeline é finalizada com sucesso."""
        pass

    def _on_pipeline_error(self, errors):
        """Exibe um modal de erro genérico para a pipeline."""
        exc = errors[0] if errors else Exception("Erro desconhecido")

        QgisMessageUtil.modal_error(
            self.iface,
            f"Erro durante processamento:\n{exc}"
        )
    


    def create_action(self, icon_rel_path, text, callback):
        """Cria e registra uma ação no menu do plugin.

        Recebe: icon_rel_path (str), text (str), callback (callable).
        Retorna: QAction criado.
        Faz: cria a QAction, conecta o callback e adiciona ao menu.
        """
        self.logger.debug(f"Criando ação: {text}")
        icon_path = os.path.join(
            os.path.dirname(self.__class__.__module__.replace('.', os.sep)),
            icon_rel_path
        )

        action = QAction(icon_path, text, self.iface.mainWindow())
        action.triggered.connect(callback)

        self.iface.addPluginToMenu(self.MENU_NAME, action)
        self.actions.append(action)


    def show_info_dialog(self, title="📘 Instruções"):
        """Mostra diálogo de instruções do plugin.

        Recebe: title (str opcional).
        Retorna: None.
        Faz: abre `InfoDialog` com o arquivo de instruções, se existir.
        """
        self.logger.debug("Exibindo diálogo de informações")
        if hasattr(self, "instructions_file"):
            title = f"📘 Instruções – {self.PLUGIN_NAME}"
            InfoDialog(self.instructions_file, self, title).exec() 
            

   
              
    def apply_qml_style(
        self,
        layer: QgsVectorLayer,
        qml_path: str
    ) -> bool:
        """Aplica um arquivo QML como estilo na camada.

        Recebe: layer (QgsVectorLayer), qml_path (str).
        Retorna: bool (sucesso).
        Faz: valida entrada, carrega estilo e repinta a camada.
        """
        self.logger.debug(f"Aplicando estilo QML à camada: {layer.name() if isinstance(layer, QgsVectorLayer) else 'inválida'}. Caminho: {qml_path}")

        if not isinstance(layer, QgsVectorLayer):
            return False

        if not qml_path or not os.path.exists(qml_path):
            self.logger.debug(f"Caminho QML inválido ou não existe: {qml_path}")
            return False

        ok = layer.loadNamedStyle(qml_path)
        if isinstance(ok, tuple):
            ok = ok[0]

        if ok:
            layer.triggerRepaint()
            self.logger.debug(f"Estilo QML aplicado com sucesso")

        return bool(ok)
    
    def save_vector_layer(
        self,
        buffer_layer: QgsVectorLayer,
        output_path: Optional[str],
        save_to_folder: bool,
        output_name: str
    ) -> Optional[QgsVectorLayer]:
        """DEPRECADO: Use SaveVectorTask."""

        return VectorLayerSource.save_vector_layer(
            layer=buffer_layer,
            output_path=output_path,
            save_to_folder=save_to_folder,
            output_name=output_name,
            external_tool_key=self.TOOL_KEY
        )   
     
