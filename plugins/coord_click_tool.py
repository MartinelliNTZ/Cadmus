from qgis.gui import QgsMapTool
from qgis.core import QgsApplication
import sip

from ..core.task.reverse_geocoding_task import ReverseGeocodeTask
from ..core.task.altimetry_task import AltimetriaTask
from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.ExecutionContext import ExecutionContext
from ..core.engine_tasks.ReverseGeocodeStep import ReverseGeocodeStep
from ..core.engine_tasks.AltimetryStep import AltimetryStep
from ..core.engine_tasks.ParallelStep import ParallelStep
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from .coord_result_dialog import CoordResultDialog
from ..core.config.LogUtils import LogUtils
from ..utils.QgisMessageUtil import QgisMessageUtil


class CoordClickTool(QgsMapTool):

    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.dialog = None
        self.address_task = None
        self.alt_task = None
        # logger for the map tool
        try:
            self.logger = LogUtils(tool="coord_click", class_name="CoordClickTool", level=LogUtils.DEBUG)
            self.logger.debug("CoordClickTool initialized")
        except Exception:
            self.logger = None

    def canvasReleaseEvent(self, event):
        try:
            if self.logger:
                self.logger.debug("canvasReleaseEvent triggered")
        except Exception:
            pass

        snap = self.canvas.snappingUtils().snapToMap(event.pos())
        point = snap.point() if snap.isValid() else self.toMapCoordinates(event.pos())

        info = VectorLayerProjection.get_coordinate_info(
            point,
            self.canvas.mapSettings().destinationCrs()
        )

        # -----------------------------
        # VIEW
        # -----------------------------
        if not self.dialog or not self.dialog.isVisible():
            try:
                if self.logger:
                    self.logger.debug("Creating CoordResultDialog")
                self.dialog = CoordResultDialog(self.iface, info)
                self.dialog.show()
                # ensure dialog is brought to front
                try:
                    self.dialog.raise_()
                    self.dialog.activateWindow()
                except Exception:
                    pass
                if self.logger:
                    self.logger.debug("CoordResultDialog shown")
            except Exception as e:
                # fallback: notify user
                QgisMessageUtil.bar_critical(self.iface, f"Erro ao abrir diálogo de coordenadas: {e}")
                if self.logger:
                    self.logger.error(f"Erro ao criar/mostrar CoordResultDialog: {e}")
        else:
            try:
                if self.logger:
                    self.logger.debug("Updating existing CoordResultDialog")
                self.dialog.update_info(info)
                try:
                    self.dialog.raise_()
                    self.dialog.activateWindow()
                except Exception:
                    pass
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Erro ao atualizar diálogo: {e}")

        # -----------------------------
        # Cancela tasks antigas
        # -----------------------------
        self._cancel_task(self.address_task)
        self._cancel_task(self.alt_task)

        # Se o diálogo não foi criado/atualizado com sucesso, não iniciar tasks.
        if not self.dialog:
            if self.logger:
                self.logger.debug("Dialog not available; skipping tasks scheduling")
            return

        lat, lon = info["lat"], info["lon"]

        # -----------------------------
        # -----------------------------
        # Use AsyncPipelineEngine with Steps for reverse geocode + altimetry
        # -----------------------------
        try:
            # cancel previous pipeline if running
            try:
                if hasattr(self, "pipeline_engine") and self.pipeline_engine and self.pipeline_engine.is_running():
                    self.pipeline_engine.cancel()
            except Exception:
                pass

            context = ExecutionContext({
                "lat": lat,
                "lon": lon,
                "iface": self.iface,
                "dialog": self.dialog,
                "tool_key": "coord_click",
            })

            # Reverse geocode and altimetry are independent — run in parallel
            steps = [
                ParallelStep([ReverseGeocodeStep(), AltimetryStep()], description="coord_click_geo_alt")
            ]

            self.pipeline_engine = AsyncPipelineEngine(steps, context)
            self.pipeline_engine.start()
        except Exception as e:
            # Fallback to previous behavior: schedule tasks individually
            if self.logger:
                self.logger.warning(f"Pipeline failed, falling back to legacy tasks: {e}")

            def on_address(result, error):
                try:
                    if error:
                        if self.logger:
                            self.logger.warning(f"Reverse geocode error: {error}")
                        self.dialog.set_address(None)
                        self.iface.messageBar().pushWarning(
                            "Geocodificação", error
                        )
                    else:
                        if self.logger:
                            self.logger.debug(f"Reverse geocode result: {result}")
                        self.dialog.set_address(result)
                except Exception as e2:
                    if self.logger:
                        self.logger.error(f"on_address handler error: {e2}")

            self.address_task = ReverseGeocodeTask(lat, lon, on_address)
            QgsApplication.taskManager().addTask(self.address_task)

            def on_altitude(value, error):
                try:
                    if error:
                        if self.logger:
                            self.logger.warning(f"Altimetry error: {error}")
                        self.dialog.set_altitude(None)
                        self.iface.messageBar().pushWarning(
                            "Altimetria", error
                        )
                    else:
                        if self.logger:
                            self.logger.debug(f"Altimetry result: {value}")
                        self.dialog.set_altitude(value)
                except Exception as e2:
                    if self.logger:
                        self.logger.error(f"on_altitude handler error: {e2}")

            self.alt_task = AltimetriaTask(lat, lon, on_altitude)
            QgsApplication.taskManager().addTask(self.alt_task)

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    def _cancel_task(self, task):
        if task and not sip.isdeleted(task):
            if not task.isCanceled():
                task.cancel()
