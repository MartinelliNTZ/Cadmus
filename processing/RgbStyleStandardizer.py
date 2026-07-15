# -*- coding: utf-8 -*-

from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterLayer,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..utils.ToolKeys import ToolKey
from ..utils.raster.RasterLayerRendering import RasterLayerRendering
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RgbStyleStandardizer(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Aplica padronizacao de estilo por percentil
    em um raster RGB multibanda. Calcula os percentis das 3 primeiras bandas,
    gera estilo QML sidecar, salva copia em temp/styles e aplica na camada.
    """

    TOOL_KEY = ToolKey.RGB_STYLE_STANDARDIZER
    ALGORITHM_NAME = "rgb_style_standardizer"
    ALGORITHM_DISPLAY_NAME = STR.RGB_STYLE_STANDARDIZER_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = "cadmus_icon.ico"
    INSTRUCTIONS_FILE = "rgb_style_standardizer.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="RgbStyleStandardizer", level="DEBUG")

    INPUT_RASTER = "INPUT_RASTER"
    LOWER_PCT = "LOWER_PCT"
    UPPER_PCT = "UPPER_PCT"
    DISPLAY_HELP = BaseProcessingAlgorithm.PARAM_DISPLAY_HELP

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo RgbStyleStandardizer...")
        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_RASTER, STR.INPUT_RASTER_RGB)
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LOWER_PCT,
                "Percentil inferior (%)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("lower_pct", 2.0),
                minValue=0.0,
                maxValue=50.0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.UPPER_PCT,
                "Percentil superior (%)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("upper_pct", 98.0),
                minValue=50.0,
                maxValue=100.0,
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
        self.logger.debug("Iniciando processAlgorithm do RgbStyleStandardizer...")

        try:
            raster = self.parameterAsRasterLayer(params, self.INPUT_RASTER, context)
            if not raster or not raster.isValid():
                raise QgsProcessingException("Raster RGB invalido ou nao encontrado.")

            lower_pct = self.parameterAsDouble(params, self.LOWER_PCT, context)
            upper_pct = self.parameterAsDouble(params, self.UPPER_PCT, context)
            display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)

            raster_path = raster.source()

            # --- Banner inicial ---
            self._push_banner(feedback, "PADRONIZADOR DE ESTILO RGB - CADMUS")
            self._push_info_line(feedback, "Raster", raster_path)
            self._push_info_line(feedback, "Percentis", f"{lower_pct}% - {upper_pct}%")
            feedback.pushInfo("")

            # --- Pipeline completo via RasterLayerRendering ---
            result = RasterLayerRendering.generate_percentil_multiband_style(
                raster_path=raster_path,
                band_indices=[1, 2, 3],
                lower_pct=lower_pct,
                upper_pct=upper_pct,
                alpha_band=-1,
                opacity=1.0,
                algorithm="StretchToMinimumMaximum",
                layer=raster,
                feedback=feedback,
                tool_key=self.TOOL_KEY,
            )
            self.logger.debug(f"Resultado do processamento: {result}")

            # --- Salvar preferencias ---
            self.prefs.update({
                "lower_pct": lower_pct,
                "upper_pct": upper_pct,
                "display_help": display_help,
            })
            self.save_preferences()

            feedback.pushInfo("Processamento concluido com sucesso.")
            return {}

        except QgsProcessingException as e:
            self.logger.error(f"Erro de processamento: {e}")
            raise
        except ImportError as e:
            msg = f"Biblioteca necessaria nao disponivel: {e}"
            self.logger.error(msg)
            raise QgsProcessingException(msg)
        except Exception as e:
            msg = f"Erro nao tratado em processAlgorithm: {e}"
            self.logger.error(msg)
            raise QgsProcessingException(msg)
