# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from .RasterMassSampler import RasterMassSampler
from .RasterMassClipper import RasterMassClipper
from .RasterOptimizer import RasterOptimizer
from .DifferenceFields import DifferenceFieldsAlgorithm
from .AttributeStatistics import AttributeStatistics
from .GeometryLineFromPoints import GeometryLineFromPoints
from .RasterDifferenceStatiscs import RasterDifferenceStatiscs
from .RasterWeightedAverage import RasterWeightedAverage
from .GridGenerator import GridGenerator
from .NdviCalculator import NdviCalculator
from .NdreCalculator import NdreCalculator
from .RgbMosaicCreator import RgbMosaicCreator
from .RgbStyleStandardizer import RgbStyleStandardizer
from .GliCalculator import GliCalculator
from ..i18n.TranslationManager import STR


class MTLProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        print("[DEBUG] Registrando algoritmos MTL…")
        self.addAlgorithm(RasterMassSampler())
        self.addAlgorithm(RasterMassClipper())
        self.addAlgorithm(RasterOptimizer())
        self.addAlgorithm(DifferenceFieldsAlgorithm())
        self.addAlgorithm(AttributeStatistics())
        self.addAlgorithm(GeometryLineFromPoints())
        self.addAlgorithm(RasterDifferenceStatiscs())
        self.addAlgorithm(RasterWeightedAverage())
        self.addAlgorithm(GridGenerator())
        self.addAlgorithm(NdviCalculator())
        self.addAlgorithm(NdreCalculator())
        self.addAlgorithm(RgbMosaicCreator())
        self.addAlgorithm(RgbStyleStandardizer())
        self.addAlgorithm(GliCalculator())

    def id(self):
        return "cadmus"

    def name(self):
        return STR.APP_NAME

    def longName(self):
        return "Cadmus – Processamento"

    def icon(self):
        path = os.path.join(
            os.path.dirname(__file__), "..", "resources", "icons", "cadmus_icon.ico"
        )
        return QIcon(path)
