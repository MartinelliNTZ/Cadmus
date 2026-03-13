# -*- coding: utf-8 -*-
# FILE: Cadmus/logic/difference_fields_model.py

from qgis.core import QgsFields, QgsField, QgsFeature, QgsFeatureSink
from PyQt5.QtCore import QVariant


class DifferenceFieldsModel:
    """
    Lógica independente para cálculo de diferenças entre campos.
    Reutilizável por qualquer ferramenta ou interface.
    """

    def __init__(self, prefix="D_", precision=4):
        self.prefix = prefix
        self.precision = precision

    def create_output_fields(self, source_layer, fields_to_compare):
        out_fields = QgsFields()
        for f in source_layer.fields():
            out_fields.append(f)

        for col in fields_to_compare:
            new_name = f"{self.prefix}{col}"
            out_fields.append(QgsField(new_name, QVariant.Double))

        return out_fields

    def process_features(self, layer, base_field, fields_to_compare, out_fields, sink):
        for feat in layer.getFeatures():
            geom = feat.geometry()
            attrs = feat.attributes()
            base_value = feat[base_field]

            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(geom)

            for col in fields_to_compare:
                value = feat[col]
                if value is None or base_value is None:
                    attrs.append(None)
                else:
                    diff = float(value) - float(base_value)
                    attrs.append(round(diff, self.precision))

            out_feat.setAttributes(attrs)
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
