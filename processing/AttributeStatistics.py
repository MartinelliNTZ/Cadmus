# -*- coding: utf-8 -*-
import math
import os

from qgis.core import (
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProject,
    QgsVectorLayer,
)

from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm
from .model.attribute_statistics_model import AttributeStatisticsModel


class AttributeStatistics(BaseProcessingAlgorithm):
    TOOL_KEY = ToolKey.ATTRIBUTE_STATISTICS
    ALGORITHM_NAME = "attribute_statistics"
    ALGORITHM_DISPLAY_NAME = STR.ATTRIBUTE_STATISTICS_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_ESTATISTICA
    ICON = im.ATTRIBUTE_STATS
    INPUT_LAYER = "INPUT_LAYER"
    EXCLUDE_FIELDS = "EXCLUDE_FIELDS"
    PRECISION = "PRECISION"
    PTBR_FORMAT = "PTBR_FORMAT"
    LOAD_AFTER = "LOAD_AFTER"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = "DISPLAY_HELP"
    OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"

    STATS = {
        "MEAN": STR.MEAN,
        "MEAN_ABS": STR.MEAN_ABSOLUTE,
        "STD_POP": STR.STD_POP,
        "STD_SAMP": STR.STD_SAMPLE,
        "MIN": STR.MINIMUM,
        "MAX": STR.MAXIMUM,
        "RANGE": STR.RANGE,
        "MEDIAN": STR.MEDIAN,
        "P5": STR.PERCENTILE_5,
        "P95": STR.PERCENTILE_95,
        "MODE": STR.MODE,
        "VARIANCE": STR.VARIANCE,
        "SUM": STR.SUM,
        "CV": STR.COEFFICIENT_OF_VARIATION,
        "SKEW": STR.SKEWNESS,
        "KURT": STR.KURTOSIS,
    }

    def initAlgorithm(self, config=None):
        self.load_preferences()
        prefs = self.prefs or {}
        self._model = AttributeStatisticsModel()
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER, STR.INPUT_LAYER, [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.EXCLUDE_FIELDS,
                STR.EXCLUDE_FIELDS_OPTIONAL,
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Any,
                allowMultiple=True,
                optional=True,
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PRECISION,
                STR.PRECISION_DECIMAL_PLACES,
                type=QgsProcessingParameterNumber.Integer,
                minValue=0,
                maxValue=12,
                defaultValue=prefs.get("precision", 2),
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                STR.DISPLAY_HELP_FIELD,
                defaultValue=prefs.get("display_help", True),
            )
        )
        p_load = QgsProcessingParameterBoolean(
            self.LOAD_AFTER,
            STR.LOAD_CSV_AUTOMATICALLY_AFTER_EXECUTION,
            defaultValue=prefs.get("load_after", False),
        )
        p_load.setFlags(p_load.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_load)
        p_force_ptbr = QgsProcessingParameterBoolean(
            self.PTBR_FORMAT,
            STR.FORCE_CSV_PTBR_FORMAT,
            defaultValue=prefs.get("force_ptbr", False),
        )
        p_force_ptbr.setFlags(
            p_force_ptbr.flags() | QgsProcessingParameterDefinition.FlagAdvanced
        )
        self.addParameter(p_force_ptbr)
        p_open = QgsProcessingParameterBoolean(
            self.OPEN_OUTPUT_FOLDER,
            STR.OPEN_OUTPUT_FOLDER,
            defaultValue=prefs.get("open_output_folder", True),
        )
        p_open.setFlags(p_open.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(p_open)
        enabled_stats = prefs.get("stats_enabled", {})
        for key, label in self.STATS.items():
            p = QgsProcessingParameterBoolean(
                key, f"{STR.CALCULATE}: {label}", defaultValue=enabled_stats.get(key, True)
            )
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)
        last_folder = prefs.get("last_output_folder", "")
        default_output = os.path.join(last_folder, "atributos_estatistica.csv") if last_folder else None
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, STR.OUTPUT_CSV_FILE, fileFilter="CSV (*.csv)", defaultValue=default_output
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsLayer(parameters, self.INPUT_LAYER, context)
        if layer is None:
            raise QgsProcessingException(STR.INVALID_LAYER)
        exclude_fields = self.parameterAsFields(parameters, self.EXCLUDE_FIELDS, context) or []
        precision = int(self.parameterAsInt(parameters, self.PRECISION, context))
        ptbr_format = bool(self.parameterAsBool(parameters, self.PTBR_FORMAT, context))
        load_after = bool(self.parameterAsBool(parameters, self.LOAD_AFTER, context))
        open_output_folder = bool(self.parameterAsBool(parameters, self.OPEN_OUTPUT_FOLDER, context))
        stats_enabled = {k: self.parameterAsBool(parameters, k, context) for k in self.STATS.keys()}
        output_path = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        out_folder = os.path.dirname(output_path)
        numeric_fields = [f for f in self._model.extract_numeric_fields(layer.fields()) if f not in exclude_fields]
        if not numeric_fields:
            feedback.pushInfo(STR.NO_NUMERIC_FIELD_FOUND)
            return {self.OUTPUT: output_path}
        total = layer.featureCount()
        values_by_field = {fn: [] for fn in numeric_fields}
        for i, feat in enumerate(layer.getFeatures()):
            for fn in numeric_fields:
                v = feat[fn]
                if v is not None:
                    val = float(v)
                    if math.isfinite(val):
                        values_by_field[fn].append(val)
            if total:
                feedback.setProgress(int(100 * i / total))
        force_ptbr = bool(self.parameterAsBool(parameters, self.PTBR_FORMAT, context))
        sep = ";" if (force_ptbr or ptbr_format) else ","
        dec = "," if (force_ptbr or ptbr_format) else "."
        headers = [STR.FIELD, STR.COUNT] + [label for key, label in self.STATS.items() if stats_enabled.get(key, False)]

        def fmt(v):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return ""
            return str(round(v, precision)).replace(".", dec)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sep.join(headers) + "\n")
                computed = self._model.compute_all(values_by_field, stats_enabled)
                for fn in numeric_fields:
                    vals = sorted(values_by_field[fn])
                    row = [fn, str(len(vals))]
                    if len(vals) == 0:
                        row += [""] * (len(headers) - 2)
                    else:
                        for key in self.STATS.keys():
                            if stats_enabled.get(key, False):
                                row.append(fmt(computed.get(fn, {}).get(key, float("nan"))))
                    f.write(sep.join(row) + "\n")
        except Exception as e:
            raise QgsProcessingException(f"{STR.ERROR_SAVING_CSV} {e}")
        display_help = bool(self.parameterAsBool(parameters, self.DISPLAY_HELP, context)) if self.DISPLAY_HELP in parameters else False
        self.prefs.update({
            "precision": precision,
            "exclude_fields": exclude_fields,
            "last_output_folder": out_folder,
            "force_ptbr": force_ptbr,
            "load_after": load_after,
            "stats_enabled": stats_enabled,
            "display_help": display_help,
            "open_output_folder": open_output_folder,
        })
        self.save_preferences()
        if load_after and output_path:
            uri = f"file:///{output_path}?type=csv&delimiter={sep}&detectTypes=yes&decimalPoint={dec}"
            vl = QgsVectorLayer(uri, os.path.basename(output_path), "delimitedtext")
            if vl.isValid():
                context.temporaryLayerStore().addMapLayer(vl)
                QgsProject.instance().addMapLayer(vl)
                feedback.pushInfo(f"{STR.FILE_LOADED_AS_LAYER} {output_path}")
        if output_path:
            feedback.pushInfo(f"{STR.CSV_FILE_GENERATED} {output_path}")
            feedback.pushInfo(f"{STR.FILE_SAVED_IN} {out_folder}")
            if open_output_folder:
                self.open_folder_in_explorer(out_folder)
        return {self.OUTPUT: output_path}
