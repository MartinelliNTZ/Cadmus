# -*- coding: utf-8 -*-
import os
import tempfile

from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import (
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsRasterLayer,
)

from ..core.config.LogUtils import LogUtils
from ..core.enum.ResamplingMethod import ResamplingMethod
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from ..utils.raster.RasterLayerProjection import RasterLayerProjection
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RasterWeightedAverage(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Calcula media ponderada entre 2 a 4 camadas raster.
    """

    TOOL_KEY = ToolKey.RASTER_WEIGHTED_AVERAGE
    ALGORITHM_NAME = "raster_weighted_average"
    ALGORITHM_DISPLAY_NAME = STR.RASTER_WEIGHTED_AVERAGE_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = im.RASTER_WEIGHTED_AVERAGE
    INSTRUCTIONS_FILE = "raster_mass_sampler.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="RasterWeightedAverage", level="DEBUG")

    INPUT_RASTER_1 = "INPUT_RASTER_1"
    INPUT_RASTER_2 = "INPUT_RASTER_2"
    INPUT_RASTER_3 = "INPUT_RASTER_3"
    INPUT_RASTER_4 = "INPUT_RASTER_4"
    WEIGHT_1 = "WEIGHT_1"
    WEIGHT_2 = "WEIGHT_2"
    WEIGHT_3 = "WEIGHT_3"
    WEIGHT_4 = "WEIGHT_4"
    OUTPUT_CRS = "OUTPUT_CRS"
    OUTPUT_RESOLUTION = "OUTPUT_RESOLUTION"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = "DISPLAY_HELP"
    OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo RasterWeightedAverage...")
        self.load_preferences()

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_RASTER_1, "Raster 1"))
        self.addParameter(
            QgsProcessingParameterNumber(
                self.WEIGHT_1,
                "Peso Raster 1",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("weight_1", 50.0),
                minValue=0.0,
            )
        )
        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT_RASTER_2, "Raster 2"))
        self.addParameter(
            QgsProcessingParameterNumber(
                self.WEIGHT_2,
                "Peso Raster 2",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=self.prefs.get("weight_2", 50.0),
                minValue=0.0,
            )
        )

        param = QgsProcessingParameterRasterLayer(
            self.INPUT_RASTER_3, "Raster 3 (opcional)", optional=True
        )
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

        param = QgsProcessingParameterRasterLayer(
            self.INPUT_RASTER_4, "Raster 4 (opcional)", optional=True
        )
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

        param = QgsProcessingParameterNumber(
            self.WEIGHT_3,
            "Peso Raster 3",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=self.prefs.get("weight_3", 50.0),
            minValue=0.0,
            optional=True,
        )
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

        param = QgsProcessingParameterNumber(
            self.WEIGHT_4,
            "Peso Raster 4",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=self.prefs.get("weight_4", 50.0),
            minValue=0.0,
            optional=True,
        )
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

        self.addParameter(
            QgsProcessingParameterCrs(
                self.OUTPUT_CRS,
                "CRS de Saida (opcional)",
                optional=True,
            )
        )

        param = QgsProcessingParameterNumber(
            self.OUTPUT_RESOLUTION,
            "Resolucao de Saida (pixels)",
            type=QgsProcessingParameterNumber.Double,
            defaultValue=self.prefs.get("output_resolution", 0),
            minValue=0.0,
            optional=True,
        )
        self.addParameter(param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, "Saida"))

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN_OUTPUT_FOLDER,
                STR.OPEN_OUTPUT_FOLDER,
                defaultValue=self.prefs.get("open_output_folder", True),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                STR.DISPLAY_HELP_FIELD,
                defaultValue=self.prefs.get("display_help", True),
            )
        )

    def processAlgorithm(self, params, context, feedback):
        self.logger.debug("Iniciando processAlgorithm...")

        try:
            raster1 = self.parameterAsRasterLayer(params, self.INPUT_RASTER_1, context)
            raster2 = self.parameterAsRasterLayer(params, self.INPUT_RASTER_2, context)
            raster3 = self.parameterAsRasterLayer(params, self.INPUT_RASTER_3, context)
            raster4 = self.parameterAsRasterLayer(params, self.INPUT_RASTER_4, context)

            for idx, raster in enumerate([raster1, raster2], 1):
                if not raster or not raster.isValid():
                    msg = f"Raster {idx} e obrigatorio e invalido."
                    self.logger.error(msg)
                    raise QgsProcessingException(msg)

            rasters = [raster1, raster2]
            if raster3 and raster3.isValid():
                rasters.append(raster3)
            if raster4 and raster4.isValid():
                rasters.append(raster4)

            weight1 = self.parameterAsDouble(params, self.WEIGHT_1, context)
            weight2 = self.parameterAsDouble(params, self.WEIGHT_2, context)
            weight3 = self.parameterAsDouble(params, self.WEIGHT_3, context)
            weight4 = self.parameterAsDouble(params, self.WEIGHT_4, context)

            output_resolution = self.parameterAsDouble(params, self.OUTPUT_RESOLUTION, context)
            if output_resolution is None or output_resolution <= 0:
                output_resolution = None

            output_crs = self.parameterAsCrs(params, self.OUTPUT_CRS, context)
            if not output_crs or not output_crs.isValid():
                output_crs = None

            open_output_folder = self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context)
            display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)
            output_path = self.parameterAsOutputLayer(params, self.OUTPUT, context)

            rasters_with_weights = [(raster1, weight1), (raster2, weight2)]
            if raster3 and raster3.isValid():
                rasters_with_weights.append((raster3, weight3))
            if raster4 and raster4.isValid():
                rasters_with_weights.append((raster4, weight4))

            self.logger.debug(
                f"Parametros resolvidos: output_crs={output_crs.authid() if output_crs else None}, output_resolution={output_resolution}, output_path={output_path}"
            )

            self._validate_raster_compatibility(rasters_with_weights)

            prepared_rasters_with_weights = self._prepare_rasters_for_execution(
                rasters_with_weights,
                output_crs=output_crs,
                output_resolution=output_resolution,
                context=context,
                feedback=feedback,
            )

            entries = []
            formula_parts = []
            total_weight = 0.0
            refs = ["A", "B", "C", "D"]

            for i, (ras, weight) in enumerate(prepared_rasters_with_weights):
                entry = QgsRasterCalculatorEntry()
                entry.raster = ras
                entry.bandNumber = 1
                entry.ref = f"{refs[i]}@1"
                entries.append(entry)
                formula_parts.append(f"({entry.ref} * {weight})")
                total_weight += weight

            if total_weight == 0:
                raise QgsProcessingException("A soma dos pesos nao pode ser zero.")

            formula = f"({' + '.join(formula_parts)}) / {total_weight}"
            self.logger.debug(f"Formula gerada: {formula}")
            feedback.pushInfo(f"Processando {len(prepared_rasters_with_weights)} rasters")
            feedback.pushInfo(f"Formula: {formula}")

            base_raster = prepared_rasters_with_weights[0][0]

            calc = QgsRasterCalculator(
                formula,
                output_path,
                "GTiff",
                base_raster.extent(),
                base_raster.width(),
                base_raster.height(),
                entries,
            )

            result = calc.processCalculation()
            if result != 0:
                msg = f"Erro no calculo raster. Codigo de erro: {result}"
                self.logger.error(msg)
                raise QgsProcessingException(msg)

            self.prefs.update(
                {
                    "weight_1": float(weight1),
                    "weight_2": float(weight2),
                    "weight_3": float(weight3),
                    "weight_4": float(weight4),
                    "output_resolution": float(output_resolution) if output_resolution else 0,
                    "display_help": bool(display_help),
                    "open_output_folder": bool(open_output_folder),
                }
            )
            self.save_preferences()

            if output_path and isinstance(output_path, str) and not output_path.startswith("memory:"):
                out_folder = os.path.dirname(output_path)
                if out_folder:
                    feedback.pushInfo(f"Arquivo salvo em: {out_folder}")
                    if open_output_folder:
                        self.open_folder_in_explorer(out_folder)

            feedback.pushInfo("Media ponderada calculada com sucesso!")
            return {self.OUTPUT: output_path}

        except QgsProcessingException as e:
            self.logger.error(f"Erro de processamento: {e}")
            raise
        except Exception as e:
            msg = f"Erro nao tratado em processAlgorithm: {e}"
            self.logger.error(msg)
            raise QgsProcessingException(msg)

    def _prepare_rasters_for_execution(
        self,
        rasters_with_weights,
        *,
        output_crs,
        output_resolution,
        context,
        feedback,
    ):
        """Prepara rasters garantindo compatibilidade de CRS e resolucao."""
        if not rasters_with_weights:
            return []

        base_raster = rasters_with_weights[0][0]
        base_crs = RasterLayerProjection.get_raster_crs(base_raster, self.TOOL_KEY)
        if base_crs is None or not base_crs.isValid():
            raise QgsProcessingException("Raster 1 nao possui CRS valido.")

        target_crs = output_crs if output_crs and output_crs.isValid() else base_crs
        force_all_reproject = output_resolution is not None

        self.logger.debug(
            f"_prepare_rasters_for_execution(target_crs={target_crs.authid()}, output_resolution={output_resolution}, force_all_reproject={force_all_reproject})"
        )

        prepared = []
        for idx, (raster, weight) in enumerate(rasters_with_weights, 1):
            raster_crs = RasterLayerProjection.get_raster_crs(raster, self.TOOL_KEY)
            if raster_crs is None or not raster_crs.isValid():
                raise QgsProcessingException(f"Raster {idx} nao possui CRS valido.")

            needs_reproject = force_all_reproject or raster_crs != target_crs
            if not output_crs and not force_all_reproject and idx == 1:
                needs_reproject = False

            if needs_reproject:
                feedback.pushInfo(
                    f"Preparando raster {idx}: CRS {raster_crs.authid()} -> {target_crs.authid()}"
                )
                reproj_path = self._create_temp_raster_path(idx)
                reproj_output = RasterLayerProjection.reproject_raster_to_crs(
                    raster.source(),
                    target_crs,
                    resampling_method=ResamplingMethod.CUBICO_SUAVIZADO,
                    external_tool_key=self.TOOL_KEY,
                    nodata_value=None,
                    output_data_type=0,
                    target_resolution=output_resolution,
                    output_path=reproj_path,
                    source_crs=raster_crs,
                    context=context,
                    feedback=feedback,
                    is_child_algorithm=True,
                )
                prepared_raster = QgsRasterLayer(reproj_output, f"{raster.name()}_prepared")
                if not prepared_raster.isValid():
                    raise QgsProcessingException(
                        f"Falha ao carregar raster preparado: {reproj_output}"
                    )
                self.logger.debug(
                    f"Raster {idx} preparado com sucesso: {prepared_raster.source()}"
                )
                prepared.append((prepared_raster, weight))
            else:
                self.logger.debug(f"Raster {idx} mantido sem reprojecao: {raster.name()}")
                prepared.append((raster, weight))

        return prepared

    def _create_temp_raster_path(self, idx):
        temp_dir = tempfile.mkdtemp(prefix="cadmus_weighted_avg_")
        return os.path.join(temp_dir, f"weighted_avg_raster_{idx}.tif")

    def _validate_raster_compatibility(self, rasters_with_weights):
        """Valida compatibilidade basica entre rasters."""
        if not rasters_with_weights:
            return

        base_raster, _ = rasters_with_weights[0]
        base_crs = RasterLayerProjection.get_raster_crs(base_raster, self.TOOL_KEY)
        base_extent = base_raster.extent()

        self.logger.debug("Validando compatibilidade basica dos rasters...")

        for i, (ras, _) in enumerate(rasters_with_weights[1:], 1):
            ras_crs = RasterLayerProjection.get_raster_crs(ras, self.TOOL_KEY)
            if base_crs and ras_crs and ras_crs != base_crs:
                self.logger.warning(
                    f"Raster {i + 1} tem CRS diferente: {ras_crs.authid()} vs {base_crs.authid()}"
                )

            if not ras.extent().intersects(base_extent):
                self.logger.warning(f"Raster {i + 1} nao intersecta com Raster 1")
