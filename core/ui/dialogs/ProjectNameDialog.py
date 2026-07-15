# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from ....i18n.TranslationManager import STR
from ....plugins.BaseDialog import BaseDialog
from ....resources.styles.Styles import Styles


class ProjectNameDialog(BaseDialog):
    def __init__(self, suggested_name: str, parent=None):
        super().__init__(parent)
        self._suggested_name = suggested_name
        self.setObjectName("project_name_dialog")
        self.setWindowTitle(STR.PROJECT_NAME_TITLE)
        self.setModal(False)
        self.resize(460, 110)
        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        """Monta os widgets do dialogo de nome de projeto."""
        layout = QVBoxLayout(self)

        info = QLabel(STR.PROJECT_NAME_PROMPT)
        info.setObjectName("project_name_info_label")
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        field_label = QLabel(STR.PROJECT_NAME_LABEL)
        field_label.setObjectName("project_name_field_label")
        row.addWidget(field_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("project_name_input")
        self.name_input.setPlaceholderText(self._suggested_name)
        row.addWidget(self.name_input)
        layout.addLayout(row)

        buttons_row = QHBoxLayout()
        buttons_row.addStretch()

        cancel_button = QPushButton(STR.CANCEL)
        cancel_button.setObjectName("project_name_btn_cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_button)

        ok_button = QPushButton(STR.OK)
        ok_button.setObjectName("project_name_btn_ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        buttons_row.addWidget(ok_button)

        layout.addLayout(buttons_row)

    def _apply_styles(self):
        """Aplica o stylesheet do dialogo de nome de projeto."""
        self.setStyleSheet(Styles.project_name_dialog())

    def get_project_name(self) -> str:
        """Retorna o nome de projeto informado sem espacos extras."""
        return self.name_input.text().strip()
