# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class DifferenceFieldsAlgorithm(BaseProcessingAlgorithm):
    TOOL_KEY = ToolKey.DIFFERENCE_FIELDS
    ALGORITHM_NAME = "difference_fields"
    ALGORITHM_DISPLAY_NAME = STR.DIFFERENCE_FIELDS_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_ESTATISTICA
    ICON = im.FIELD_DIFFERENCE
    INSTRUCTIONS_FILE = "difference_fields.html"
    logger = LogUtils(
        tool=TOOL_KEY, class_name="DifferenceFieldsAlgorithm", level="DEBUG"
    )
    INPUT_LAYER = "INPUT_LAYER"
    BASE_FIELD = "BASE_FIELD"
    EXCLUDE_FIELDS = "EXCLUDE_FIELDS"
    PREFIX = "PREFIX"
    PRECISION = "PRECISION"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = "DISPLAY_HELP"
    NUMERIC = {
        QVariant.Int,
        QVariant.UInt,
        QVariant.LongLong,
        QVariant.ULongLong,
        QVariant.Double,
    }

    def initAlgorithm(self, config=None):
        self.load_preferences()
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER, STR.POINT_LAYER, [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.BASE_FIELD,
                STR.BASE_FIELD_SUBTRAHEND,
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.Numeric,
            )
        )
        param_exclude = QgsProcessingParameterField(
            self.EXCLUDE_FIELDS,
            STR.FIELDS_TO_EXCLUDE_FROM_CALCULATION,
            parentLayerParameterName=self.INPUT_LAYER,
            type=QgsProcessingParameterField.Numeric,
            allowMultiple=True,
        )
        param_exclude.setFlags(
            param_exclude.flags() | QgsProcessingParameterField.FlagOptional
        )
        self.addParameter(param_exclude)
        self.addParameter(
            QgsProcessingParameterString(
                self.PREFIX,
                STR.PREFIX_FOR_NEW_FIELDS,
                defaultValue=self.prefs.get("prefix", "diff_"),
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.PRECISION,
                STR.PRECISION_DECIMAL_PLACES,
                type=QgsProcessingParameterNumber.Integer,
                minValue=0,
                maxValue=10,
                defaultValue=self.prefs.get("precision", 2),
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                STR.DISPLAY_HELP_FIELD,
                defaultValue=self.prefs.get("display_help", True),
            )
        )
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, STR.DIFFERENCE))

    def processAlgorithm(self, params, context, feedback):
        layer = self.parameterAsSource(params, self.INPUT_LAYER, context)
        base_field = self.parameterAsFields(params, self.BASE_FIELD, context)[0]
        excludeds = self.parameterAsFields(params, self.EXCLUDE_FIELDS, context)
        prefix = self.parameterAsString(params, self.PREFIX, context)
        precision = self.parameterAsInt(params, self.PRECISION, context)
        if not excludeds:
            fields_to_compare = [
                f.name()
                for f in layer.fields()
                if f.type() in self.NUMERIC and f.name() != base_field
            ]
            feedback.pushInfo(STR.NO_EXCLUDED_FIELD_USING_ALL_NUMERIC)
        else:
            fields_to_compare = [
                f.name()
                for f in layer.fields()
                if f.type() in self.NUMERIC and f.name() not in excludeds and f.name() != base_field
            ]
        feedback.pushInfo(f"{STR.BASE}: {base_field}")
        feedback.pushInfo(f"{STR.EXCLUDED_FIELDS}: {excludeds}")
        feedback.pushInfo(f"{STR.FIELDS_USED_IN_CALCULATION}: {fields_to_compare}")
        feedback.pushInfo(f"{STR.PREFIX}: {prefix}")
        feedback.pushInfo(f"{STR.PRECISION}: {precision}")
        display_help = bool(self.parameterAsBool(params, self.DISPLAY_HELP, context)) if self.DISPLAY_HELP in params else False
        self.prefs.update({"prefix": prefix, "precision": precision, "display_help": display_help})
        self.save_preferences()
        out_fields = self.create_output_fields(layer, fields_to_compare, prefix=prefix)
        sink, dest = self.parameterAsSink(
            params, self.OUTPUT, context, out_fields, layer.wkbType(), layer.sourceCrs()
        )
        self.process_features(layer, base_field, fields_to_compare, out_fields, sink, precision=precision)
        feedback.pushInfo(STR.PROCESS_FINISHED_SUCCESS)
        return {self.OUTPUT: dest}

    def create_output_fields(self, source_layer, fields_to_compare, prefix="diff_"):
        out_fields = QgsFields()
        for f in source_layer.fields():
            out_fields.append(f)
        for col in fields_to_compare:
            out_fields.append(QgsField(f"{prefix}{col}", QVariant.Double))
        return out_fields

    def process_features(self, layer, base_field, fields_to_compare, out_fields, sink, precision=2):
        for feat in layer.getFeatures():
            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(feat.geometry())
            attrs = feat.attributes()
            base_value = feat[base_field]
            for col in fields_to_compare:
                value = feat[col]
                attrs.append(None if value is None or base_value is None else round(float(value) - float(base_value), precision))
            out_feat.setAttributes(attrs)
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
