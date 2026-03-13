# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QCheckBox, QListWidget, QPushButton, QListWidgetItem
)
from qgis.PyQt.QtCore import Qt


class AttributeSelectorWidget(QWidget):
    """
    Widget exclusivo para seleção de atributos (campos).
    """

    def __init__(
        self,
        *,
        title="Atributos",
        check_all_text="Usar todos os atributos",
        parent=None
    ):
        super().__init__(parent)
        self._build_ui(title, check_all_text)

    # ------------------------------------------------------------------

    def _build_ui(self, title, check_all_text):
        layout = QVBoxLayout(self)

        if title:
            layout.addWidget(QLabel(title))

        self.chk_all = QCheckBox(check_all_text)
        layout.addWidget(self.chk_all)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.btn_select = QPushButton("✔ Selecionar")
        self.btn_unselect = QPushButton("✖ Remover")
        self.btn_invert = QPushButton("⇄ Inverter")

        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_unselect)
        btn_layout.addWidget(self.btn_invert)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # bindings
        self.chk_all.toggled.connect(self._on_chk_all_toggled)

        self.btn_select.clicked.connect(
            lambda: self._set_check_state(Qt.Checked)
        )
        self.btn_unselect.clicked.connect(
            lambda: self._set_check_state(Qt.Unchecked)
        )
        self.btn_invert.clicked.connect(self._invert_selection)

    # ------------------------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------------------------

    def set_fields(self, field_names):
        self.list_widget.clear()

        for name in field_names:
            item = QListWidgetItem(name)
            item.setCheckState(Qt.Checked)
            self.list_widget.addItem(item)

    def get_selected_fields(self):
        if self.chk_all.isChecked():
            return None

        return [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]

    def use_all_fields(self) -> bool:
        return self.chk_all.isChecked()
    def set_checked_all(self,checked):
        self.chk_all.setChecked(checked)

    

    # ------------------------------------------------------------------
    # INTERNO
    # ------------------------------------------------------------------

    def _on_chk_all_toggled(self, checked: bool):
        """
        Quando 'Usar todos os atributos' está ativo,
        todo o controle manual fica desabilitado.
        """
        self.list_widget.setDisabled(checked)

        self.btn_select.setDisabled(checked)
        self.btn_unselect.setDisabled(checked)
        self.btn_invert.setDisabled(checked)

    def _set_check_state(self, state):
        selected = self.list_widget.selectedItems()
        items = selected if selected else [
            self.list_widget.item(i)
            for i in range(self.list_widget.count())
        ]
        for item in items:
            item.setCheckState(state)

    def _invert_selection(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setCheckState(
                Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
            )
