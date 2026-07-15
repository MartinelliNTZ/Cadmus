# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import Qt
from ..core.config.LogUtils import LogUtils
from .BaseDialog import BaseDialog
from ..core.ui.WidgetFactory import WidgetFactory
from ..utils.ToolKeys import ToolKey
from ..i18n.TranslationManager import STR


def _qt_text_browser_interaction():
    """Compatibilidade Qt5/Qt6: retorna TextBrowserInteraction."""
    try:
        return Qt.TextInteractionFlag.TextBrowserInteraction
    except AttributeError:
        return Qt.TextBrowserInteraction


class AboutDialog(BaseDialog):

    def __init__(self, iface):
        self.iface = iface
        try:
            super().__init__(iface.mainWindow())

            self.logger = LogUtils(
                tool=ToolKey.ABOUT_DIALOG,
                class_name=self.__class__.__name__,
                level=LogUtils.DEBUG,
            )
            self.logger.debug("Inicializando AboutDialog")

            self.setWindowTitle(STR.ABOUT_CADMUS)
            self._build_ui(
                title=STR.ABOUT_CADMUS, enable_scroll=False, minimum_size=(420, 520)
            )
            self.logger.debug("AboutDialog _build_ui concluído")

            lbl_title = WidgetFactory.create_label(
                text=f"<h2>{STR.APP_NAME}</h2>",
                bold=False,
                word_wrap=True,
                parent=self,
                text_format=Qt.TextFormat.RichText,
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
            self.layout.addWidget(lbl_title)
            self.logger.debug("Título adicionado")

            info_text = self.tr(
                f"<b>{STR.VERSION}:</b> 3.0.0.2.2<br>"
                f"<b>{STR.UPDATED_ON}:</b> 15 / 07 / 2026<br>"
                f"<b>{STR.CREATED_ON}:</b> 9 / 12 / 2024<br>"
                f"<b>{STR.CREATOR}:</b> MTL Agricultura e Tecnologia<br>"
                f"<b>{STR.LOCATION}:</b> Palmas - Tocantins - Brasil<br>"
                '<b>Site:</b> <a href="https://github.com/MartinelliNTZ/Cadmus">github.com/MartinelliNTZ/Cadmus</a>'
            )

            lbl_info = WidgetFactory.create_label(
                text=info_text,
                bold=False,
                word_wrap=True,
                parent=self,
                text_format=Qt.TextFormat.RichText,
                text_interaction_flags=_qt_text_browser_interaction(),
                open_external_links=True,
                alignment=Qt.AlignmentFlag.AlignCenter,
            )
            self.layout.addWidget(lbl_info)
            self.logger.debug("Informações adicionadas")

            # Social icons row
            from ..resources.IconManager import IconManager as IM
            from qgis.PyQt.QtWidgets import QHBoxLayout, QPushButton
            from qgis.PyQt.QtGui import QIcon
            from qgis.PyQt.QtCore import QSize
            import webbrowser

            social_links = [
                ("GitHub", IM.GITHUB, "https://github.com/MartinelliNTZ"),
                (
                    "LinkedIn",
                    IM.LINKEDIN,
                    "https://www.linkedin.com/in/matheus-martinelli-a82149108",
                ),
                (
                    "Instagram",
                    IM.INSTAGRAM,
                    "https://www.instagram.com/matheusmartinelli00",
                ),
                ("E-mail", IM.EMAIL, "mailto:martinelli.matheus11@gmail.com"),
                (
                    "Buy Me a Coffee",
                    IM.BUY_ME_A_COFFEE,
                    "https://buymeacoffee.com/martinelliNTZ",
                ),
            ]

            social_layout = QHBoxLayout()
            social_layout.setSpacing(10)
            social_layout.setContentsMargins(0, 8, 0, 4)
            social_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            for name, icon_file, url in social_links:
                icon_path = os.path.join(
                    os.path.dirname(__file__), "..", "resources", "icons", icon_file
                )
                if os.path.exists(icon_path):
                    btn = QPushButton(parent=self)
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(32, 32))
                    btn.setToolTip(name)
                    btn.setFixedSize(40, 40)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.setFlat(True)
                    btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
                    social_layout.addWidget(btn)

            self.layout.addLayout(social_layout)
            self.logger.debug("Ícones sociais adicionados")

            close_layout, close_button = WidgetFactory.create_simple_button(
                text=STR.CLOSE,
                parent=self,
                separator_top=True,
                separator_bottom=False,
            )
            close_button.clicked.connect(self.close)
            self.layout.addLayout(close_layout)
            self.logger.debug("Botão Fechar adicionado")

            self.logger.debug("AboutDialog UI construída com sucesso")
        except Exception as ex:
            if hasattr(self, "logger") and self.logger:
                self.logger.error(f"AboutDialog falhou na inicialização: {ex}")
            else:
                print(f"AboutDialog falhou na inicialização: {ex}")
            raise


def run(iface):
    dlg = AboutDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
