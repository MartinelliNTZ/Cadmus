# -*- coding: utf-8 -*-
import os
from qgis.gui import QgsCustomDropHandler

from ...i18n.TranslationManager import STR
from ...utils.ExplorerUtils import ExplorerUtils
from ...utils.QgisMessageUtil import QgisMessageUtil
from .DronePipelineService import DronePipelineService


class MrkDropHandler(QgsCustomDropHandler):
    """Handler de drag-and-drop de arquivos .mrk no QGIS."""

    PROVIDER_KEY = "cadmus_mrk"

    def __init__(self, iface):
        super().__init__()
        self.iface = iface

    def handleFileDrop(self, file):
        if not ExplorerUtils.has_extension(file, [".mrk"]):
            return False

        QgisMessageUtil.bar_info(self.iface, STR.MRK_DROP_START, duration=3)
        return DronePipelineService.execute(
            iface=self.iface,
            input_path=os.path.dirname(file),
            file_path=file,
        )

    def customUriProviderKey(self):
        return self.PROVIDER_KEY

    def handleCustomUriDrop(self, uri):
        if not uri:
            return False
        return self.handleFileDrop(uri.uri)
