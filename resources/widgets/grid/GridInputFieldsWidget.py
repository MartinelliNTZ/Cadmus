# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
)
from qgis.PyQt.QtCore import pyqtSignal


class GridInputFieldsWidget(QWidget):
    """
    Widget para múltiplos campos de input baseados em um dicionário.

    Características:
    - Suporta tipos: text, int, float
    - Sempre retorna dict via get_values()
    - Permite definir valores via set_values()
    - Emite sinal valuesChanged quando qualquer valor muda

    Sinais:
        valuesChanged: emitido quando qualquer valor muda (retorna dict)
    """

    valuesChanged = pyqtSignal(dict)

    def __init__(self, fields_dict: dict, parent=None):
        """
        Inicializa widget com múltiplos campos.

        Parameters:
            fields_dict: Dicionário de configuração dos campos
            parent: Widget pai
        """
        super().__init__(parent)
        self.fields_dict = fields_dict
        self.inputs = {}  # Mapeia chave -> widget de input
        self._build_ui()

    def _build_ui(self):
        """Constrói UI com campos baseados no dicionário."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        for key, config in self.fields_dict.items():
            title = config.get("title", key)
            description = str(config.get("description", ""))
            show_label = config.get("show_label", True)
            input_type = config.get("type", "text")
            default = config.get("default", "")

            # Layout horizontal para label + input
            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(4)

            # Label com largura mínima consistente
            if show_label:
                label = QLabel(title)
                label.setMinimumWidth(100)
                label.setMaximumWidth(150)
                if description:
                    label.setToolTip(description)
                h_layout.addWidget(label)

            # Input widget conforme o tipo
            if input_type == "int":
                input_widget = QSpinBox()
                input_widget.setRange(-999999, 999999)
                input_widget.setMaximumHeight(24)
                input_widget.setValue(int(default) if default else 0)
                input_widget.valueChanged.connect(self._on_value_changed)

            elif input_type == "float":
                input_widget = QDoubleSpinBox()
                input_widget.setRange(-999999.0, 999999.0)
                input_widget.setMaximumHeight(24)
                input_widget.setDecimals(4)
                input_widget.setValue(float(default) if default else 0.0)
                input_widget.valueChanged.connect(self._on_value_changed)

            else:  # text (padrão)
                input_widget = QLineEdit()
                input_widget.setMaximumHeight(24)
                input_widget.setText(str(default))
                input_widget.textChanged.connect(self._on_value_changed)

            if description and show_label:
                input_widget.setToolTip(description)

            h_layout.addWidget(input_widget)
            layout.addLayout(h_layout)

            # Armazenar widget para referência posterior
            self.inputs[key] = input_widget

    def _on_value_changed(self):
        """Emite sinal quando qualquer valor muda."""
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict:
        """
        Retorna dicionário com valores atuais de todos os campos.

        Returns:
            dict: {chave: valor, ...}
        """
        values = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QSpinBox):
                values[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                values[key] = widget.value()
            else:  # QLineEdit
                values[key] = widget.text()
        return values

    def set_values(self, values: dict):
        """
        Define valores dos campos.

        Parameters:
            values: Dicionário {chave: valor, ...}
        """
        for key, value in values.items():
            if key in self.inputs:
                widget = self.inputs[key]
                if isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(float(value))
                else:  # QLineEdit
                    widget.setText(str(value))

    def get_value(self, key: str):
        """Retorna valor de um campo específico."""
        values = self.get_values()
        return values.get(key)

    def set_value(self, key: str, value):
        """Define valor de um campo específico."""
        if key in self.inputs:
            widget = self.inputs[key]
            if isinstance(widget, QSpinBox):
                widget.setValue(int(value))
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(value))
            else:  # QLineEdit
                widget.setText(str(value))
