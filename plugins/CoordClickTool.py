from qgis.gui import QgsMapTool
from qgis.core import QgsApplication
import sip

from ..core.task.ReverseGeocodeTask import ReverseGeocodeTask
from ..core.task.AltimetryTask import AltimetriaTask
from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.ExecutionContext import ExecutionContext
from ..core.engine_tasks.ReverseGeocodeStep import ReverseGeocodeStep
from ..core.engine_tasks.AltimetryStep import AltimetryStep
from ..core.engine_tasks.ParallelStep import ParallelStep
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from .CoorResultDialog import CoordResultDialog
from ..core.config.LogUtils import LogUtils


class CoordClickTool(QgsMapTool):

    def __init__(self, iface):
        super().__init__(iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.dialog = None
        self.address_task = None
        self.alt_task = None

        self.logger = LogUtils(
            tool="coord_click", class_name="CoordClickTool", level=LogUtils.DEBUG
        )
        self.logger.debug("CoordClickTool initialized")

    def canvasReleaseEvent(self, event):

        self.logger.debug("canvasReleaseEvent triggered")

        snap = self.canvas.snappingUtils().snapToMap(event.pos())
        point = snap.point() if snap.isValid() else self.toMapCoordinates(event.pos())

        info = VectorLayerProjection.get_coordinate_info(
            point, self.canvas.mapSettings().destinationCrs()
        )

        # -----------------------------
        # VIEW
        # -----------------------------
        if not self.dialog or not self.dialog.isVisible():
            try:
                self.logger.debug("Creating CoordResultDialog")
                self.dialog = CoordResultDialog(self.iface, info)
                self.dialog.show()
                # ensure dialog is brought to front

                self.dialog.raise_()
                self.dialog.activateWindow()

                self.logger.debug("CoordResultDialog shown")
            except Exception as e:
                # fallback: notify user
                self.logger.error(f"Erro ao abrir diálogo de coordenadas: {e}")
        else:
            try:
                self.logger.debug("Updating existing CoordResultDialog")
                self.dialog.update_info(info)
                self.dialog.raise_()
                self.dialog.activateWindow()
            except Exception as e:
                self.logger.error(f"Erro ao atualizar diálogo: {e}")

        # -----------------------------
        # Cancela tasks antigas
        # -----------------------------
        self._cancel_task(self.address_task)
        self._cancel_task(self.alt_task)

        # Se o diálogo não foi criado/atualizado com sucesso, não iniciar tasks.
        if not self.dialog:
            self.logger.debug("Dialog not available; skipping tasks scheduling")
            return

        lat, lon = info["lat"], info["lon"]

        # -----------------------------
        # -----------------------------
        # Use AsyncPipelineEngine with Steps for reverse geocode + altimetry
        # -----------------------------
        try:
            # cancel previous pipeline if running
            if (
                hasattr(self, "pipeline_engine") and self.pipeline_engine and self.pipeline_engine.is_running()
            ):
                self.pipeline_engine.cancel()
            context = ExecutionContext(
                tool_key="coord_click",
                lat=lat,
                lon=lon,
            )

            # Reverse geocode and altimetry are independent — run in parallel
            # Both steps read lat/lon directly from context (atributos canônicos)
            steps = [
                ParallelStep(
                    [ReverseGeocodeStep(), AltimetryStep()],
                    description="coord_click_geo_alt",
                )
            ]

            self.pipeline_engine = AsyncPipelineEngine(
                steps,
                context,
                on_finished=self._on_pipeline_finished,
                on_error=self._on_pipeline_error,
            )
            self.pipeline_engine.start()
        except Exception as e:
            # Fallback to previous behavior: schedule tasks individually
            self.logger.warning(f"Pipeline failed, falling back to legacy tasks: {e}")

            def on_address(result, error):
                try:
                    if error:
                        self.logger.warning(f"Reverse geocode error: {error}")
                        self.dialog.set_address(None)
                        self.iface.messageBar().pushWarning("Geocodificação", error)
                    else:
                        self.logger.debug(f"Reverse geocode result: {result}")
                        self.dialog.set_address(result)
                except Exception as e2:
                    self.logger.error(f"on_address handler error: {e2}")

            self.address_task = ReverseGeocodeTask(lat, lon, tool_key="coord_click")
            self.address_task.on_success = lambda result: on_address(result, None)
            self.address_task.on_error = lambda exc: on_address(None, str(exc) if exc else "Unknown error")
            QgsApplication.taskManager().addTask(self.address_task)

            def on_altitude(value, error):
                try:
                    if error:
                        self.logger.warning(f"Altimetry error: {error}")
                        self.dialog.set_altitude(None)
                        self.iface.messageBar().pushWarning("Altimetria", error)
                    else:
                        self.logger.debug(f"Altimetry result: {value}")
                        self.dialog.set_altitude(value)
                except Exception as e2:
                    self.logger.error(f"on_altitude handler error: {e2}")

            self.alt_task = AltimetriaTask(lat, lon, tool_key="coord_click")
            self.alt_task.on_success = lambda result: on_altitude(result, None)
            self.alt_task.on_error = lambda exc: on_altitude(None, str(exc) if exc else "Unknown error")
            QgsApplication.taskManager().addTask(self.alt_task)

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    # --------------------------------------------------
    # Pipeline callbacks (desacoplados — lêem dados do contexto)
    # --------------------------------------------------
    def _on_pipeline_finished(self, context):
        """Callback chamado pela engine ao finalizar pipeline com sucesso."""
        try:
            address_data = context.get_result("address_data")
            if address_data and self.dialog:
                self.dialog.set_address(address_data)
                self.logger.debug(f"Address set from pipeline: {address_data}")

            altitude = context.get_result("altitude")
            if altitude is not None and self.dialog:
                self.dialog.set_altitude(altitude)
                self.logger.debug(f"Altitude set from pipeline: {altitude}")
        except Exception as e:
            self.logger.error(f"Pipeline finished callback error: {e}")

    def _on_pipeline_error(self, errors):
        """Callback chamado pela engine ao finalizar pipeline com erro."""
        try:
            for err in errors:
                self.logger.warning(f"Pipeline error: {err}")
                if self.dialog:
                    self.dialog.set_address(None)
                    self.dialog.set_altitude(None)
                self.iface.messageBar().pushWarning("Pipeline", str(err))
        except Exception as e:
            self.logger.error(f"Pipeline error callback error: {e}")

    def _cancel_task(self, task):
        if task and not sip.isdeleted(task):
            if not task.isCanceled():
                task.cancel()
