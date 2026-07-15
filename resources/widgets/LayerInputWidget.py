# -*- coding: utf-8 -*-

from qgis.PyQt.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from qgis.PyQt.QtCore import pyqtSignal
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsVectorLayer, QgsMapLayerProxyModel, QgsProject
from ...core.config.LogUtils import LogUtils
from ...i18n.TranslationManager import STR

# Logger do widget
logger = LogUtils(tool="widgets", class_name="LayerInputWidget")


class LayerInputWidget(QWidget):
    """
    Widget padrão para seleção de camada.

    Recursos:
    - Emite signal layerChanged(layer)
    - Sincroniza com camada ativa do QGIS
    - Scroll do mouse troca camada
    - Atualiza estado de seleção automaticamente
    """

    layerChanged = pyqtSignal(object)  # QgsMapLayer | None

    def __init__(
        self,
        label_text: str,
        filters,
        *,
        allow_empty: bool = True,
        enable_selected_checkbox: bool = True,
        parent=None,
    ):
        super().__init__(parent)

        self._state_layer = None
        self._filters = self._normalize_filters(filters)

        self._label = QLabel(label_text)
        self._combo = QgsMapLayerComboBox()
        self._combo.setAllowEmptyLayer(allow_empty)
        self._combo.setFilters(self._filters)

        self._chk_selected = None
        if enable_selected_checkbox:
            self._chk_selected = QCheckBox(STR.ONLY_SELECTED_FEATURES)
            self._chk_selected.setEnabled(False)

        self._build_layout()
        self._bind_events()
        self._try_select_active_layer()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def _build_layout(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._label)
        layout.addWidget(self._combo)

        if self._chk_selected:
            layout.addWidget(self._chk_selected)

    # --------------------------------------------------
    # Bindings
    # --------------------------------------------------
    def _bind_events(self):
        self._combo.layerChanged.connect(self._on_layer_changed)
        QgsProject.instance().layerWasAdded.connect(self._on_project_layers_changed)
        QgsProject.instance().layerWillBeRemoved.connect(
            self._on_project_layers_changed
        )

        self._on_layer_changed()

    # --------------------------------------------------
    # Core logic
    # --------------------------------------------------
    def _on_layer_changed(self, *args):
        self._disconnect_old_layer()

        layer = self._combo.currentLayer()
        self._state_layer = layer

        if isinstance(layer, QgsVectorLayer):
            try:
                layer.selectionChanged.connect(self._update_selection_state)
            except RuntimeError:
                # Objeto C++ deletado durante shutdown — ignora
                pass

        self._update_selection_state()
        self.layerChanged.emit(layer)

    def _on_active_layer_changed(self, layer):
        if not layer:
            return

        if not self._layer_matches_filter(layer):
            return

        self._combo.setLayer(layer)

    def _on_project_layers_changed(self, *args):
        # garante que o combo se mantenha consistente
        try:
            if self._state_layer not in QgsProject.instance().mapLayers().values():
                self._combo.setCurrentIndex(0)
        except RuntimeError:
            # Objeto C++ foi deletado durante shutdown do QGIS
            pass

    def _update_selection_state(self):
        if not self._chk_selected:
            return

        layer = self._state_layer

        if not isinstance(layer, QgsVectorLayer):
            self._chk_selected.setChecked(False)
            self._chk_selected.setEnabled(False)
            return

        try:
            count = layer.selectedFeatureCount()
        except RuntimeError:
            # Objeto C++ deletado durante shutdown — desabilita checkbox
            self._chk_selected.setChecked(False)
            self._chk_selected.setEnabled(False)
            return

        self._chk_selected.setEnabled(count > 0)

        if count == 0:
            self._chk_selected.setChecked(False)

    def _disconnect_old_layer(self):
        old = self._state_layer
        if isinstance(old, QgsVectorLayer):
            try:
                # Verifica se o objeto C++ ainda existe (evita RuntimeError durante shutdown)
                if old is not None and not old.isValid():
                    return
                old.selectionChanged.disconnect(self._update_selection_state)
            except RuntimeError:
                # Objeto C++ foi deletado (ex: durante restart/shutdown do QGIS)
                # A desconexão já é tratada automaticamente pelo Qt
                pass
            except Exception as e:
                logger.exception(e)

    # --------------------------------------------------
    # Auto select
    # --------------------------------------------------

    def _try_select_active_layer(self):
        try:
            from qgis.utils import iface

            layer = iface.activeLayer()
        except Exception as e:
            logger.error(f"Erro ao obter activeLayer: {e}")
            layer = None

        if layer and self._layer_matches_filter(layer):
            self._combo.setLayer(layer)

    def _layer_matches_filter(self, layer) -> bool:
        if not layer:
            return False

        if self._filters & QgsMapLayerProxyModel.Filter.VectorLayer:
            return isinstance(layer, QgsVectorLayer)

        return True

    # --------------------------------------------------
    # Wheel event (scroll troca camada)
    # --------------------------------------------------
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        idx = self._combo.currentIndex()
        count = self._combo.count()

        if count == 0:
            return

        if delta > 0:
            idx -= 1
        else:
            idx += 1

        idx = max(0, min(idx, count - 1))
        self._combo.setCurrentIndex(idx)
        event.accept()

    # --------------------------------------------------
    # API pública
    # --------------------------------------------------
    def current_layer(self):
        return self._combo.currentLayer()

    def only_selected_enabled(self) -> bool:
        return bool(self._chk_selected and self._chk_selected.isChecked())

    def set_layer(self, layer):
        self._combo.setLayer(layer)

    def on_layer_change(self, callback):
        """
        Conecta um callback ao sinal layerChanged.
        Já invoca imediatamente para popular o dropdown
        logo na abertura, independente do estado da camada.

        Uso no plugin:
            self.layer_input.on_layer_change(self._on_layer_changed)

        O plugin apenas informa qual callback conectar,
        o widget gerencia o ciclo de vida.
        """
        self.layerChanged.connect(callback)
        callback()

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    @staticmethod
    def _normalize_filters(filters):
        if isinstance(filters, (list, tuple, set)):
            final = 0
            for f in filters:
                final |= f
            return final
        return filters
