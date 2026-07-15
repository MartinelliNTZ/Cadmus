# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple

from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox, QLabel, QPushButton

from ...styles.Styles import Styles


class DependentCheckBox(QCheckBox):
    """QCheckBox que habilita/desabilita checkboxes dependentes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dependents = []
        self._previous_states = {}
        self.stateChanged.connect(self._on_state_changed)

    def set_dependents(self, dependents: List[QCheckBox]):
        self._dependents = dependents or []
        enabled = self.isChecked()
        for dep in self._dependents:
            self._previous_states.setdefault(dep, dep.isChecked())
            dep.setEnabled(enabled)
            if not enabled:
                dep.setChecked(False)

    def _on_state_changed(self, state):
        enabled = bool(state)
        for dep in self._dependents:
            if not enabled:
                self._previous_states[dep] = dep.isChecked()
                dep.setChecked(False)
            else:
                dep.setChecked(self._previous_states.get(dep, dep.isChecked()))
            dep.setEnabled(enabled)


class GridCheckboxWidget(QWidget):
    """Grid de checkboxes com suporte a formato legado e formato expandido.

    Formatos aceitos:
    - Legado: {"key": "Label"}
    - Expandido por dict: {"key": {"label": "...", "description": "..."}}
    - Expandido por lista: [{"key": "...", "label": "...", "description": "..."}]
    """

    def __init__(
        self,
        options,
        *,
        items_per_row: int = 3,
        checked_by_default: bool = False,
        title: str = None,
        show_control_buttons: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.items_per_row = max(1, int(items_per_row))
        self.checked_by_default = checked_by_default
        self.title = title
        self.show_control_buttons = bool(show_control_buttons)
        self.checkbox_map: Dict[str, QCheckBox] = {}
        self._options = self._normalize_options(options)
        self._build()

    def _normalize_options(self, options) -> List[Tuple[str, str, str]]:
        normalized = []

        if isinstance(options, dict):
            for key, value in options.items():
                if isinstance(value, dict):
                    label = value.get("label") or key
                    description = value.get("description") or ""
                else:
                    label = value
                    description = ""
                key_str = key.value if hasattr(key, 'value') else str(key)
                normalized.append((key_str, str(label), str(description or "")))
            return normalized

        if isinstance(options, list):
            for item in options:
                if not isinstance(item, dict):
                    continue
                key = item.get("key")
                if not key:
                    continue
                key_str = key.value if hasattr(key, 'value') else str(key)
                label = item.get("label") or key
                description = item.get("description") or ""
                normalized.append((key_str, str(label), str(description)))

        return normalized

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        if self.title:
            lbl = QLabel(self.title)
            lbl.setStyleSheet("font-weight: bold;")
            layout.addWidget(lbl)
            layout.addSpacing(6)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(Styles.LAYOUT_H_SPACING)
        grid.setVerticalSpacing(Styles.LAYOUT_V_SPACING)

        for idx, (key, label, description) in enumerate(self._options):
            row = idx // self.items_per_row
            col = idx % self.items_per_row

            chk = DependentCheckBox(label)
            chk.setChecked(self.checked_by_default)
            chk.setFixedHeight(14)
            if description:
                chk.setToolTip(description)

            grid.addWidget(chk, row, col)
            self.checkbox_map[key] = chk

        for col in range(self.items_per_row):
            grid.setColumnStretch(col, 1)

        layout.addLayout(grid)

        if self.show_control_buttons:
            layout.addSpacing(6)

            # Criar botões de controle
            buttons_layout = QHBoxLayout()
            buttons_layout.setContentsMargins(0, 0, 0, 0)
            buttons_layout.setSpacing(6)

            btn_select_all = QPushButton("✔ Selecionar Todos")
            btn_deselect_all = QPushButton("✖ Desselecionar Todos")
            btn_toggle = QPushButton("⇄ Inverter")

            btn_select_all.clicked.connect(self.select_all)
            btn_deselect_all.clicked.connect(self.deselect_all)
            btn_toggle.clicked.connect(self.toggle_all)

            buttons_layout.addWidget(btn_select_all)
            buttons_layout.addWidget(btn_deselect_all)
            buttons_layout.addWidget(btn_toggle)
            buttons_layout.addStretch()

            layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_checkbox(self, key):
        return self.checkbox_map.get(key)

    def get_checkbox_map(self):
        return self.checkbox_map

    def get_checked_keys(self) -> List[str]:
        return [key for key, chk in self.checkbox_map.items() if chk.isChecked()]

    def get_unchecked_keys(self) -> List[str]:
        return [key for key, chk in self.checkbox_map.items() if not chk.isChecked()]

    def get_state_map(self) -> Dict[str, bool]:
        return {key: chk.isChecked() for key, chk in self.checkbox_map.items()}

    def set_checked_keys(self, keys: List[str]):
        keys_set = set(keys or [])
        for key, chk in self.checkbox_map.items():
            chk.setChecked(key in keys_set)

    def set_state_map(self, state_map: Dict[str, bool]):
        state_map = state_map or {}
        for key, chk in self.checkbox_map.items():
            if key in state_map:
                chk.setChecked(bool(state_map.get(key)))

    def set_dependents(self, controller_key, dependent_keys):
        controller = self.checkbox_map.get(controller_key)
        if not controller:
            return

        dependents = [
            self.checkbox_map.get(k) for k in dependent_keys if self.checkbox_map.get(k)
        ]
        if hasattr(controller, "set_dependents"):
            controller.set_dependents(dependents)

    def select_all(self):
        """Marca todos os checkboxes como selecionados."""
        for chk in self.checkbox_map.values():
            chk.setChecked(True)

    def deselect_all(self):
        """Desseleciona todos os checkboxes."""
        for chk in self.checkbox_map.values():
            chk.setChecked(False)

    def toggle_all(self):
        """Inverte o estado de todos os checkboxes."""
        for chk in self.checkbox_map.values():
            chk.setChecked(not chk.isChecked())
