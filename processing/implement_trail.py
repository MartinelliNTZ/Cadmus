# -*- coding: utf-8 -*-
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsProcessingUtils,
    QgsFeatureSink
)
from qgis import processing

class ImplementTrail(QgsProcessingAlgorithm):

    PARAM_LINHAS = "j"
    PARAM_TAMANHO = "tamanhoimplemento"
    OUTPUT_RASTRO = "Rastro_Implemento"

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PARAM_LINHAS,
                "Linhas",
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.PARAM_TAMANHO,
                "Tamanho implemento",
                QgsProcessingParameterNumber.Double,
                defaultValue=16.0
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_RASTRO,
                "Rastro_Implemento",
                QgsProcessing.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Carregar camada corretamente
        linhas_layer = QgsProcessingUtils.mapLayerFromString(
            parameters[self.PARAM_LINHAS], context
        )

        if linhas_layer is None:
            raise QgsProcessingException("Não foi possível carregar a camada de linhas.")

        tamanho = self.parameterAsDouble(parameters, self.PARAM_TAMANHO, context)
        distancia = tamanho / 2

        feedback.pushInfo("🔹 Explodindo linhas…")

        exploded = processing.run(
            "native:explodelines",
            {
                "INPUT": linhas_layer,
                "OUTPUT": "memory:"
            },
            context=context,
            feedback=feedback
        )["OUTPUT"]

        # Criar o sink corretamente (CRUCIAL!!)
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT_RASTRO,
            context,
            linhas_layer.fields(),  # campos da camada original
            QgsProcessing.TypeVectorPolygon,
            linhas_layer.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException("Falha ao criar o sink de saída.")

        feedback.pushInfo(f"🔹 Criando buffer com distância = {distancia}")

        # Chamar buffer escrevendo diretamente no sink
        buffer_result = processing.run(
            "native:buffer",
            {
                "INPUT": exploded,
                "DISTANCE": distancia,
                "SEGMENTS": 5,
                "END_CAP_STYLE": 1,
                "JOIN_STYLE": 1,
                "MITER_LIMIT": 2,
                "DISSOLVE": False,
                "OUTPUT": dest_id  # <-- ESSENCIAL!
            },
            context=context,
            feedback=feedback
        )

        return {
            self.OUTPUT_RASTRO: dest_id
        }

    def name(self):
        return "gerar_rastro_implemento"

    def displayName(self):
        return "MTL - Gerar Rastro Implemento"

    def group(self):
        return "Martinelli"

    def groupId(self):
        return "martinelli"

    def shortHelpString(self):
        return "Explode linhas e cria polígono representando o rastro do implemento."

    def createInstance(self):
        return ImplementTrail()
