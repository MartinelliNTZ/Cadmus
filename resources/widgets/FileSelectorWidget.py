# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QLineEdit, QPushButton
)
from ...utils.StringUtils import StringUtils
from qgis.PyQt.QtWidgets import QFileDialog


class FileSelectorWidget(QWidget):
    """

    """    
    MODE_OPEN = "open"
    MODE_SAVE = "save"

    def __init__(
        self,
        *,
        checkbox_text="Arquivo?",
        label_text="Arquivo:",
        file_filter=StringUtils.FILTER_ALL,        
        mode=MODE_OPEN,
        parent=None
    ):
        super().__init__(parent)

        self._file_filter = file_filter
        self._mode = mode

        self._chk = QCheckBox(checkbox_text)
        self._txt = QLineEdit()
        self._btn = QPushButton("...")

        self._build_ui(label_text)
        self._bind_events()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _build_ui(self, label_text):
        layout = QVBoxLayout(self)

        layout.addWidget(self._chk)

        row = QHBoxLayout()
        row.addWidget(QLabel(label_text))
        row.addWidget(self._txt)
        row.addWidget(self._btn)

        layout.addLayout(row)

        self._txt.setEnabled(False)
        self._btn.setEnabled(False)

    # --------------------------------------------------
    # Bindings
    # --------------------------------------------------
    def _bind_events(self):
        self._chk.toggled.connect(self._update_enabled_state)

        self._btn.clicked.connect(
            lambda: self.select_file(
                self._txt,
                self._file_filter,
                self._mode
            )
        )


        self._update_enabled_state()


    def _update_enabled_state(self):
        enabled = self._chk.isChecked()
        self._txt.setEnabled(enabled)
        self._btn.setEnabled(enabled)

    # --------------------------------------------------
    # API pública
    # --------------------------------------------------
    def is_enabled(self) -> bool:
        return self._chk.isChecked()

    def set_enabled(self, enabled: bool):
        self._chk.setChecked(enabled)

    def get_file_path(self) -> str:
        return self._txt.text().strip()

    def set_file_path(self, path: str):
        self._txt.setText(path or "")
        
    def select_file(self, line_edit, file_filter, mode):
        if mode == FileSelectorWidget.MODE_SAVE:
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar arquivo",
                line_edit.text(),
                file_filter
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Selecionar arquivo",
                line_edit.text(),
                file_filter
            )

        if path:
            line_edit.setText(path)
