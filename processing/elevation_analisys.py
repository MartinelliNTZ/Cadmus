# -*- coding: utf-8 -*-
import os
from PyQt5.QtGui import QIcon

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterCrs,
    QgsFeatureSink,
    QgsProcessing
)

# Preferências
from ..utils.Preferences import load_tool_prefs, save_tool_prefs

# Lógicas externas
from .model.raster_mass_sampler_model import RasterMassSamplerModel
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from ..utils.ToolKeys import ToolKey
#from ..qgis_model.implement_trail.py import ....


TOOL_KEY = ToolKey.ELEVATION_ANALISYS


class ElevationAnalisys(QgsProcessingAlgorithm):

    INPUT_POINTS = "INPUT_POINTS"
    INPUT_RASTERS = "INPUT_RASTERS"
    OUTPUT_CRS = "OUTPUT_CRS"
    OUTPUT = "OUTPUT"

    def name(self):
        return "raster_mass_sampler"

    def displayName(self):
        return "Análise de Elevação"

    def createInstance(self):
        return ElevationAnalisys()

    # -------------------------- INIT -------------------------
    def initAlgorithm(self, config=None):

        prefs = load_tool_prefs(TOOL_KEY)

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                "Pontos de entrada",
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                "Rasters",
                QgsProcessing.TypeRaster
            )
        )

        # Agora só existe CRS DE SAÍDA
        self.addParameter(
            QgsProcessingParameterCrs(
                self.OUTPUT_CRS,
                "Reprojetar camada de saída (opcional)",
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Valores_Amostrados"
            )
        )

    # ----------------------- PROCESS -------------------------
    def processAlgorithm(self, params, context, feedback):

        pts = self.parameterAsSource(params, self.INPUT_POINTS, context)
        rasters = self.parameterAsLayerList(params, self.INPUT_RASTERS, context)

        # ----------------- CRS DE SAÍDA -----------------
        output_crs = None
        output_crs = self.parameterAsCrs(params, self.OUTPUT_CRS, context)
        if not output_crs.isValid():
            output_crs = None

        # Salva preferência (sempre somente o CRS de saída)
        
 

        feedback.pushInfo(f"CRS de saída: {output_crs.authid() if output_crs else 'None'}")

        # ----------------- EXECUTA A LÓGICA -----------------
        logic = RasterMassSamplerModel()
        out_fields, features = logic.process(
            pts,
            rasters,
            context,
            feedback,
            # sem CRS de entrada
            forced_input_crs=None
        )

        # ----------------- REPROJEÇÃO SE NECESSÁRIO -----------------
        if output_crs:
            source_crs = pts.sourceCrs()

            features = VectorLayerProjection.reproject_features(
                features,
                source_crs,
                output_crs,
                context
            )

        final_crs = output_crs if output_crs else pts.sourceCrs()

        # ----------------- SINK -----------------
        sink, dest = self.parameterAsSink(
            params,
            self.OUTPUT,
            context,
            out_fields,
            pts.wkbType(),
            final_crs
        )

        for f in features:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        # ----------------- LINK E PREFERÊNCIAS DE SAÍDA -----------------
        if dest and isinstance(dest, str) and not dest.startswith("memory:"):
            out_folder = os.path.dirname(dest)
            clickable = f"<a href=\"file:///{out_folder}\">{out_folder}</a>"
            feedback.pushInfo(f"Arquivo salvo em: {clickable}")

            prefs = load_tool_prefs(TOOL_KEY)
            prefs["last_output_folder"] = out_folder
            prefs["last_output_file"] = dest
            save_tool_prefs(TOOL_KEY, prefs)

        return {self.OUTPUT: dest}

    # ------------------------ UI INFO ------------------------
    def icon(self):
        path = os.path.join(os.path.dirname(__file__), "..", "resources","icons", "raster_mass.ico")
        return QIcon(path)

    def group(self):
        return "Estatistica"

    def groupId(self):
        return "estatistica"
