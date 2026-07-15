# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget

from ...core.config.LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey


class CrsSelectorWidget(QWidget):
    crsChanged = pyqtSignal(str, str)

    def __init__(
        self,
        *,
        title: str,
        parent=None,
        tool_key: str = None,
        default_auth_id: str = "",
    ):
        super().__init__(parent)
        self._title = title
        self._tool_key = tool_key or ToolKey.UNTRACEABLE
        self.logger = LogUtils(
            tool=self._tool_key,
            class_name="CrsSelectorWidget",
            level=LogUtils.DEBUG,
        )
        self._build_ui()
        if default_auth_id:
            self.set_crs_authid(default_auth_id)

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

        self._selector = QgsProjectionSelectionWidget(self)
        self._selector.crsChanged.connect(self._on_crs_changed)
        row.addWidget(self._selector)

        layout.addLayout(row)

    def _on_crs_changed(self, crs):
        authid = crs.authid() if crs and crs.isValid() else ""
        description = crs.description() if crs and crs.isValid() else ""
        self.logger.debug(f"CRS selecionado: {authid} | {description}")
        self.crsChanged.emit(authid, description)

    def set_crs(self, crs: QgsCoordinateReferenceSystem):
        if crs and crs.isValid():
            self._selector.setCrs(crs)

    def set_crs_authid(self, authid: str):
        crs = QgsCoordinateReferenceSystem(authid)
        if crs.isValid():
            self._selector.setCrs(crs)
            return True
        return False

    def get_crs(self) -> QgsCoordinateReferenceSystem:
        return self._selector.crs()

    def get_crs_authid(self) -> str:
        crs = self.get_crs()
        return crs.authid() if crs and crs.isValid() else ""

    def selector(self) -> QgsProjectionSelectionWidget:
        return self._selector
