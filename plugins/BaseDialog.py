# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QDialog, QSizeGrip

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
import os
from typing import Optional
from ..core.ui.WidgetFactory import WidgetFactory


# Compatibilidade Qt5/Qt6: Qt5 usa Qt.{attr}, Qt6 usa Qt.WindowType.{attr}
def _qt_window_type(name):
    try:
        return getattr(Qt.WindowType, name)
    except AttributeError:
        return getattr(Qt, name)


def _qt_widget_attr(name):
    try:
        return getattr(Qt.WidgetAttribute, name)
    except AttributeError:
        return getattr(Qt, name)


class BaseDialog(QDialog):
    """Base para diálogos, com métodos comuns e integração com iface e logger."""

    layout = None
    logger = None

    def _build_ui(
        self,
        title: Optional[str] = None,
        icon_path: Optional[str] = "cadmus_icon.ico",
        enable_scroll: bool = True,
        minimum_size=(300, 300),
        **kwargs,
    ):
        """Constrói a interface do plugin.
        Recebe: title (str|None), icon_path (str), instructions_file (str), enable_scroll (bool).
        ARQUITETURA (MainLayout encapsula scroll):
        - MainLayout cria ScrollWidget internamente se enable_scroll=True
        - Plugin apenas atribui self.layout = WidgetFactory.create_main_layout()
        - Responsabilidade única: MainLayout gerencia scroll, plugin usa add_items()
        """
        if title is not None:
            self.PLUGIN_NAME = title
        self.set_layout(
            enable_scroll=enable_scroll,
            icon_path=icon_path,
            title=self.PLUGIN_NAME,
            minimum_size=minimum_size,
        )

    def set_layout(
        self,
        enable_scroll=True,
        icon_path=None,
        title="Cadmus",
        minimum_size=(300, 300),
    ):
        """Define o layout principal do plugin."""
        self.logger.debug(f"Construindo UI para plugin: {self.PLUGIN_NAME}")
        self.layout = WidgetFactory.create_main_layout(
            self, title=title, enable_scroll=enable_scroll, icon_path="cadmus_icon.png"
        )
        # Garantir que o MainLayout seja sempre criado. Usar PLUGIN_NAME como fallback.
        self.setWindowFlags(
            _qt_window_type("Dialog") | _qt_window_type("FramelessWindowHint")
        )
        self.setAttribute(_qt_widget_attr("WA_TranslucentBackground"), True)
        # Tamanho mínimo padrão: 300x300 (persistido em preferências)
        self.setMinimumSize(*minimum_size)
        # Size grip (resize visual indicator)
        self.size_grip = QSizeGrip(self.layout._frame)
        self.size_grip.setFixedSize(16, 16)
        self.layout.addWidget(
            self.size_grip,
            alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
        )
        # Ícone nao ta funcionando, talvez por causa do frameless. Tentar setar ícone do aplicativo como fallback
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "resources", "icons", icon_path
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            self.logger.debug(f"Ícone carregado de: {icon_path}")

    def mousePressEvent(self, event):
        """Delega evento de mouse para detecção de bordas e início de resize do MainLayout."""
        if self.layout and hasattr(self.layout, "handle_mouse_press"):
            if self.layout.handle_mouse_press(event):
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Delega evento de mouse para atualização de cursor e resize do MainLayout."""
        if self.layout and hasattr(self.layout, "handle_mouse_move"):
            self.layout.handle_mouse_move(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Delega evento de mouse para finalização de resize do MainLayout."""
        if self.layout and hasattr(self.layout, "handle_mouse_release"):
            if self.layout.handle_mouse_release(event):
                return
        super().mouseReleaseEvent(event)

    def _load_prefs(self):
        """Carrega preferências do plugin.

        Recebe: None.
        Retorna: None.
        Faz: carrega preferências do armazenamento persistente usando TOOL_KEY.
        """
