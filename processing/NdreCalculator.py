# -*- coding: utf-8 -*-
import os

from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterBand,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingMultiStepFeedback,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.OtherFilesManager import OtherFilesManager
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class NdreCalculator(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Calcula o NDRE (Normalized Difference Red Edge Index)
    a partir de dois rasters (NIR e RedEdge).
    NDRE = (NIR - RedEdge) / (NIR + RedEdge)

    Fluxo:
      Step 1: QgsRasterCalculator (calculo NDRE com Float32)
      Step 2: native:setlayerstyle (aplica estilo QML de 8 classes)
    """

    TOOL_KEY = ToolKey.NDRE_CALCULATOR
    ALGORITHM_NAME = "ndre_calculator"
    ALGORITHM_DISPLAY_NAME = STR.NDRE_CALCULATOR_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = "cadmus_icon.ico"
    INSTRUCTIONS_FILE = "ndre_calculator.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="NdreCalculator", level="DEBUG")

    INPUT_NIR = "INPUT_NIR"
    NIR_BAND = "NIR_BAND"
    INPUT_REDEDGE = "INPUT_REDEDGE"
    REDEDGE_BAND = "REDEDGE_BAND"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = BaseProcessingAlgorithm.PARAM_DISPLAY_HELP
    OPEN_OUTPUT_FOLDER = BaseProcessingAlgorithm.PARAM_OPEN_OUTPUT_FOLDER

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo NdreCalculator...")
        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_NIR, STR.INPUT_RASTER_NIR_NDRE)
        )
        self.addParameter(
            QgsProcessingParameterBand(
                self.NIR_BAND,
                STR.BAND_NIR,
                parentLayerParameterName=self.INPUT_NIR,
                defaultValue=self.prefs.get("nir_band", 1),
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_REDEDGE, STR.INPUT_RASTER_REDEDGE)
        )
        self.addParameter(
            QgsProcessingParameterBand(
                self.REDEDGE_BAND,
                STR.BAND_REDEDGE,
                parentLayerParameterName=self.INPUT_REDEDGE,
                defaultValue=self.prefs.get("rededge_band", 1),
            )
        )

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, STR.NDRE))

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN_OUTPUT_FOLDER,
                self.PARAM_OPEN_OUTPUT_FOLDER_LABEL,
                defaultValue=self.prefs.get("open_output_folder", True),
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                self.PARAM_DISPLAY_HELP_LABEL,
                defaultValue=self.prefs.get("display_help", True),
            )
        )

    def processAlgorithm(self, params, context, feedback):
        self.logger.debug("Iniciando processAlgorithm do NdreCalculator...")

        try:
            nir_raster = self.parameterAsRasterLayer(params, self.INPUT_NIR, context)
            rededge_raster = self.parameterAsRasterLayer(params, self.INPUT_REDEDGE, context)

            if not nir_raster or not nir_raster.isValid():
                raise QgsProcessingException("Raster NIR invalido ou nao encontrado.")
            if not rededge_raster or not rededge_raster.isValid():
                raise QgsProcessingException("Raster RedEdge invalido ou nao encontrado.")

            nir_band = self.parameterAsInt(params, self.NIR_BAND, context)
            rededge_band = self.parameterAsInt(params, self.REDEDGE_BAND, context)

            open_output_folder = self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context)
            display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)
            output_path = self.parameterAsOutputLayer(params, self.OUTPUT, context)

            # steps: calculator(0), setlayerstyle(1)
            steps = 2
            multi_feedback = QgsProcessingMultiStepFeedback(steps, feedback)

            # --- Banner inicial ---
            self._push_banner(feedback, "CALCULADORA NDRE - CADMUS")
            feedback.pushInfo("")
            feedback.pushInfo("Formula: NDRE = (NIR - RedEdge) / (NIR + RedEdge)")
            feedback.pushInfo("")
            feedback.pushInfo("--- Bandas recomendadas por satelite ---")
            feedback.pushInfo("Sentinel-2: Banda 8 (NIR) e Banda 5 (RedEdge 1)")
            feedback.pushInfo("            Banda 8 (NIR) e Banda 6 (RedEdge 2)")
            feedback.pushInfo("            Banda 8 (NIR) e Banda 7 (RedEdge 3)")
            feedback.pushInfo("")
            self._push_info_line(feedback, "NIR raster", f"{nir_raster.source()}  | Banda {nir_band}")
            self._push_info_line(feedback, "RedEdge raster", f"{rededge_raster.source()}  | Banda {rededge_band}")
            self._push_info_line(feedback, "Output", output_path)
            feedback.pushInfo("")

            nir_extent = nir_raster.extent()
            rededge_extent = rededge_raster.extent()
            if not nir_extent.intersects(rededge_extent):
                feedback.reportError(
                    "ATENCAO: Os rasters NIR e RedEdge nao possuem extensoes sobrepostas. "
                    "O NDRE pode resultar em valores nulos."
                )

            step_index = 0

            # ===================================================================
            # STEP 1: Calcular NDRE via QgsRasterCalculator
            # ===================================================================
            multi_feedback.setCurrentStep(step_index)
            if multi_feedback.isCanceled():
                return {}

            from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry

            entry_nir = QgsRasterCalculatorEntry()
            entry_nir.raster = nir_raster
            entry_nir.bandNumber = nir_band
            entry_nir.ref = "NIR@1"

            entry_rededge = QgsRasterCalculatorEntry()
            entry_rededge.raster = rededge_raster
            entry_rededge.bandNumber = rededge_band
            entry_rededge.ref = "REDEDGE@1"

            entries = [entry_nir, entry_rededge]

            formula = (
                '("NIR@1" - "REDEDGE@1") / (abs("NIR@1" + "REDEDGE@1") + 1e-10) * '
                '("NIR@1" + "REDEDGE@1" != 0)'
            )

            feedback.pushInfo(f"[Step {step_index + 1}/{steps}] Formula NDRE: {formula}")
            feedback.pushInfo("Calculando NDRE...")

            calc = QgsRasterCalculator(
                formula,
                output_path,
                "GTiff",
                nir_raster.extent(),
                nir_raster.width(),
                nir_raster.height(),
                entries,
            )

            result = calc.processCalculation()
            if result != 0:
                msg = f"Erro no calculo NDRE. Codigo de erro: {result}"
                self.logger.error(msg)
                raise QgsProcessingException(msg)

            feedback.pushInfo("NDRE calculado com sucesso!")
            feedback.pushInfo("")
            feedback.pushInfo("Interpretacao dos valores NDRE:")
            feedback.pushInfo("  -1.0 a 0.0  : Agua, superficies nao vegetadas")
            feedback.pushInfo("   0.0 a 0.2  : Solo exposto, vegetacao esparsa")
            feedback.pushInfo("   0.2 a 0.5  : Vegetacao moderada")
            feedback.pushInfo("   0.5 a 1.0  : Vegetacao densa e saudavel")
            feedback.pushInfo("")
            step_index += 1

            # ===================================================================
            # STEP 2: Aplicar estilo de cores via native:setlayerstyle
            # ===================================================================
            multi_feedback.setCurrentStep(step_index)
            if multi_feedback.isCanceled():
                return {}

            feedback.pushInfo(f"[Step {step_index + 1}/{steps}] Aplicando estilo de cores NDRE...")

            self._apply_qml_style(
                feedback=multi_feedback,
                logger=self.logger,
                calc_output=output_path,
                qml_filename=OtherFilesManager.INDICE_NDRE_STYLE,
                context=context,
            )

            feedback.pushInfo("")

            self.prefs.update({
                "nir_band": nir_band,
                "rededge_band": rededge_band,
                "open_output_folder": open_output_folder,
                "display_help": display_help,
            })
            self.save_preferences()

            if output_path and isinstance(output_path, str) and not output_path.startswith("memory:"):
                out_folder = os.path.dirname(output_path)
                if out_folder and open_output_folder:
                    self.open_folder_in_explorer(out_folder)

            feedback.pushInfo("Processamento concluido com sucesso.")
            return {self.OUTPUT: output_path}

        except QgsProcessingException as e:
            self.logger.error(f"Erro de processamento: {e}")
            raise
        except Exception as e:
            msg = f"Erro nao tratado em processAlgorithm: {e}"
            self.logger.error(msg)
            raise QgsProcessingException(msg)
