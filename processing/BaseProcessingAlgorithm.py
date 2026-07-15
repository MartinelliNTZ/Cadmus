# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.core import QgsProcessingAlgorithm

import processing

from ..core.config.LogUtils import LogUtils
from ..resources.HtmlInstructionsProvider import HtmlInstructionsProvider
from ..resources.IconManager import IconManager as im
from ..resources.OtherFilesManager import OtherFilesManager
from ..utils.Preferences import Preferences
from ..utils.ToolKeys import ToolKey
from ..i18n.TranslationManager import STR


class GroupProcessing:
    def __init__(self, id=None, name=None, icon_path="cadmus_icon.ico"):
        self.id = id
        self.name = name
        self.icon_path = icon_path


class BaseProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    Base class for processing algorithms in the Cadmus plugin.
    """

    GROUP_ESTATISTICA = GroupProcessing(id="estatistica", name=STR.STATISTICS)
    GROUP_RASTER = GroupProcessing(id="raster", name=STR.RASTER)
    GROUP_VETORIAL = GroupProcessing(id="vetorial", name=STR.VECTOR)
    prefs = {}  # para armazenar preferências carregadas
    INSTRUCTIONS_FILE = None
    TOOL_KEY = None
    ALGORITHM_NAME = None
    ALGORITHM_DISPLAY_NAME = None
    ALGORITHM_GROUP = GROUP_VETORIAL
    ICON = "cadmus_icon.ico"

    # Constantes comuns de parâmetros booleano (reutilizáveis entre algoritmos)
    PARAM_OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"
    PARAM_DISPLAY_HELP = "DISPLAY_HELP"
    PARAM_OPEN_OUTPUT_FOLDER_LABEL = STR.OPEN_OUTPUT_FOLDER
    PARAM_DISPLAY_HELP_LABEL = STR.DISPLAY_HELP_FIELD

    def shortHelpString(self):
        if self.prefs.get("display_help", True):  # self.INSTRUCTIONS_FILE:
            html = HtmlInstructionsProvider(self.TOOL_KEY)
            return html.get_instructions(self.ALGORITHM_NAME)  # valor padrão genérico
        else:
            return

    def icon(self):
        icon_path = im.icon_path(self.ICON) if self.ICON else None
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def createInstance(self):
        return self.__class__()

    def name(self):
        if self.ALGORITHM_NAME:
            return self.ALGORITHM_NAME
        raise NotImplementedError(
            "Algoritmo precisa definir ALGORITHM_NAME ou override name()."
        )

    def displayName(self):
        if self.ALGORITHM_DISPLAY_NAME:
            return self.ALGORITHM_DISPLAY_NAME
        raise NotImplementedError(
            "Algoritmo precisa definir ALGORITHM_DISPLAY_NAME ou override displayName()."
        )

    def group(self):
        return (
            self.ALGORITHM_GROUP.name
            if self.ALGORITHM_GROUP
            else self.GROUP_VETORIAL.name
        )

    def groupId(self):
        return (
            self.ALGORITHM_GROUP.id if self.ALGORITHM_GROUP else self.GROUP_VETORIAL.id
        )

    def load_preferences(self):
        """Carrega preferências usando Preferences.load_tool_prefs e armazena em self.prefs. Retorna dict de preferências ou vazio se falhar."""
        if not self.TOOL_KEY:
            return {}
        try:
            self.prefs = Preferences.load_tool_prefs(self.TOOL_KEY)
        except Exception as e:
            LogUtils(
                tool=ToolKey.UNTRACEABLE,
                class_name=self.__class__.__name__,
                level=LogUtils.WARNING,
            ).warning(f"Falha ao carregar preferências de {self.TOOL_KEY}: {e}")
            return {}

    def save_preferences(self):
        """Salva self.prefs usando Preferences.save_tool_prefs. Espera que self.prefs já esteja atualizada."""
        if not self.TOOL_KEY:
            return
        if self.prefs is None:
            self.prefs = {}
        Preferences.save_tool_prefs(self.TOOL_KEY, self.prefs)

    def open_folder_in_explorer(self, folder_path):
        if folder_path and os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    # ------------------------------------------------------------------
    # Helpers comuns para feedback
    # ------------------------------------------------------------------

    @staticmethod
    def _push_banner(feedback, title: str, width: int = 50):
        """
        Exibe um banner estilizado no feedback do processing.

        Exemplo:
            self._push_banner(feedback, "CRIADOR DE MOSAICO RGB - CADMUS")
        """
        if feedback is None:
            return
        feedback.pushInfo("=" * width)
        feedback.pushInfo(title)
        feedback.pushInfo("=" * width)

    @staticmethod
    def _push_info_line(feedback, label: str, value: str):
        """Exibe uma linha info formatada no feedback."""
        if feedback is None:
            return
        feedback.pushInfo(f"{label}: {value}")

    @staticmethod
    def _apply_qml_style(feedback, logger, calc_output: str, qml_filename: str, context=None) -> bool:
        """
        Aplica um arquivo QML de estilo a um raster de saída via native:setlayerstyle.

        O caminho é resolvido automaticamente via OtherFilesManager (resources/qml/).

        Retorna True se o estilo foi aplicado com sucesso, False caso contrário.

        Parâmetros:
            feedback          - objeto feedback do processing
            logger            - logger da classe (LogUtils)
            calc_output (str) - caminho do raster de saída
            qml_filename (str)- nome do arquivo .qml (ex: "indice_gli_8_classes.qml")
            context           - contexto do processing (obrigatório para executar o algoritmo)
        """
        style_file_path = OtherFilesManager.style_path(qml_filename)

        if os.path.exists(style_file_path):
            style_params = {
                'INPUT': calc_output,
                'STYLE': style_file_path,
            }
            logger.debug(f"Aplicando estilo via native:setlayerstyle: {style_file_path}")
            processing.run(
                'native:setlayerstyle',
                style_params,
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )
            feedback.pushInfo(f"Estilo aplicado: {style_file_path}")
            return True
        else:
            feedback.pushInfo(
                f"Arquivo de estilo nao encontrado: {style_file_path}. "
                "O raster sera carregado sem estilo personalizado."
            )
            logger.warning(f"Arquivo de estilo nao encontrado: {style_file_path}")
            return False
