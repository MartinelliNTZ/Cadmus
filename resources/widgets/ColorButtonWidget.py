# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStyle,
)
from qgis.PyQt.QtCore import pyqtSignal, QSize, Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.gui import QgsColorButton

from ...utils.ProjectUtils import ProjectUtils
from ..IconManager import IconManager as IM


class ColorButtonWidget(QWidget):
    """Widget compacto e configuravel para selecao de cor."""

    colorChanged = pyqtSignal(QColor)

    def __init__(
        self,
        *,
        title: str = "Cor",
        initial_color: QColor = None,
        tooltip: str = "Escolha uma cor",
        parent=None,
    ):
        super().__init__(parent)

        self._title = title
        self._initial_color = initial_color or QColor("#ffffff")
        self._tooltip = tooltip

        self._build_ui()
        self.set_color(self._initial_color)

    def _build_ui(self):
        self.setObjectName("color_button_widget")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self._layout = layout

        self._title_label = QLabel(self._title)
        self._title_label.setObjectName("color_button_title")
        self._title_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._title_label)
        layout.setAlignment(self._title_label, Qt.AlignmentFlag.AlignVCenter)

        self._button = QgsColorButton()
        self._button.setObjectName("color_button_picker")
        self._button.setAllowOpacity(True)
        self._button.setToolTip(self._tooltip)
        self._button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._button.colorChanged.connect(self._on_color_changed)
        layout.addWidget(self._button)
        layout.setAlignment(self._button, Qt.AlignmentFlag.AlignVCenter)

        self._value_input = QLineEdit("#ffffff")
        self._value_input.setObjectName("color_button_hex_input")
        self._value_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._value_input.editingFinished.connect(self._on_hex_edited)
        layout.addWidget(self._value_input, 1)
        layout.setAlignment(self._value_input, Qt.AlignmentFlag.AlignVCenter)

        self._copy_button = QPushButton()
        self._copy_button.setObjectName("color_button_copy")
        self._copy_button.setToolTip("Copiar valor hexadecimal")
        self._copy_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._copy_button.clicked.connect(self._copy_hex_value)
        self._copy_button.setIcon(self._resolve_copy_icon())
        layout.addWidget(self._copy_button)
        layout.setAlignment(self._copy_button, Qt.AlignmentFlag.AlignVCenter)

        layout.setStretch(2, 1)

    def _on_color_changed(self, color: QColor):
        self._update_value_label(color)
        self.colorChanged.emit(color)

    def _update_value_label(self, color: QColor):
        if color.alpha() < 255:
            text = color.name(QColor.NameFormat.HexArgb)
        else:
            text = color.name(QColor.NameFormat.HexRgb)
        self._value_input.setText(text)

    def _on_hex_edited(self):
        text = self._value_input.text().strip()
        if not text:
            self._update_value_label(self.get_color())
            return

        color = QColor(text)
        if color.isValid():
            self.set_color(color)
            self.colorChanged.emit(color)
        else:
            self._update_value_label(self.get_color())

    def _copy_hex_value(self):
        ProjectUtils.set_clipboard_text(self._value_input.text().strip())

    def _resolve_copy_icon(self) -> QIcon:
        icon_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "icons", "copy_attributes.ico")
        )
        icon_path = IM.icon_path(IM.COPY_BUTTON)

        if os.path.exists(icon_path):
            return QIcon(icon_path)

        return self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)

    def set_color(self, color: QColor):
        self._button.setColor(color)
        self._update_value_label(color)

    def set_title(self, title: str):
        self._title = title or ""
        self._title_label.setText(self._title)

    def set_title_width(self, width: int = None):
        if width is None:
            self._title_label.setMinimumWidth(0)
            self._title_label.setMaximumWidth(16777215)
            return
        self._title_label.setFixedWidth(max(1, int(width)))

    def set_hex_width(self, minimum_width: int = None):
        if minimum_width is None:
            self._value_input.setMinimumWidth(0)
            return
        self._value_input.setMinimumWidth(max(1, int(minimum_width)))

    def set_hex_height(self, height: int = None):
        if height is None:
            self._value_input.setMinimumHeight(0)
            self._value_input.setMaximumHeight(16777215)
            return
        value = max(1, int(height))
        self._value_input.setFixedHeight(value)

    def set_picker_size(self, width: int = None, height: int = None):
        if width is not None and height is not None:
            self._button.setFixedSize(int(width), int(height))
        elif height is not None:
            self._button.setFixedHeight(int(height))
        elif width is not None:
            self._button.setFixedWidth(int(width))

    def set_copy_button_size(self, width: int = 24, height: int = 24):
        if width is not None and height is not None:
            value_w = max(1, int(width))
            value_h = max(1, int(height))
            self._copy_button.setMinimumSize(value_w, value_h)
            self._copy_button.setMaximumSize(value_w, value_h)
            self._copy_button.setFixedSize(value_w, value_h)
        elif height is not None:
            value = max(1, int(height))
            self._copy_button.setMinimumHeight(value)
            self._copy_button.setMaximumHeight(value)
            self._copy_button.setFixedHeight(value)
        elif width is not None:
            value = max(1, int(width))
            self._copy_button.setMinimumWidth(value)
            self._copy_button.setMaximumWidth(value)
            self._copy_button.setFixedWidth(value)

    def set_copy_icon_size(self, width: int = 14, height: int = 14):
        self._copy_button.setIconSize(QSize(int(width), int(height)))

    def set_spacing(self, spacing: int):
        self._layout.setSpacing(int(spacing))

    def set_hex_read_only(self, read_only: bool):
        self._value_input.setReadOnly(bool(read_only))

    def set_hex_placeholder(self, text: str):
        self._value_input.setPlaceholderText(text or "")

    def set_copy_icon(self, icon: QIcon):
        if icon and not icon.isNull():
            self._copy_button.setIcon(icon)

    def get_color(self) -> QColor:
        return self._button.color()

    def color_button(self) -> QgsColorButton:
        return self._button

    def hex_input(self) -> QLineEdit:
        return self._value_input

    def copy_button(self) -> QPushButton:
        return self._copy_button
