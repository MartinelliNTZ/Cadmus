# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ....i18n.TranslationManager import STR
from ....resources.widgets.simple.SelectorWidget import SelectorWidget


class DefaultProjectsFolderDialog(QDialog):
    DEFAULT_FOLDER = "C:/QgisProjects"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(STR.DEFAULT_PROJECTS_FOLDER_TITLE)
        self.setModal(True)
        self.resize(620, 120)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        info = QLabel(STR.DEFAULT_PROJECTS_FOLDER_PROMPT)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.selector = SelectorWidget(
            title=STR.PROJECTS_FOLDER,
            mode=SelectorWidget.MODE_FOLDER,
            parent=self,
        )
        self.selector.set_path(self.DEFAULT_FOLDER)
        layout.addWidget(self.selector)

        # Qt5: QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        # Qt6: QDialogButtonBox.StandardButton.Ok |
        #      QDialogButtonBox.StandardButton.Cancel
        # Usar StandardButton garante compatibilidade Qt5/Qt6
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_folder_path(self) -> str:
        paths = self.selector.get_paths()
        if paths:
            return paths[0].strip()

        fallback_text = self.selector.get_file_path().strip()
        return fallback_text or self.DEFAULT_FOLDER
