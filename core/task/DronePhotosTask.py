# DronePhotosTask.py
# -*- coding: utf-8 -*-
import os
from qgis.core import QgsTask
from utils.mrk.PhotoMetadata import PhotoMetadata
from core.config.LogUtils import LogUtils
from utils.ToolKeys import ToolKey

class DronePhotosTask(QgsTask):
    TOOL_KEY = ToolKey.DRONE_COORDINATES

    def __init__(self, description, points, base_folder, recursive=True, callback=None):
        super().__init__(description, QgsTask.CanCancel)
        self._logger = LogUtils(tool=self.TOOL_KEY, class_name=self.__class__.__name__)
        self._logger.info(f"Inicializando task: {description}")
        self.points = points
        self.base_folder = base_folder
        self.recursive = recursive
        self.result_points = None
        self.callback = callback

    # ---------- RUN SEM ARGUMENTOS ----------
    def run(self):
        self._logger.info(f"ENTRANDO NO RUN DA TASK: cruzando fotos em {self.base_folder}")
        try:
            self.result_points = PhotoMetadata.enrich(
                self.points,
                base_folder=self.base_folder,
                recursive=self.recursive
            )
            self.setProgress(100)  # atualiza progresso no QGIS
            self._logger.info(f"Cruzamento concluído ({len(self.result_points)} pontos)")
            self.finished(True)
            return True
        except Exception as e:
            self._logger.exception(e)
            return False

    # ---------- CALLBACK FINAL ----------
    def finished(self, result):
        self._logger.info(f"FINALIZANDO TASK: {self.description()}")
        if result and self.callback:
            self.callback(self.result_points)
        elif not result:
            self._logger.warning("O cruzamento de fotos falhou ou foi cancelado")
