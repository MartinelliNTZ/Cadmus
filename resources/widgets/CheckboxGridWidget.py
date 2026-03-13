from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QCheckBox, QLabel
from typing import List
from ...resources.styles.Styles import Styles


class DependentCheckBox(QCheckBox):
    """QCheckBox que pode habilitar/desabilitar outros checkboxes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dependents = []
        self._previous_states = {}
        self.stateChanged.connect(self._on_state_changed)

    def set_dependents(self, dependents: List[QCheckBox]):
        """Define checkboxes que dependem deste checkbox.

        Quando desmarcado, os dependentes são desabilitados e desmarcados.
        Quando marcado, os dependentes são reativados e retornam ao estado anterior.
        """
        self._dependents = dependents or []
        current_checked = self.isChecked()
        for d in self._dependents:
            # guardar estado anterior (antes de alterar enable/checked)
            self._previous_states.setdefault(d, d.isChecked())
            d.setEnabled(current_checked)
            if not current_checked:
                # desmarcar quando controlador estiver off
                d.setChecked(False)

    def _on_state_changed(self, state):
        enabled = bool(state)
        for d in self._dependents:
            try:
                if not enabled:
                    # guarda o estado atual para restaurar depois
                    self._previous_states[d] = d.isChecked()
                    d.setChecked(False)
                d.setEnabled(enabled)
            except Exception:
                pass


class CheckboxGridWidget(QWidget):
    """
    Widget exclusivo para grid de checkboxes com suporte a dicionário chave→label.
    """
    def __init__(self, options_dict, *, items_per_row=3, checked_by_default=False, title=None, parent=None):
        super().__init__(parent)
        self.options_dict = options_dict
        self.items_per_row = items_per_row
        self.checked_by_default = checked_by_default
        self.title = title
        self.checkbox_map = {}
        self._build()

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

        for idx, (key, label) in enumerate(self.options_dict.items()):
            row = idx // self.items_per_row
            col = idx % self.items_per_row
            chk = DependentCheckBox(label)
            chk.setChecked(self.checked_by_default)
            chk.setFixedHeight(14)
            grid.addWidget(chk, row, col)
            self.checkbox_map[key] = chk

        for col in range(self.items_per_row):
            grid.setColumnStretch(col, 1)
        layout.addLayout(grid)
        self.setLayout(layout)

    def get_checkbox(self, key):
        return self.checkbox_map.get(key)

    def get_checkbox_map(self):
        return self.checkbox_map

    def set_dependents(self, controller_key, dependent_keys):
        """Configura dependências entre checkboxes.

        controller_key: chave do checkbox que controla (enable/disable)
        dependent_keys: lista de chaves que serão dependentes
        """
        controller = self.checkbox_map.get(controller_key)
        if not controller:
            return

        dependents = [self.checkbox_map.get(k) for k in dependent_keys if self.checkbox_map.get(k)]
        if hasattr(controller, "set_dependents"):
            controller.set_dependents(dependents)
