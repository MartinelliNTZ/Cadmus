# -*- coding: utf-8 -*-
import os
from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider
from .raster_mass_sampler import RasterMassSampler
from .difference_fields_algorithm import DifferenceFieldsAlgorithm
from .attribute_statistics import AttributeStatisticsAlgorithm
#from .elevation_analisys import ElevationAnalisys


class MTLProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        print("[DEBUG] Registrando algoritmos MTL…")
        self.addAlgorithm(RasterMassSampler())
        self.addAlgorithm(DifferenceFieldsAlgorithm())  
        self.addAlgorithm(AttributeStatisticsAlgorithm())        
               
            
        """     try:
            self.addAlgorithm(ElevationAnalisys())  
        except :            
            print("Error: Cannot divide by zero!") """
        

    def id(self):
        return "cadmus"

    def name(self):
        return "Cadmus"

    def longName(self):
        return "Cadmus – Processamento"
    
    def icon(self):
        path = os.path.join(os.path.dirname(__file__), "..", "resources","icons", "cadmus_icon.ico")
        return QIcon(path)
