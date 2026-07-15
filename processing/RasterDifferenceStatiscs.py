# -*- coding: utf-8 -*-
import itertools
import os

import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterMultipleLayers,
    QgsRasterLayer,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RasterDifferenceStatiscs(BaseProcessingAlgorithm):
    TOOL_KEY = ToolKey.RASTER_MASS_CLIPPER
    ALGORITHM_NAME = "raster_difference_statistics"
    ALGORITHM_DISPLAY_NAME = STR.RASTER_DIFFERENCE_STATISTICS_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = "raster_diference_statistics.ico"
    logger = LogUtils(
        tool="raster_diff_task", class_name="RasterDiffTask", level="DEBUG"
    )

    INPUT_FOLDER = "INPUT_FOLDER"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"
    INPUT_LAYERS = "INPUT_LAYERS"
    DISPLAY_HELP = "DISPLAY_HELP"
    OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"

    def initAlgorithm(self, config=None):
        self.logger.debug("initAlgorithm initialized")
        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.INPUT_FOLDER,
                STR.RASTER_FOLDER_OR_SELECT_RASTER_LAYERS,
                defaultValue=self.prefs.get("last_input_folder", ""),
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_LAYERS,
                STR.QGIS_RASTER_LAYERS_OR_SELECT_RASTER_FOLDER,
                QgsProcessing.TypeRaster,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                STR.OUTPUT_FOLDER_FOR_GENERATED_RASTERS,
                defaultValue=self.prefs.get("last_output_folder", ""),
                optional=True,
            )
        )

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

    @staticmethod
    def overlap(r1, r2):
        e1 = r1.extent()
        e2 = r2.extent()
        inter = e1.intersect(e2)
        return not inter.isEmpty()

    def _normalize_placeholders(self, input_folder, output_folder):
        sanitized_input = input_folder or ""
        sanitized_output = output_folder or ""

        if sanitized_input.upper() == "TEMPORARY_OUTPUT" or sanitized_input.endswith(
            "INPUT_FOLDER"
        ):
            self.logger.debug(
                "Input_folder placeholder detectado, ignorando input_folder."
            )
            sanitized_input = ""

        if sanitized_output.upper() == "TEMPORARY_OUTPUT" or sanitized_output.endswith(
            "OUTPUT_FOLDER"
        ):
            self.logger.debug(
                "Output_folder placeholder detectado, ignorando output_folder."
            )
            sanitized_output = ""

        return sanitized_input, sanitized_output

    def _ensure_output_folder(self, output_folder, feedback):
        if not output_folder:
            import tempfile

            output_folder = tempfile.mkdtemp(prefix="cadmus_folderlayer_")
            feedback.pushInfo(
                f"{STR.NO_OUTPUT_FOLDER_PROVIDED_USING_TEMP} {output_folder}"
            )
            self.logger.info(f"Output_folder gerada temporÃ¡ria: {output_folder}")

        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def _collect_rasters_from_folder(self, input_folder, feedback):
        rasters = []
        if not input_folder:
            return rasters

        if not os.path.isdir(input_folder):
            self.logger.error(f"Pasta invÃ¡lida: {input_folder}")
            raise QgsProcessingException(f"{STR.INVALID_FOLDER}: {input_folder}")

        self.logger.info(f"Lendo arquivos de pasta (recursivamente): {input_folder}")
        raster_paths = []

        for root, _, files in os.walk(input_folder):
            for f in files:
                if f.lower().endswith((".tif", ".tiff", ".vrt", ".img")):
                    raster_paths.append(os.path.join(root, f))

        if not raster_paths:
            feedback.pushInfo(STR.NO_RASTER_FOUND_IN_SPECIFIED_FOLDER)
            self.logger.warning(
                "Nenhum arquivo raster vÃ¡lido encontrado na pasta de input."
            )

        for path in sorted(raster_paths):
            layer = QgsRasterLayer(path, os.path.splitext(os.path.basename(path))[0])
            if layer.isValid():
                rasters.append(layer)
                self.logger.debug(f"Raster carregado da pasta: {path}")
            else:
                feedback.pushInfo(f"{STR.INVALID_RASTER_IGNORED}: {path}")
                self.logger.warning(f"Raster invÃ¡lido ignorado: {path}")

        self.logger.info(f"Total de rasters carregados da pasta: {len(rasters)}")
        return rasters

    def _collect_rasters_from_layers(self, input_layers):
        rasters = []

        if not input_layers:
            return rasters

        for lay in input_layers:
            if isinstance(lay, QgsRasterLayer):
                rasters.append(lay)
            elif isinstance(lay, str):
                layer = QgsRasterLayer(lay, os.path.splitext(os.path.basename(lay))[0])
                if layer.isValid():
                    rasters.append(layer)

        return rasters

    def _build_formula(self, nd1, nd2):
        return (
            f'(("A@1" != {nd1}) AND ("B@1" != {nd2})) * ("A@1" - "B@1") + '
            f'(("A@1" = {nd1}) OR ("B@1" = {nd2})) * {nd1}'
        )

    def _process_pair(self, r1, r2, output_folder, context, feedback, stats_summary):
        if not self.overlap(r1, r2):
            feedback.pushInfo(
                f"{STR.NO_OVERLAP_BETWEEN} {r1.name()} {STR.AND} {r2.name()}. {STR.SKIPPING}"
            )
            self.logger.info(f"Sem sobreposiÃ§Ã£o: {r1.name()} x {r2.name()}")
            return

        nd1 = r1.dataProvider().sourceNoDataValue(1)
        nd2 = r2.dataProvider().sourceNoDataValue(1)
        nd1 = nd1 if nd1 is not None else -9999
        nd2 = nd2 if nd2 is not None else -9999

        fname = f"DIF_{r1.name()}_{r2.name()}.tif".replace(" ", "_")
        out_tif = os.path.join(output_folder, fname)

        formula = self._build_formula(nd1, nd2)

        entry1 = QgsRasterCalculatorEntry()
        entry1.ref = "A@1"
        entry1.raster = r1
        entry1.bandNumber = 1

        entry2 = QgsRasterCalculatorEntry()
        entry2.ref = "B@1"
        entry2.raster = r2
        entry2.bandNumber = 1

        try:
            calc = QgsRasterCalculator(
                formula,
                out_tif,
                "GTiff",
                r1.extent(),
                r1.width(),
                r1.height(),
                [entry1, entry2],
            )
            result = calc.processCalculation()
        except Exception as e:
            feedback.pushInfo(f"{STR.CALCULATION_ERROR_FOR} {r1.name()} x {r2.name()}: {e}")
            self.logger.error(f"Erro em QgsRasterCalculator: {e}")
            return

        if result != 0:
            feedback.pushInfo(f"{STR.CALCULATION_ERROR_FOR} {r1.name()} x {r2.name()}")
            self.logger.error(
                f"QgsRasterCalculator retornou cÃ³digo {result} para {r1.name()} x {r2.name()}"
            )
            return

        feedback.pushInfo(f"{STR.DIFFERENCE_RASTER_CREATED} {out_tif}")
        self.logger.info(f"Raster diferenÃ§a criado: {out_tif}")

        stats_html = os.path.join(
            output_folder, f"{os.path.splitext(fname)[0]}_stats.html"
        )
        try:
            stats = processing.run(
                "native:rasterlayerstatistics",
                {
                    "INPUT": out_tif,
                    "BAND": 1,
                    "OUTPUT_HTML_FILE": stats_html,
                },
                context=context,
                feedback=feedback,
            )
            min_v = stats.get("MIN")
            max_v = stats.get("MAX")
            mean_v = stats.get("MEAN")
            std_v = stats.get("STD_DEV")

            feedback.pushInfo(
                f"{STR.STATS_GENERATED_FOR} {fname}: MIN={min_v} MAX={max_v} MEAN={mean_v} STD_DEV={std_v}"
            )
            self.logger.info(f"Stats HTML criado: {stats_html}")

            stats_summary.append(
                {
                    "raster_path": out_tif,
                    "min": min_v,
                    "max": max_v,
                    "mean": mean_v,
                    "std_dev": std_v,
                }
            )
        except Exception as e:
            feedback.pushInfo(f"{STR.FAILED_TO_GENERATE_STATS_FOR} {fname}: {e}")
            self.logger.error(f"Erro em native:rasterlayerstatistics para {fname}: {e}")
            stats_summary.append(
                {
                    "raster_path": out_tif,
                    "min": None,
                    "max": None,
                    "mean": None,
                    "std_dev": None,
                }
            )

    def _write_summary_html(self, output_folder, total, stats_summary):
        summary_html = os.path.join(
            output_folder, "raster_difference_stats_summary.html"
        )

        with open(summary_html, "w", encoding="utf-8") as fh:
            fh.write(
                f"<html><head><meta charset='utf-8'><title>{STR.DIFFERENCE_STATISTICS_SUMMARY_TITLE}</title></head><body>"
            )
            fh.write(f"<h1>{STR.DIFFERENCE_STATISTICS_SUMMARY_TITLE}</h1>")
            fh.write(f"<p>{STR.TOTAL_PROCESSED_PAIRS} {total}</p>")
            fh.write("<table border='1' cellpadding='6' cellspacing='0'>")
            fh.write(
                f"<tr><th>{STR.RASTER}</th><th>MIN</th><th>MAX</th><th>{STR.INTERVAL}</th><th>MEAN</th><th>STD_DEV</th></tr>"
            )

            for row in stats_summary:
                min_value = row.get("min")
                max_value = row.get("max")
                interval_value = ""
                try:
                    if min_value is not None and max_value is not None:
                        interval_value = float(max_value) - float(min_value)
                except Exception as e:
                    self.logger.error(f"Erro ao calcular intervalo para {row.get('raster_path')}: {e}")
                    interval_value = ""

                fh.write("<tr>")
                fh.write(f"<td>{row.get('raster_path')}</td>")
                fh.write(f"<td>{min_value if min_value is not None else ''}</td>")
                fh.write(f"<td>{max_value if max_value is not None else ''}</td>")
                fh.write(f"<td>{interval_value}</td>")
                fh.write(f"<td>{row.get('mean', '')}</td>")
                fh.write(f"<td>{row.get('std_dev', '')}</td>")
                fh.write("</tr>")

            fh.write("</table>")
            fh.write("</body></html>")

        return summary_html

    def processAlgorithm(self, params, context, feedback):
        input_folder = self.parameterAsString(params, self.INPUT_FOLDER, context)
        input_layers = (
            self.parameterAsLayerList(params, self.INPUT_LAYERS, context) or []
        )
        output_folder = self.parameterAsString(params, self.OUTPUT_FOLDER, context)
        display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)
        open_output_folder = self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context)

        self.logger.info(
            f"ProcessAlgorithm iniciado: input_folder={input_folder}, output_folder={output_folder}, input_layers={len(input_layers)}"
        )
        self.logger.debug(f"ParÃ¢metros detalhados: {params}")

        input_folder, output_folder = self._normalize_placeholders(
            input_folder, output_folder
        )
        output_folder = self._ensure_output_folder(output_folder, feedback)

        if display_help:
            feedback.pushInfo(STR.PROCESSING_RASTER_DIFFERENCE_BY_FOLDER_OR_LAYERS)

        folder_rasters = self._collect_rasters_from_folder(input_folder, feedback)
        layer_rasters = self._collect_rasters_from_layers(input_layers)
        rasters = folder_rasters + layer_rasters

        if not input_folder and not rasters:
            raise QgsProcessingException(STR.INFORM_RASTER_FOLDER_OR_SELECT_LAYER)

        if len(rasters) < 2:
            self.logger.error(
                "Menos de 2 rasters disponÃ­veis para cÃ¡lculo de diferenÃ§a."
            )
            raise QgsProcessingException(STR.AT_LEAST_2_RASTERS_REQUIRED)

        pairs = list(itertools.combinations(rasters, 2))
        total = len(pairs)
        feedback.pushInfo(f"{STR.FOUND_RASTER_COMBINATIONS_FOR_DIFFERENCE} {total}.")
        self.logger.info(f"Total {total} pares carregados para processamento.")

        stats_summary = []

        for idx, (r1, r2) in enumerate(pairs, start=1):
            feedback.pushInfo(f"{STR.PROCESSING} {idx}/{total}: {r1.name()} x {r2.name()}")
            self._process_pair(r1, r2, output_folder, context, feedback, stats_summary)

        summary_html = self._write_summary_html(output_folder, total, stats_summary)

        feedback.pushInfo(f"{STR.CONSOLIDATED_REPORT_GENERATED} {summary_html}")
        self.logger.info(f"Resumo consolidado de estatÃ­sticas criado: {summary_html}")

        self.prefs.update(
            {
                "last_input_folder": input_folder,
                "last_output_folder": output_folder,
                "display_help": bool(display_help),
                "open_output_folder": bool(open_output_folder),
            }
        )
        self.save_preferences()

        if open_output_folder:
            self.open_folder_in_explorer(output_folder)

        return {self.OUTPUT_FOLDER: output_folder, "SUMMARY_HTML": summary_html}
