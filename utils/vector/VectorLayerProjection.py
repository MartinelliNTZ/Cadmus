# -*- coding: utf-8 -*-

from typing import Optional, List, Dict

from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsUnitTypes,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
)


class VectorLayerProjection:
    """
    Responsável por:

    - CRS
    - Conversão de unidades
    - Reprojeção

    NÃO salva camada.
    NÃO valida regra de negócio.
    NÃO altera atributos.
    """

    # ---------------------------------------------------------
    # CONVERSÃO DE DISTÂNCIA
    # ---------------------------------------------------------
    @staticmethod
    def convert_distance_to_layer_units(
        layer: QgsVectorLayer, distance_meters: float
    ) -> float:
        """
        Converte uma distância em METROS
        para a unidade da camada.

        Dialog nunca deve saber se é grau, metro ou pé.
        """

        if not layer or not layer.isValid():
            return distance_meters

        crs = layer.crs()
        unit = crs.mapUnits()

        # Se já estiver em metros
        if unit == QgsUnitTypes.DistanceMeters:
            return distance_meters

        # Se estiver em graus (ex: EPSG:4326)
        if unit == QgsUnitTypes.DistanceDegrees:
            # Conversão média aproximada
            # 1 grau ≈ 111320 metros
            return distance_meters / 111320.0

        # Outras unidades (feet, etc.)
        factor = QgsUnitTypes.fromUnitToUnitFactor(QgsUnitTypes.DistanceMeters, unit)

        return distance_meters * factor

    # ---------------------------------------------------------
    # REPROJEÇÃO EM MEMÓRIA
    # ---------------------------------------------------------
    @staticmethod
    def reproject_layer(
        layer: QgsVectorLayer, target_crs: QgsCoordinateReferenceSystem
    ) -> Optional[QgsVectorLayer]:
        """
        Cria uma nova camada em memória reprojetada.
        """

        if not layer or not layer.isValid():
            return None

        if not target_crs or not target_crs.isValid():
            return None

        source_crs = layer.crs()

        if source_crs == target_crs:
            return layer

        uri = f"{layer.wkbType()}?crs={target_crs.authid()}"
        new_layer = QgsVectorLayer(uri, f"{layer.name()}_reprojected", "memory")

        provider = new_layer.dataProvider()
        provider.addAttributes(layer.fields())
        new_layer.updateFields()

        transform = QgsCoordinateTransform(
            source_crs, target_crs, QgsProject.instance().transformContext()
        )

        feats = []

        for feat in layer.getFeatures():
            new_feat = QgsFeature(layer.fields())
            new_feat.setAttributes(feat.attributes())

            geom = feat.geometry()
            if geom and not geom.isEmpty():
                geom = QgsGeometry(geom)
                geom.transform(transform)
                new_feat.setGeometry(geom)

            feats.append(new_feat)

        provider.addFeatures(feats)
        new_layer.updateExtents()

        return new_layer

    # ---------------------------------------------------------
    # GARANTIR CRS ESPECÍFICO
    # ---------------------------------------------------------
    @staticmethod
    def ensure_crs(
        layer: QgsVectorLayer, target_crs: QgsCoordinateReferenceSystem
    ) -> Optional[QgsVectorLayer]:
        """
        Garante que a camada esteja no CRS desejado.
        Se já estiver, retorna ela mesma.
        Caso contrário, reprojeta.
        """

        if not layer or not layer.isValid():
            return None

        if layer.crs() == target_crs:
            return layer

        return VectorLayerProjection.reproject_layer(layer, target_crs)

    @staticmethod
    def is_geographic_crs(layer: QgsVectorLayer) -> bool:
        """
        Verifica se o CRS da camada é geográfico (WGS84, EPSG:4326, etc).

        Parameters
        ----------
        layer : QgsVectorLayer
            Camada vetorial a verificar

        Returns
        -------
        bool
            True se CRS é geográfico (lat/lon), False se projetado
        """
        if not layer or not layer.isValid():
            return False

        crs = layer.crs()
        return crs.isGeographic()

    def get_layer_crs(self, layer, external_tool_key="untraceable"):
        """Obtém o CRS atual da camada."""
        pass

    def set_layer_crs(self, layer, target_crs, external_tool_key="untraceable"):
        """Define o CRS da camada sem reprojetar (apenas muda a definição)."""
        pass

    def validate_crs_compatibility(
        self, layer1, layer2, external_tool_key="untraceable"
    ):
        """Verifica se duas camadas possuem CRS compatíveis ou próximos."""
        pass

    def get_layer_unit_type(self, layer, external_tool_key="untraceable"):
        """Obtém o tipo de unidade de medida do CRS da camada (metros, graus, etc)."""
        pass

    def convert_distance_unit(
        self, distance_value, from_unit, to_unit, external_tool_key="untraceable"
    ):
        """Converte um valor de distância entre diferentes unidades de medida."""
        pass

    def convert_area_unit(
        self, area_value, from_unit, to_unit, external_tool_key="untraceable"
    ):
        """Converte um valor de área entre diferentes unidades de medida."""
        pass

    def get_layer_extent_in_different_crs(
        self, layer, target_crs, external_tool_key="untraceable"
    ):
        """Calcula a extensão da camada quando projetada em um CRS diferente."""
        pass

    def check_layer_is_geographic_crs(self, layer, external_tool_key="untraceable"):
        """Verifica se a camada usa sistema de coordenadas geográficas (lat/lon)."""
        pass

    def check_layer_is_projected_crs(self, layer, external_tool_key="untraceable"):
        """Verifica se a camada usa sistema de coordenadas projetado."""
        pass

    def get_crs_axis_order(self, crs, external_tool_key="untraceable"):
        """Obtém a ordem de eixos do CRS (XY ou YX)."""
        pass

    def list_common_crs_for_region(self, region_code, external_tool_key="untraceable"):
        """Lista os CRS mais comuns e apropriados para uma região geográfica."""
        pass

    # ---------------------------------------------------------
    # REPROJEÇÃO DE FEATURES (movido de ProjectionHelper)
    # ---------------------------------------------------------
    @staticmethod
    def reproject_features(
        features: List[QgsFeature],
        source_crs: QgsCoordinateReferenceSystem,
        target_crs: QgsCoordinateReferenceSystem,
        context,
    ) -> List[QgsFeature]:
        """
        Reprojeta uma lista de features entre CRS diferentes.

        Movido de ProjectionHelper para consolidar lógica de projeção.

        Parameters
        ----------
        features : List[QgsFeature]
            Lista de QgsFeature a reprojetar
        source_crs : QgsCoordinateReferenceSystem
            CRS de origem
        target_crs : QgsCoordinateReferenceSystem
            CRS de destino
        context : QgsProcessingContext
            Contexto de processamento com transformContext()

        Returns
        -------
        List[QgsFeature]
            Nova lista de features reprojetadas
        """
        if not target_crs.isValid():
            return features

        transform = QgsCoordinateTransform(
            source_crs, target_crs, context.transformContext()
        )
        reproj = []

        for feat in features:
            new_feat = QgsFeature(feat)
            geom = feat.geometry()

            if geom is not None:
                new_geom = QgsGeometry(geom)
                new_geom.transform(transform)
                new_feat.setGeometry(new_geom)

            reproj.append(new_feat)

        return reproj

    # ---------------------------------------------------------
    # INFORMAÇÕES DE COORDENADAS (movido de crs_utils)
    # ---------------------------------------------------------
    @staticmethod
    def _decimal_to_dms(value: float) -> str:
        """Converte coordenada decimal para DMS (graus, minutos, segundos)."""
        sign = "-" if value < 0 else ""
        value = abs(value)
        deg = int(value)
        minutes_full = (value - deg) * 60
        minutes = int(minutes_full)
        seconds = (minutes_full - minutes) * 60
        return f"{sign}{deg}°{minutes}'{seconds:.3f}\""

    @staticmethod
    def _utm_zone_from_lon(lon: float) -> int:
        """Calcula zona UTM a partir da longitude."""
        return int((lon + 180) / 6) + 1

    @staticmethod
    def _utm_letter_from_lat(lat: float) -> str:
        """Calcula letra UTM a partir da latitude."""
        # Letras UTM (C–X, sem I e O)
        UTM_LETTERS = "CDEFGHJKLMNPQRSTUVWX"
        if lat < -80 or lat > 84:
            return ""
        index = int((lat + 80) / 8)
        return UTM_LETTERS[index]

    @staticmethod
    def get_coordinate_info(
        point: QgsPoint, canvas_crs: QgsCoordinateReferenceSystem
    ) -> Dict:
        """
        Obtém informações de coordenada em múltiplos formatos.

        Movido de crs_utils.get_coord_info() para consolidar lógica de projeção.

        Parameters
        ----------
        point : QgsPoint
            Ponto em coordenadas do canvas
        canvas_crs : QgsCoordinateReferenceSystem
            CRS do canvas

        Returns
        -------
        Dict
            Dicionário com informações:
            - lat, lon: coordenadas WGS84
            - lat_dms, lon_dms: formato DMS
            - utm_x, utm_y: coordenadas UTM SIRGAS 2000
            - zona_num, zona_letra: zona UTM
            - hemisferio: "Norte" ou "Sul"
            - epsg: código EPSG da zona UTM
        """
        # Transformar para WGS84
        crs_wgs = QgsCoordinateReferenceSystem("EPSG:4326")
        transform = QgsCoordinateTransform(
            canvas_crs, crs_wgs, QgsProject.instance().transformContext()
        )
        p_wgs = transform.transform(point)

        lon = p_wgs.x()
        lat = p_wgs.y()

        zona = VectorLayerProjection._utm_zone_from_lon(lon)
        letra = VectorLayerProjection._utm_letter_from_lat(lat)

        # SIRGAS 2000 UTM
        epsg_utm_sirgas = 31960 + zona
        crs_utm_sirgas = QgsCoordinateReferenceSystem(f"EPSG:{epsg_utm_sirgas}")
        transform_utm = QgsCoordinateTransform(
            canvas_crs, crs_utm_sirgas, QgsProject.instance().transformContext()
        )
        p_utm_sirgas = transform_utm.transform(point)

        hemisferio = "Sul" if lat < 0 else "Norte"

        return {
            "lat": lat,
            "lon": lon,
            "lat_dms": VectorLayerProjection._decimal_to_dms(lat),
            "lon_dms": VectorLayerProjection._decimal_to_dms(lon),
            "utm_x": p_utm_sirgas.x(),
            "utm_y": p_utm_sirgas.y(),
            "zona_num": zona,
            "zona_letra": letra,
            "hemisferio": hemisferio,
            "epsg": epsg_utm_sirgas,
        }
