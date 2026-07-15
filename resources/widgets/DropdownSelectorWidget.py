# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from ...i18n.TranslationManager import STR


class DropdownSelectorWidget(QWidget):
    selectionChanged = pyqtSignal(str, str)

    def __init__(
        self,
        *,
        title: str,
        options_dict: dict,
        selected_key=None,
        allow_empty: bool = False,
        empty_text: str = f"{STR.SELECT}...",
        parent=None,
    ):
        super().__init__(parent)
        self._title = title
        self._options_dict = options_dict or {}
        self._allow_empty = allow_empty
        self._empty_text = empty_text
        self._build_ui()
        self.set_options(self._options_dict)
        if selected_key is not None:
            self.set_selected_key(selected_key)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        self._label = QLabel(self._title)
        self._label.setMinimumWidth(100)
        self._label.setMaximumWidth(220)
        row.addWidget(self._label)

        self._combo = QComboBox()
        self._combo.currentIndexChanged.connect(self._on_index_changed)
        row.addWidget(self._combo)

        layout.addLayout(row)

    def _on_index_changed(self, _index: int):
        self.selectionChanged.emit(self.get_selected_key(), self.get_selected_text())

    def set_options(self, options_dict: dict):
        self._options_dict = options_dict or {}
        self._combo.blockSignals(True)
        self._combo.clear()

        if self._allow_empty:
            self._combo.addItem(self._empty_text, None)

        for key, label in self._options_dict.items():
            self._combo.addItem(str(label), key)

        self._combo.blockSignals(False)
        self._on_index_changed(self._combo.currentIndex())

    def get_selected_key(self):
        return self._combo.currentData()

    def get_selected_text(self) -> str:
        return self._combo.currentText()

    def set_selected_key(self, key):
        idx = self._combo.findData(key)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)

    def set_selected_text(self, text: str):
        idx = self._combo.findText(str(text))
        if idx >= 0:
            self._combo.setCurrentIndex(idx)

    def combo(self) -> QComboBox:
        return self._combo
