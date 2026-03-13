# -*- coding: utf-8 -*-
"""
ReadOnlyFieldWidget

Widget exclusivo para exibir campos somente-leitura com botão de copiar.

Estrutura visual por item:
Label | QLineEdit(readonly) | [Copiar]

Suporta agrupamento em múltiplas colunas e botão opcional "Copiar tudo".
"""

from qgis.PyQt.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy
)
from qgis.PyQt.QtCore import Qt
from typing import Dict, Optional, Any
from ...utils.ProjectUtils import ProjectUtils


class ReadOnlyFieldWidget(QWidget):
    def __init__(
        self,
        fields: Dict[str, Dict[str, Any]],
        *,
        title: Optional[str] = None,
        title_button_copy_all: Optional[str] = None,
        default_button_title: str = "Copiar",
        num_columns: int = 1,
        parent=None,
    ):
        """
        fields: dict onde cada chave é um identificador e o valor é outro dict com chaves:
            - title: texto do label exibido
            - value: valor inicial (qualquer)
            - value_type: opcional, apenas para referência
            - titlebutton: opcional, texto do botão de copiar individual

        Exemplos:
            {
                'lat': {'title': 'Latitude (Decimal)', 'value': -10.23423423, 'value_type': 'float'},
                'lon_dms': {'title': 'Longitude (DMS)', 'value': '10°20''30"', 'titlebutton': 'Copiar'},
            }
        """
        super().__init__(parent)

        self._fields = fields or {}
        self._num_columns = max(1, int(num_columns))
        self._widgets = {}  # key -> (label, lineedit, button)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(6)

        # title (top) - copy-all button will be placed below the items
        if title:
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(title)
            lbl.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(lbl)
            header_layout.addStretch()
            self._main_layout.addLayout(header_layout)

        # grid for items
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        items = list(self._fields.items())
        for idx, (key, info) in enumerate(items):
            row = idx // self._num_columns
            col = idx % self._num_columns

            title_text = info.get('title', str(key))
            value = info.get('value', "")
            btn_title = info.get('titlebutton', None) or default_button_title

            h = QHBoxLayout()
            h.setContentsMargins(0, 0, 0, 0)
            lbl = QLabel(title_text)
            lbl.setFixedWidth(160)

            le = QLineEdit()
            le.setReadOnly(True)
            le.setText("" if value is None else str(value))
            le.setMinimumWidth(120)
            le.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            btn = QPushButton(btn_title)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # bind copy for this key
            btn.clicked.connect(self._make_copy_callback(key))

            h.addWidget(lbl)
            h.addWidget(le)
            h.addWidget(btn)

            container = QWidget()
            container.setLayout(h)

            grid.addWidget(container, row, col)

            self._widgets[key] = (lbl, le, btn)

        self._main_layout.addLayout(grid)
        self._main_layout.addStretch()

        # copy-all button under the items (right aligned)
        if title_button_copy_all:
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.addStretch()
            btn_all = QPushButton(title_button_copy_all)
            btn_all.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn_all.clicked.connect(self._copy_all)
            btn_layout.addWidget(btn_all)
            self._main_layout.addLayout(btn_layout)

    def _make_copy_callback(self, key):
        def _cb():
            _, le, _ = self._widgets.get(key, (None, None, None))
            if le:
                ProjectUtils.set_clipboard_text(le.text())
        return _cb

    def _copy_all(self):
        parts = []
        for key, (lbl, le, btn) in self._widgets.items():
            title = lbl.text() or key
            parts.append(f"{title}: {le.text()}")
        ProjectUtils.set_clipboard_text("\n".join(parts))

    def set_value(self, key: str, value: Any):
        """Define o valor do campo identificado por `key`."""
        w = self._widgets.get(key)
        if not w:
            return
        _, le, _ = w
        le.setText("" if value is None else str(value))

    def get_value(self, key: str) -> Optional[str]:
        w = self._widgets.get(key)
        if not w:
            return None
        _, le, _ = w
        return le.text()

    def set_values(self, values: Dict[str, Any]):
        for k, v in (values or {}).items():
            self.set_value(k, v)
