# -*- coding: utf-8 -*-
from qgis.core import QgsDistanceArea, QgsProject


class VectorLayerMetrics:
    """
    Responsável pela leitura e cálculos espaciais de camadas vetoriais.
    
    Escopo:
    - Calcular métricas geométricas (área, comprimento, perímetro)
    - Gerar estatísticas espaciais
    - Medir distâncias e ângulos
    - Analisar distribuição de feições
    - Cálculos de densidade e concentração
    
    Responsabilidade Principal:
    - Fornecer cálculos e análises espaciais precisas
    - Garantir acurácia em medições
    - NÃO alterar dados
    
    NÃO é Responsabilidade:
    - Transformar geometrias (use VectorLayerGeometry)
    - Reprojetar (use VectorLayerProjection)
    - Manipular atributos (use VectorLayerAttributes)
    - Carregar ou salvar (use VectorLayerSource)
    """

    def calculate_feature_area(self, feature, external_tool_key="untraceable"):
        """Calcula a área total de uma feição em unidades do CRS."""
        pass

    def calculate_feature_length(self, feature, external_tool_key="untraceable"):
        """Calcula o comprimento total de uma feição em unidades do CRS."""
        pass

    def calculate_feature_perimeter(self, feature, external_tool_key="untraceable"):
        """Calcula o perímetro de uma feição em unidades do CRS."""
        pass

    def get_layer_total_area(self, layer, external_tool_key="untraceable"):
        """Calcula a área total de todas as feições da camada."""
        pass

    def get_layer_total_length(self, layer, external_tool_key="untraceable"):
        """Calcula o comprimento total de todas as feições da camada."""
        pass

    def get_layer_extent_area(self, layer, external_tool_key="untraceable"):
        """Calcula a área do retângulo envolvente (extent) da camada."""
        pass

    def calculate_feature_count_by_area(self, layer, area_ranges, external_tool_key="untraceable"):
        """Agrupa e conta feições por intervalos de área especificados."""
        pass

    def get_feature_centroid(self, feature, external_tool_key="untraceable"):
        """Calcula o centroide de uma feição."""
        pass

    def get_layer_centroid(self, layer, external_tool_key="untraceable"):
        """Calcula o centroide geral de todas as feições da camada."""
        pass

    def calculate_distance_between_features(self, feature1, feature2, external_tool_key="untraceable"):
        """Calcula a distância entre duas feições."""
        pass

    def get_layer_density_statistics(self, layer, grid_size, external_tool_key="untraceable"):
        """Calcula estatísticas de densidade de feições em uma grade."""
        pass

    def analyze_spatial_distribution(self, layer, external_tool_key="untraceable"):
        """Analisa o padrão de distribuição espacial das feições."""
        pass

    @staticmethod
    def calculate_line_length(layer, field_name, use_ellipsoidal=True, precision: int = 4):
        """
        Calcula comprimento de linhas (elipsoidal ou cartesiano).
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial de linhas
        field_name : str
            Nome do campo para armazenar comprimento
        use_ellipsoidal : bool
            Se True usa modelo elipsoidal, False usa cartesiano (padrão: True)
        precision : int
            Casas decimais para arredondamento e definição de campo
        """
        if not layer or not layer.isValid():
            return
            
        if not layer.isEditable():
            layer.startEditing()
        
        from qgis.core import QgsField
        from qgis.PyQt.QtCore import QVariant
        
        # Criar campo se não existir
        if layer.fields().lookupField(field_name) == -1:
            layer.addAttribute(
                QgsField(field_name, QVariant.Double, len=16, prec=precision)
            )
            layer.updateFields()
        
        if use_ellipsoidal:
            # Configurar medidor elipsoidal
            d = QgsDistanceArea()
            d.setSourceCrs(
                layer.crs(),
                QgsProject.instance().transformContext()
            )
            
            ellipsoid = layer.crs().ellipsoidAcronym()
            if not ellipsoid:
                ellipsoid = "WGS84"
            
            d.setEllipsoid(ellipsoid)
            
            # Calcular comprimento elipsoidal
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom and not geom.isEmpty():
                    length_m = d.measureLength(geom)
                    feat[field_name] = round(length_m, precision)
                    layer.updateFeature(feat)
        else:
            # Calcular comprimento cartesiano (projetado)
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom and not geom.isEmpty():
                    length = geom.length()
                    feat[field_name] = round(length, precision)
                    layer.updateFeature(feat)

    @staticmethod
    def calculate_polygon_area(layer, field_name, use_ellipsoidal=True, precision: int = 4):
        """
        Calcula área de polígonos em hectares (elipsoidal ou cartesiano).
        
        precision : int
            Casas decimais para arredondamento e definição de campo
        
        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial de polígonos
        field_name : str
            Nome do campo para armazenar área em hectares
        use_ellipsoidal : bool
            Se True usa modelo elipsoidal, False usa cartesiano (padrão: True)
        """
        if not layer or not layer.isValid():
            return
            
        if not layer.isEditable():
            layer.startEditing()
        
        from qgis.core import QgsField
        from qgis.PyQt.QtCore import QVariant
        
        # Criar campo se não existir
        if layer.fields().lookupField(field_name) == -1:
            layer.addAttribute(
                QgsField(field_name, QVariant.Double, len=16, prec=precision)
            )
            layer.updateFields()
        
        if use_ellipsoidal:
            # Configurar medidor elipsoidal
            d = QgsDistanceArea()
            d.setSourceCrs(
                layer.crs(),
                QgsProject.instance().transformContext()
            )
            
            ellipsoid = layer.crs().ellipsoidAcronym()
            if not ellipsoid:
                ellipsoid = "WGS84"
            
            d.setEllipsoid(ellipsoid)
            
            # Calcular área elipsoidal
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom and not geom.isEmpty():
                    area_m2 = d.measureArea(geom)
                    area_ha = area_m2 / 10000.0
                    feat[field_name] = round(area_ha, precision)
                    layer.updateFeature(feat)
        else:
            # Calcular área cartesiana (projetada)
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if geom and not geom.isEmpty():
                    area_m2 = geom.area()
                    area_ha = area_m2 / 10000.0
                    feat[field_name] = round(area_ha, precision)
                    layer.updateFeature(feat)
