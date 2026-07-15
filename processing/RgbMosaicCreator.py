# -*- coding: utf-8 -*-
import os

from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterBand,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..utils.ToolKeys import ToolKey
from ..utils.raster.RasterLayerProcessing import RasterLayerProcessing
from ..utils.raster.RasterLayerMetrics import RasterLayerMetrics
from ..utils.raster.RasterLayerRendering import RasterLayerRendering
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RgbMosaicCreator(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Cria um mosaico RGB a partir de 3 rasters individuais
    (bandas R, G, B), com opcao de criar banda alpha para valores NoData.
    Ao final, salva o estilo QML na pasta temp e aplica no raster de saida.
    """

    TOOL_KEY = ToolKey.RGB_MOSAIC_CREATOR
    ALGORITHM_NAME = "rgb_mosaic_creator"
    ALGORITHM_DISPLAY_NAME = STR.RGB_MOSAIC_CREATOR_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = "cadmus_icon.ico"
    INSTRUCTIONS_FILE = "rgb_mosaic_creator.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="RgbMosaicCreator", level="DEBUG")

    INPUT_R = "INPUT_R"
    BAND_R = "BAND_R"
    INPUT_G = "INPUT_G"
    BAND_G = "BAND_G"
    INPUT_B = "INPUT_B"
    BAND_B = "BAND_B"
    CREATE_ALPHA = "CREATE_ALPHA"
    ALPHA_NODATA = "ALPHA_NODATA"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = BaseProcessingAlgorithm.PARAM_DISPLAY_HELP
    OPEN_OUTPUT_FOLDER = BaseProcessingAlgorithm.PARAM_OPEN_OUTPUT_FOLDER

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo RgbMosaicCreator...")
        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_R, STR.INPUT_RASTER_RED_BAND)
        )
        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_R,
                STR.BAND_RED_LABEL,
                parentLayerParameterName=self.INPUT_R,
                defaultValue=self.prefs.get("band_r", 1),
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_G, STR.INPUT_RASTER_GREEN_BAND)
        )
        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_G,
                STR.BAND_GREEN_LABEL,
                parentLayerParameterName=self.INPUT_G,
                defaultValue=self.prefs.get("band_g", 1),
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.INPUT_B, STR.INPUT_RASTER_BLUE_BAND)
        )
        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_B,
                STR.BAND_BLUE_LABEL,
                parentLayerParameterName=self.INPUT_B,
                defaultValue=self.prefs.get("band_b", 1),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.CREATE_ALPHA,
                STR.CREATE_ALPHA_BAND,
                defaultValue=self.prefs.get("create_alpha", True),
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ALPHA_NODATA,
                STR.ALPHA_NODATA_VALUE,
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("alpha_nodata", 0.0),
                optional=True,
            )
        )

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, STR.RGB_COMPOSITE))

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
        self.logger.debug("Iniciando processAlgorithm do RgbMosaicCreator...")

        try:
            raster_r = self.parameterAsRasterLayer(params, self.INPUT_R, context)
            raster_g = self.parameterAsRasterLayer(params, self.INPUT_G, context)
            raster_b = self.parameterAsRasterLayer(params, self.INPUT_B, context)

            if not raster_r or not raster_r.isValid():
                raise QgsProcessingException("Raster R (Vermelho) invalido ou nao encontrado.")
            if not raster_g or not raster_g.isValid():
                raise QgsProcessingException("Raster G (Verde) invalido ou nao encontrado.")
            if not raster_b or not raster_b.isValid():
                raise QgsProcessingException("Raster B (Azul) invalido ou nao encontrado.")

            band_r = self.parameterAsInt(params, self.BAND_R, context)
            band_g = self.parameterAsInt(params, self.BAND_G, context)
            band_b = self.parameterAsInt(params, self.BAND_B, context)

            create_alpha = self.parameterAsBool(params, self.CREATE_ALPHA, context)
            alpha_nodata = self.parameterAsDouble(params, self.ALPHA_NODATA, context)

            open_output_folder = self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context)
            display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)
            output_path = self.parameterAsOutputLayer(params, self.OUTPUT, context)

            # --- Banner inicial ---
            self._push_banner(feedback, "CRIADOR DE MOSAICO RGB - CADMUS")
            self._push_info_line(feedback, "R (Red)", f"{raster_r.source()}  | Banda {band_r}")
            self._push_info_line(feedback, "G (Green)", f"{raster_g.source()}  | Banda {band_g}")
            self._push_info_line(feedback, "B (Blue)", f"{raster_b.source()}  | Banda {band_b}")
            self._push_info_line(feedback, "Alpha", f"{'Sim' if create_alpha else 'Nao'}  |  NoData: {alpha_nodata}")
            self._push_info_line(feedback, "Saida", output_path)

            # --- FASE 1: Extrair bandas usando RasterLayerProcessing ---
            feedback.pushInfo("")
            feedback.pushInfo("--- FASE 1: Extraindo bandas individuais ---")
            path_r = RasterLayerProcessing.extract_band(
                raster_r.source(), band_r, tool_key=self.TOOL_KEY
            )
            path_g = RasterLayerProcessing.extract_band(
                raster_g.source(), band_g, tool_key=self.TOOL_KEY
            )
            path_b = RasterLayerProcessing.extract_band(
                raster_b.source(), band_b, tool_key=self.TOOL_KEY
            )
            feedback.pushInfo("Bandas extraidas com sucesso.")

            # --- FASE 2: Estatisticas via RasterLayerMetrics ---
            feedback.pushInfo("--- FASE 2: Calculando percentis das bandas ---")
            min_max = RasterLayerMetrics.get_global_min_max_from_rasters(
                [
                    (path_r, 1),
                    (path_g, 1),
                    (path_b, 1),
                ],
                lower_pct=2.0,
                upper_pct=98.0,
                tool_key=self.TOOL_KEY,
            )
            global_min, global_max = min_max
            feedback.pushInfo(f"Global min={global_min:.7f}  Global max={global_max:.7f}")

            # --- FASE 3: Criar banda alpha (se solicitado) ---
            alpha_path = None
            if create_alpha and alpha_nodata is not None:
                feedback.pushInfo("--- FASE 3: Criando banda alpha ---")
                alpha_path = RasterLayerProcessing.create_alpha_mask(
                    path_r, alpha_nodata, tool_key=self.TOOL_KEY
                )
                feedback.pushInfo("Banda alpha criada.")

            # --- FASE 4: Compor mosaico RGB via RasterLayerProcessing ---
            feedback.pushInfo("--- FASE 4: Compondo mosaico RGB ---")
            band_files = [path_r, path_g, path_b]
            RasterLayerProcessing.compose_multiband_raster(
                band_files=band_files,
                output_path=output_path,
                create_alpha=create_alpha,
                alpha_band_path=alpha_path,
                tool_key=self.TOOL_KEY,
            )
            feedback.pushInfo("Mosaico RGB criado com sucesso!")

            # --- FASE 5: Gerar e aplicar estilo QML via pipeline centralizado ---
            feedback.pushInfo("--- FASE 5: Gerando e aplicando estilo QML ---")
            alpha_band = 4 if (create_alpha and alpha_nodata is not None) else -1

            result = RasterLayerRendering.generate_percentil_multiband_style(
                raster_path=output_path,
                band_indices=[1, 2, 3],
                min_value=global_min,
                max_value=global_max,
                alpha_band=alpha_band,
                opacity=1.0,
                algorithm="StretchToMinimumMaximum",
                layer=None,  # Vamos aplicar separadamente com registro no context
                feedback=feedback,
                tool_key=self.TOOL_KEY,
            )

            # --- FASE 6: Criar layer de saida e aplicar estilo com registro no context ---
            feedback.pushInfo("--- FASE 6: Registrando layer de saida com estilo via apply_qml_to_layer ---")
            if result["qml_path"] and os.path.isfile(result["qml_path"]):
                RasterLayerRendering.apply_qml_to_layer(
                    raster_path=output_path,
                    qml_path=result["qml_path"],
                    context=context,
                    feedback=feedback,
                    layer_name="RGB Mosaic",
                    tool_key=self.TOOL_KEY,
                )

            # --- Salvar preferências ---
            self.prefs.update({
                "band_r": band_r,
                "band_g": band_g,
                "band_b": band_b,
                "create_alpha": create_alpha,
                "alpha_nodata": alpha_nodata,
                "open_output_folder": open_output_folder,
                "display_help": display_help,
            })
            self.save_preferences()

            # --- Abrir pasta de saída ---
            if output_path and isinstance(output_path, str) and not output_path.startswith("memory:"):
                out_folder = os.path.dirname(output_path)
                if out_folder and open_output_folder:
                    self.open_folder_in_explorer(out_folder)

            feedback.pushInfo("Processamento concluido com sucesso.")
            return {self.OUTPUT: output_path}

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
