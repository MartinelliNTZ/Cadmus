# -*- coding: utf-8 -*-
# FILE: Cadmus/processing/difference_fields_provider.py

import os
from PyQt5.QtGui import QIcon
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessing,
)


# Preferências
from ..utils.Preferences import load_tool_prefs, save_tool_prefs

# Lógica
from .model.difference_fields_model import DifferenceFieldsModel

from PyQt5.QtCore import QVariant

class DifferenceFieldsAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"
    BASE_FIELD = "BASE_FIELD"
    EXCLUDE_FIELDS = "EXCLUDE_FIELDS"   # <-- AGORA É EXCLUÍR CAMPOS
    PREFIX = "PREFIX"
    PRECISION = "PRECISION"
    OUTPUT = "OUTPUT"
    TOOL_KEY = "difference_fields_tool"
    
    NUMERIC = {
        QVariant.Int,
        QVariant.UInt,
        QVariant.LongLong,
        QVariant.ULongLong,
        QVariant.Double,
    }

    # Identificação
    def name(self):
        return "difference_fields"

    def displayName(self):
        return "Gerador de Diferenças entre Campos"

    def group(self):
        return "Estatística"

    def groupId(self):
        return "estatistica"

    def icon(self):
        icon_path = os.path.join(
            os.path.dirname(__file__), "..", "resources","icons", "field_diference.ico"
        )
        return QIcon(icon_path)

    def createInstance(self):
        return DifferenceFieldsAlgorithm()

    # Carregar preferências
    def _load_prefs(self):
        prefs = load_tool_prefs(self.TOOL_KEY)
        return {
            "prefix": prefs.get("prefix", "D_"),
            "precision": prefs.get("precision", 4),
        }

    def _save_prefs(self, prefix, precision):
        save_tool_prefs(self.TOOL_KEY, {
            "prefix": prefix,
            "precision": precision
        })

    # Definição dos parâmetros
    def initAlgorithm(self, config=None):
        prefs = self._load_prefs()

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LAYER,
            "Camada de Pontos",
            [QgsProcessing.TypeVectorPoint]
        ))

        self.addParameter(QgsProcessingParameterField(
            self.BASE_FIELD,
            "Campo Base (subtraendo)",
            parentLayerParameterName=self.INPUT_LAYER,
            type=QgsProcessingParameterField.Numeric
        ))

        param_exclude = QgsProcessingParameterField(
            self.EXCLUDE_FIELDS,
            "Campos a EXCLUIR do cálculo",
            parentLayerParameterName=self.INPUT_LAYER,
            type=QgsProcessingParameterField.Numeric,
            allowMultiple=True
        )
        param_exclude.setFlags(param_exclude.flags() | QgsProcessingParameterField.FlagOptional)
        self.addParameter(param_exclude)


        self.addParameter(QgsProcessingParameterString(
            self.PREFIX,
            "Prefixo para novos campos",
            defaultValue=prefs["prefix"]
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.PRECISION,
            "Precisão (casas decimais)",
            type=QgsProcessingParameterNumber.Integer,
            minValue=0,
            maxValue=10,
            defaultValue=prefs["precision"]
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Diferenca"
        ))

    # PROCESSAMENTO
    def processAlgorithm(self, params, context, feedback):
        layer = self.parameterAsSource(params, self.INPUT_LAYER, context)
        base_field = self.parameterAsFields(params, self.BASE_FIELD, context)[0]

        # Lê os campos a excluir (podem ser 0)
        excludeds = self.parameterAsFields(params, self.EXCLUDE_FIELDS, context)

        prefix = self.parameterAsString(params, self.PREFIX, context)
        precision = self.parameterAsInt(params, self.PRECISION, context)

        # ------------------------------------------------------------
        # SE O USUÁRIO NÃO INFORMAR NADA → USAR TODOS OS CAMPOS MENOS O BASE
        # ------------------------------------------------------------
        if not excludeds or len(excludeds) == 0:
            fields_to_compare = [
                f.name() for f in layer.fields()
                if f.type() in self.NUMERIC and f.name() != base_field
            ]
            feedback.pushInfo("Nenhum campo excluído → usando todos os campos numéricos.")
        else:
            # Se informou campos para excluir, usar todos MENOS esses
            fields_to_compare = [
                f.name() for f in layer.fields()
                if f.type() in self.NUMERIC and f.name() not in excludeds and f.name() != base_field
            ]

        feedback.pushInfo(f"Base: {base_field}")
        feedback.pushInfo(f"Campos EXCLUÍDOS: {excludeds}")
        feedback.pushInfo(f"Campos utilizados no cálculo: {fields_to_compare}")
        feedback.pushInfo(f"Prefixo: {prefix}")
        feedback.pushInfo(f"Precisão: {precision}")

        # Salvar preferências
        self._save_prefs(prefix, precision)

        # Lógica (Model)
        model = DifferenceFieldsModel(prefix=prefix, precision=precision)

        # Campos de saída
        out_fields = model.create_output_fields(layer, fields_to_compare)

        sink, dest = self.parameterAsSink(
            params,
            self.OUTPUT,
            context,
            out_fields,
            layer.wkbType(),
            layer.sourceCrs()
        )

        # Processar feições
        model.process_features(layer, base_field, fields_to_compare, out_fields, sink)

        feedback.pushInfo("✔ Processo finalizado com sucesso.")

        return {self.OUTPUT: dest}
