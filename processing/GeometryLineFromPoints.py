# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingException,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsWkbTypes,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class GeometryLineFromPoints(BaseProcessingAlgorithm):
    TOOL_KEY = ToolKey.GEOMETRY_LINE_FROM_POINTS
    ALGORITHM_NAME = "geometry_difference_line"
    ALGORITHM_DISPLAY_NAME = STR.GEOMETRY_LINE_FROM_POINTS_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_VETORIAL
    ICON = im.GEOMETRY_LINE_DIFFERENCE
    INSTRUCTIONS_FILE = "geometry_difference_line.html"
    INPUT_LAYER_A = "INPUT_LAYER_A"
    INPUT_LAYER_B = "INPUT_LAYER_B"
    USE_SECOND_LAYER = "USE_SECOND_LAYER"
    FIELD_A = "FIELD_A"
    FIELD_B = "FIELD_B"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = "DISPLAY_HELP"
    logger = LogUtils(
        tool=TOOL_KEY, class_name="GeometryLineFromPointsAlgorithm", level="DEBUG"
    )

    def initAlgorithm(self, config=None):
        self.load_preferences()
        self.logger.debug(f"PreferÃªncias carregadas: {self.prefs}")
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER_A,
                STR.POINT_LAYER_MODE1_FIRST_LAYER_MODE2,
                [QgsProcessing.TypeVectorPoint],
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD_A,
                STR.BASE_ATTRIBUTE_LAYER_A,
                parentLayerParameterName=self.INPUT_LAYER_A,
                type=QgsProcessingParameterField.Any,
            )
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.USE_SECOND_LAYER,
                STR.USE_SECOND_LAYER_MODE2,
                defaultValue=self.prefs.get("use_second_layer", False),
            )
        )
        layer_b_param = QgsProcessingParameterFeatureSource(
            self.INPUT_LAYER_B,
            STR.SECOND_POINT_LAYER_MODE2_OPTIONAL,
            [QgsProcessing.TypeVectorPoint],
            optional=True,
        )
        layer_b_param.setFlags(
            layer_b_param.flags() | QgsProcessingParameterFeatureSource.FlagOptional
        )
        self.addParameter(layer_b_param)
        field_b_param = QgsProcessingParameterField(
            self.FIELD_B,
            STR.BASE_ATTRIBUTE_LAYER_B_MODE2,
            parentLayerParameterName=self.INPUT_LAYER_B,
            type=QgsProcessingParameterField.Any,
            optional=True,
        )
        field_b_param.setFlags(
            field_b_param.flags() | QgsProcessingParameterField.FlagOptional
        )
        self.addParameter(field_b_param)
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, STR.DIFFERENCE_LINES)
        )
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                STR.DISPLAY_HELP_FIELD,
                defaultValue=self.prefs.get("display_help", True),
            )
        )

    @staticmethod
    def _feature_point(feat):
        geom = feat.geometry()
        if geom is None or geom.isEmpty():
            return None
        if geom.type() == QgsWkbTypes.PointGeometry:
            try:
                point = geom.asPoint()
                if point is None:
                    return None
                return point
            except Exception as e:
                LogUtils(
                    tool=GeometryLineFromPoints.TOOL_KEY, class_name="GeometryLine"
                ).warning(f"Erro ao extrair ponto da geometria do recurso {feat.id()}: {str(e)}")
        try:
            centroid = geom.centroid()
            if centroid is None or centroid.isEmpty():
                return None
            return centroid.asPoint()
        except Exception as e:
            LogUtils(
                tool=GeometryLineFromPoints.TOOL_KEY, class_name="GeometryLine"
            ).warning(f"Erro ao extrair centroid da geometria do recurso {feat.id()}: {str(e)}")
            return None

    @staticmethod
    def _append_line_features(features, sink, out_fields, key_name):
        for f1, f2 in features:
            geom1 = GeometryLineFromPoints._feature_point(f1)
            geom2 = GeometryLineFromPoints._feature_point(f2)
            if geom1 is None or geom2 is None:
                continue
            line = QgsGeometry.fromPolylineXY([geom1, geom2])
            if line is None or line.isEmpty():
                continue
            distance = geom1.distance(geom2)
            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(line)
            out_feat.setAttributes(
                [key_name, int(f1.id()), int(f2.id()), float(distance)]
            )
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)

    def processAlgorithm(self, params, context, feedback):
        layer_a = self.parameterAsSource(params, self.INPUT_LAYER_A, context)
        if layer_a is None:
            raise QgsProcessingException(STR.INVALID_LAYER_A)
        use_second = self.parameterAsBool(params, self.USE_SECOND_LAYER, context)
        layer_b = self.parameterAsSource(params, self.INPUT_LAYER_B, context)
        field_a = self.parameterAsString(params, self.FIELD_A, context)
        field_b = (
            self.parameterAsString(params, self.FIELD_B, context)
            if layer_b is not None
            else None
        )
        if use_second and layer_b is None:
            raise QgsProcessingException(STR.MODE2_REQUIRES_SECOND_POINT_LAYER)
        if use_second and not field_b:
            raise QgsProcessingException(STR.MODE2_INFORM_GROUP_FIELD_LAYER_B)
        fields = QgsFields()
        fields.append(QgsField("group_key", QVariant.String))
        fields.append(QgsField("feature_a", QVariant.Int))
        fields.append(QgsField("feature_b", QVariant.Int))
        fields.append(QgsField("distance", QVariant.Double))
        (sink, dest_id) = self.parameterAsSink(
            params, self.OUTPUT, context, fields, QgsWkbTypes.LineString, layer_a.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(STR.ERROR_CREATING_OUTPUT_LAYER)
        if use_second:
            index_b = {}
            for feat_b in layer_b.getFeatures():
                key = feat_b[field_b]
                if key is None:
                    continue
                index_b.setdefault(str(key), []).append(feat_b)
            for feat_a in layer_a.getFeatures():
                key = feat_a[field_a]
                if key is None:
                    continue
                matches = index_b.get(str(key))
                if matches:
                    self._append_line_features(
                        [(feat_a, feat_b) for feat_b in matches], sink, fields, str(key)
                    )
        else:
            groups = {}
            for feat in layer_a.getFeatures():
                key = feat[field_a]
                if key is None:
                    continue
                groups.setdefault(str(key), []).append(feat)
            for key_name, feats in groups.items():
                if len(feats) < 2:
                    continue
                feats = sorted(feats, key=lambda f: f.id())
                self._append_line_features(
                    [(feats[i], feats[i + 1]) for i in range(len(feats) - 1)],
                    sink,
                    fields,
                    str(key_name),
                )
        display_help = (
            bool(self.parameterAsBool(params, self.DISPLAY_HELP, context))
            if self.DISPLAY_HELP in params
            else False
        )
        self.prefs.update(
            {"use_second_layer": bool(use_second), "display_help": display_help}
        )
        self.save_preferences()
        feedback.pushInfo(STR.PROCESS_COMPLETED_LINES_GENERATED_SUCCESS)
        return {self.OUTPUT: dest_id}
