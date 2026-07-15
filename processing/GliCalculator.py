# -*- coding: utf-8 -*-
import os

from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterBand,
    QgsProcessingMultiStepFeedback,
)
import processing

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.OtherFilesManager import OtherFilesManager
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class GliCalculator(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Calcula o GLI (Green Leaf Index)
    a partir de um mosaico RGB(A) (3 ou 4 bandas).
    GLI = (2*G - R - B) / (2*G + R + B)

    Tratamento de banda alpha:
      - Se identificar banda alpha (banda 4), pixel valido se alpha > 250,
        caso contrario define como nodata (-9999).
      - Se nao houver banda alpha, verifica nodata existente no raster.

    Fluxo:
      [Opcional] Step 0: gdal:warpreproject (reamostragem)
      Step 1: gdal:translate (extrai bandas RGB / RGBA, identifica alpha/nodata)
      Step 2: gdal:rastercalculator (calculo GLI com Float32, tratando alpha/nodata)
      Step 3: native:setlayerstyle (aplica estilo QML de 8 classes)
    """

    TOOL_KEY = ToolKey.GLI_CALCULATOR
    ALGORITHM_NAME = "gli_calculator"
    ALGORITHM_DISPLAY_NAME = STR.GLI_CALCULATOR_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = "cadmus_icon.ico"
    INSTRUCTIONS_FILE = "gli_calculator.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="GliCalculator", level="DEBUG")

    INPUT_RASTER = "INPUT_RASTER"
    BAND_RED = "BAND_RED"
    BAND_GREEN = "BAND_GREEN"
    BAND_BLUE = "BAND_BLUE"
    TARGET_RESOLUTION = "TARGET_RESOLUTION"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = BaseProcessingAlgorithm.PARAM_DISPLAY_HELP
    OPEN_OUTPUT_FOLDER = BaseProcessingAlgorithm.PARAM_OPEN_OUTPUT_FOLDER

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo GliCalculator...")
        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER, STR.INPUT_RASTER_RGB_GLI
            )
        )

        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_RED,
                "Banda R (Red)",
                parentLayerParameterName=self.INPUT_RASTER,
                defaultValue=self.prefs.get("band_red", 1),
            )
        )

        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_GREEN,
                "Banda G (Green)",
                parentLayerParameterName=self.INPUT_RASTER,
                defaultValue=self.prefs.get("band_green", 2),
            )
        )

        self.addParameter(
            QgsProcessingParameterBand(
                self.BAND_BLUE,
                "Banda B (Blue)",
                parentLayerParameterName=self.INPUT_RASTER,
                defaultValue=self.prefs.get("band_blue", 3),
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.TARGET_RESOLUTION,
                "Reamostragem (resolucao alvo em metros, 0=original)",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("target_resolution", 0.0),
                minValue=0.0,
            )
        )

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, STR.GLI))

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

    def _detect_alpha_and_nodata(self, raster_path: str):
        """
        Abre o raster com GDAL e identifica:
          - Se possui banda alpha (banda 4 com color interpretation AlphaBand)
          - Se possui nodata definido na banda 1

        Retorna (has_alpha: bool, nodata_value: float|None)
        """
        from osgeo import gdal, gdalconst

        ds = gdal.Open(raster_path, gdal.GA_ReadOnly)
        if ds is None:
            return False, None

        n_bands = ds.RasterCount
        has_alpha = False

        if n_bands >= 4:
            band4 = ds.GetRasterBand(4)
            # Verifica color interpretation
            color_interp = band4.GetColorInterpretation()
            has_alpha = color_interp == gdalconst.GCI_AlphaBand

            # Fallback: verifica descricao da banda
            if not has_alpha:
                desc = (band4.GetDescription() or "").lower()
                has_alpha = "alpha" in desc or "transparency" in desc

        # Verifica nodata na banda 1
        nodata_value = None
        if n_bands >= 1:
            band1 = ds.GetRasterBand(1)
            nd_val = band1.GetNoDataValue()
            if nd_val is not None:
                nodata_value = float(nd_val)

        ds = None
        return has_alpha, nodata_value

    def processAlgorithm(self, params, context, feedback):
        self.logger.debug("Iniciando processAlgorithm do GliCalculator...")

        try:
            # --- Leitura dos parametros ---
            raster = self.parameterAsRasterLayer(params, self.INPUT_RASTER, context)
            if not raster or not raster.isValid():
                raise QgsProcessingException("Raster RGB invalido ou nao encontrado.")

            band_red = self.parameterAsInt(params, self.BAND_RED, context)
            band_green = self.parameterAsInt(params, self.BAND_GREEN, context)
            band_blue = self.parameterAsInt(params, self.BAND_BLUE, context)
            target_res = self.parameterAsDouble(params, self.TARGET_RESOLUTION, context)
            open_output_folder = self.parameterAsBool(
                params, self.OPEN_OUTPUT_FOLDER, context
            )
            display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)
            output_path = self.parameterAsOutputLayer(params, self.OUTPUT, context)

            needs_resample = target_res > 0.0

            # steps: warp(0), translate_rgb(1), calculator(2), setlayerstyle(3)
            steps = 4 if needs_resample else 3
            multi_feedback = QgsProcessingMultiStepFeedback(steps, feedback)

            # --- Banner inicial ---
            self._push_banner(feedback, "CALCULADORA GLI - CADMUS")
            feedback.pushInfo("")
            feedback.pushInfo("Formula: GLI = (2*G - R - B) / (2*G + R + B)")
            feedback.pushInfo("")
            self._push_info_line(feedback, "Raster de entrada", raster.source())
            self._push_info_line(feedback, "Banda R (Red)", str(band_red))
            self._push_info_line(feedback, "Banda G (Green)", str(band_green))
            self._push_info_line(feedback, "Banda B (Blue)", str(band_blue))
            if needs_resample:
                self._push_info_line(feedback, "Resolucao alvo", f"{target_res}m")
            else:
                feedback.pushInfo("Resolucao alvo: original (sem reamostragem)")
            self._push_info_line(feedback, "Output", output_path)
            feedback.pushInfo("")

            step_index = 0

            # ===================================================================
            # STEP 0 (opcional): Reamostragem via gdal:warpreproject
            # ===================================================================
            working_raster = raster.source()
            import tempfile

            temp_dir = tempfile.gettempdir()

            if needs_resample:
                multi_feedback.setCurrentStep(step_index)
                if multi_feedback.isCanceled():
                    return {}

                feedback.pushInfo(
                    f"[Step {step_index + 1}/{steps}] Reamostrando para {target_res}m..."
                )

                resampled_path = os.path.join(
                    temp_dir, f"gli_resampled_{os.path.basename(raster.source())}"
                )

                warp_params = {
                    "INPUT": raster.source(),
                    "SOURCE_CRS": None,
                    "TARGET_CRS": None,
                    "RESAMPLING": 0,
                    "NODATA": None,
                    "TARGET_RESOLUTION": target_res,
                    "OPTIONS": "",
                    "DATA_TYPE": 0,
                    "TARGET_EXTENT": None,
                    "TARGET_EXTENT_CRS": None,
                    "MULTITHREADING": True,
                    "OUTPUT": resampled_path,
                }
                self.logger.debug(
                    f"Reamostrando raster para resolucao {target_res}m..."
                )
                warp_result = processing.run(
                    "gdal:warpreproject",
                    warp_params,
                    context=context,
                    feedback=multi_feedback,
                    is_child_algorithm=True,
                )
                working_raster = warp_result.get("OUTPUT", resampled_path)
                feedback.pushInfo(f"Raster reamostrado: {working_raster}")
                feedback.pushInfo("")
                step_index += 1

            # ===================================================================
            # STEP 1: Identificar alpha/nodata e extrair bandas necessarias
            #   - Se tiver banda alpha (RGBA), preserva as 4 bandas
            #   - Se tiver nodata mas sem alpha, extrai RGB puro
            #   - Se for RGB puro sem nodata, usa como esta
            # ===================================================================
            multi_feedback.setCurrentStep(step_index)
            if multi_feedback.isCanceled():
                return {}

            # Detecta alpha e nodata
            has_alpha, nodata_value = self._detect_alpha_and_nodata(working_raster)

            if has_alpha:
                feedback.pushInfo(
                    f"[Step {step_index + 1}/{steps}] Banda alpha detectada. "
                    "Preservando 4 bandas (RGBA)..."
                )
                feedback.pushInfo(
                    "Tratamento: pixel valido se alpha > 250, "
                    "caso contrario definido como nodata."
                )
                feedback.pushInfo("")

                alpha_path = os.path.join(
                    temp_dir, f"gli_rgba_{os.path.basename(working_raster)}"
                )

                # Extrai todas as 4 bandas (RGBA)
                translate_params = {
                    "INPUT": working_raster,
                    "TARGET_CRS": None,
                    "NODATA": None,
                    "COPY_SUBDATASETS": False,
                    "OPTIONS": "",
                    "EXTRA": "-b 1 -b 2 -b 3 -b 4",
                    "DATA_TYPE": 0,
                    "TARGET_EXTENT": None,
                    "TARGET_EXTENT_CRS": None,
                    "OUTPUT": alpha_path,
                }
                translate_result = processing.run(
                    "gdal:translate",
                    translate_params,
                    context=context,
                    feedback=multi_feedback,
                    is_child_algorithm=True,
                )
                working_raster = translate_result.get("OUTPUT", alpha_path)
                feedback.pushInfo(f"Raster RGBA (4 bandas): {working_raster}")

            else:
                from osgeo import gdal as _gdal

                ds_check = _gdal.Open(working_raster, _gdal.GA_ReadOnly)
                n_bands = ds_check.RasterCount if ds_check else 3
                ds_check = None

                if nodata_value is not None:
                    feedback.pushInfo(
                        f"[Step {step_index + 1}/{steps}] Sem banda alpha. "
                        f"Nodata detectado: {nodata_value}."
                    )
                else:
                    feedback.pushInfo(
                        f"[Step {step_index + 1}/{steps}] Raster RGB puro "
                        f"({n_bands} banda(s)). Sem alpha nem nodata."
                    )

                # Se tiver mais de 3 bandas (ex: 4 mas sem ser alpha), extrai so RGB
                if n_bands > 3:
                    feedback.pushInfo("Extraindo apenas as 3 primeiras bandas (RGB)...")
                    rgb_path = os.path.join(
                        temp_dir, f"gli_rgb_{os.path.basename(working_raster)}"
                    )
                    translate_params = {
                        "INPUT": working_raster,
                        "TARGET_CRS": None,
                        "NODATA": nodata_value if nodata_value is not None else None,
                        "COPY_SUBDATASETS": False,
                        "OPTIONS": "",
                        "EXTRA": "-b 1 -b 2 -b 3",
                        "DATA_TYPE": 0,
                        "TARGET_EXTENT": None,
                        "TARGET_EXTENT_CRS": None,
                        "OUTPUT": rgb_path,
                    }
                    translate_result = processing.run(
                        "gdal:translate",
                        translate_params,
                        context=context,
                        feedback=multi_feedback,
                        is_child_algorithm=True,
                    )
                    working_raster = translate_result.get("OUTPUT", rgb_path)
                    feedback.pushInfo(f"Raster RGB puro (3 bandas): {working_raster}")
                else:
                    feedback.pushInfo(
                        f"Raster ja tem {n_bands} banda(s). Utilizando como esta."
                    )

            feedback.pushInfo("")
            step_index += 1

            # ===================================================================
            # STEP 2: Calcular GLI via gdal:rastercalculator
            #   - Se 4 bandas (RGBA): usa formula com alpha mask
            #   - Se 3 bandas (RGB): formula padrao
            # ===================================================================
            multi_feedback.setCurrentStep(step_index)
            if multi_feedback.isCanceled():
                return {}

            feedback.pushInfo(
                f"[Step {step_index + 1}/{steps}] Calculando GLI via gdal:rastercalculator..."
            )

            # Verifica quantas bandas tem o raster de trabalho
            from osgeo import gdal as _gdal2

            ds_final = _gdal2.Open(working_raster, _gdal2.GA_ReadOnly)
            current_nbands = ds_final.RasterCount if ds_final else 3
            ds_final = None

            gli_nodata = -9999.0

            if current_nbands >= 4:
                # Temos banda alpha: usa formula que mascara alpha <= 250 como nodata
                feedback.pushInfo(
                    "Usando formula GLI com tratamento de banda alpha (banda 4)..."
                )
                formula = (
                    "((D > 250) * ((B*2.0 - A - C) / (B*2.0 + A + C + 1e-10) "
                    "* (abs(B*2.0 + A + C) > 1e-10))) "
                    "+ ((D <= 250) * " + str(gli_nodata) + ")"
                )
                calc_params = {
                    "INPUT_A": working_raster,
                    "BAND_A": 1,
                    "INPUT_B": working_raster,
                    "BAND_B": 2,
                    "INPUT_C": working_raster,
                    "BAND_C": 3,
                    "INPUT_D": working_raster,
                    "BAND_D": 4,
                    "INPUT_E": None,
                    "BAND_E": None,
                    "INPUT_F": None,
                    "BAND_F": None,
                    "FORMULA": formula,
                    "NO_DATA": gli_nodata,
                    "RTYPE": 5,  # Float32
                    "EXTENT_OPT": 0,
                    "PROJWIN": None,
                    "OPTIONS": "",
                    "EXTRA": "",
                    "OUTPUT": output_path,
                }
            else:
                # Sem alpha: formula padrao, passa nodata se existir
                feedback.pushInfo("Usando formula GLI padrao (3 bandas RGB)...")
                formula = (
                    "(B*2.0 - A - C) / (B*2.0 + A + C + 1e-10) "
                    "* (abs(B*2.0 + A + C) > 1e-10)"
                )
                calc_params = {
                    "INPUT_A": working_raster,
                    "BAND_A": 1,
                    "INPUT_B": working_raster,
                    "BAND_B": 2,
                    "INPUT_C": working_raster,
                    "BAND_C": 3,
                    "INPUT_D": None,
                    "BAND_D": None,
                    "INPUT_E": None,
                    "BAND_E": None,
                    "INPUT_F": None,
                    "BAND_F": None,
                    "FORMULA": formula,
                    "NO_DATA": gli_nodata if nodata_value is not None else None,
                    "RTYPE": 5,  # Float32
                    "EXTENT_OPT": 0,
                    "PROJWIN": None,
                    "OPTIONS": "",
                    "EXTRA": "",
                    "OUTPUT": output_path,
                }

            self.logger.debug("Executando gdal:rastercalculator para GLI...")
            calc_result = processing.run(
                "gdal:rastercalculator",
                calc_params,
                context=context,
                feedback=multi_feedback,
                is_child_algorithm=True,
            )

            calc_output = calc_result.get("OUTPUT", output_path)
            feedback.pushInfo("GLI calculado com sucesso!")
            feedback.pushInfo("")
            step_index += 1

            # --- Exibe interpretacao ---
            for line in STR.GLI_INTERPRETATION.split("\n"):
                feedback.pushInfo(line)
            feedback.pushInfo("")

            # ===================================================================
            # STEP 3: Aplicar estilo de cores via native:setlayerstyle
            # ===================================================================
            multi_feedback.setCurrentStep(step_index)
            if multi_feedback.isCanceled():
                return {}

            feedback.pushInfo(
                f"[Step {step_index + 1}/{steps}] Aplicando estilo de cores GLI..."
            )

            self._apply_qml_style(
                feedback=multi_feedback,
                logger=self.logger,
                calc_output=calc_output,
                qml_filename=OtherFilesManager.INDICE_GLI_STYLE,
                context=context,
            )

            feedback.pushInfo("")

            # --- Salva preferencias ---
            self.prefs.update(
                {
                    "band_red": band_red,
                    "band_green": band_green,
                    "band_blue": band_blue,
                    "target_resolution": target_res,
                    "open_output_folder": open_output_folder,
                    "display_help": display_help,
                }
            )
            self.save_preferences()

            # --- Abre pasta se solicitado ---
            if (
                output_path
                and isinstance(output_path, str)
                and not output_path.startswith("memory:")
            ):
                out_folder = os.path.dirname(output_path)
                if out_folder and open_output_folder:
                    self.open_folder_in_explorer(out_folder)

            feedback.pushInfo("Processamento concluido com sucesso.")
            self.logger.info("Processamento GLI concluido com sucesso.")
            return {self.OUTPUT: output_path}

        except QgsProcessingException as e:
            self.logger.error(f"Erro de processamento: {e}")
            raise
        except Exception as e:
            msg = f"Erro nao tratado em processAlgorithm: {e}"
            self.logger.error(msg)
            raise QgsProcessingException(msg)
