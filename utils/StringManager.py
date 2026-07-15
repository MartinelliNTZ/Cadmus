# -*- coding: utf-8 -*-
from ..core.enum.OutputFieldKey import StripOutputFieldKey
from ..core.model.Field import Field
from qgis.PyQt.QtCore import QVariant


import re
from ..i18n.TranslationManager import STR
from .BaseUtil import BaseUtil


class StringManager(BaseUtil):

    DIVIDE_STRIP_FIELDS = {
        StripOutputFieldKey.SHOT_ID: Field(
            label="Shot ID",
            attribute="shot_id",
            description="Identificador único do segmento de tiro/faixa.",
            type=QVariant.String,
            length=50,
            precision=0,
        ),
        StripOutputFieldKey.OLD_SHOT_ID: Field(
            label="Old Shot ID",
            attribute="old_shot_id",
            description="Identificador original do shot antes da validação de tamanho de grupo.",
            type=QVariant.String,
            length=50,
            precision=0,
        ),
        StripOutputFieldKey.SHOT_VALID: Field(
            label="Shot Valid",
            attribute="shot_valid",
            description="Indica se o tiro possui pontos suficientes para ser válido.",
            type=QVariant.Int,
            length=1,
            precision=0,
        ),
        StripOutputFieldKey.SCORE: Field(
            label="Score",
            attribute="score",
            description="Pontuação de quebra (direção + continuidade).",
            type=QVariant.Int,
            length=10,
            precision=0,
        ),
        StripOutputFieldKey.SCORE_DIRECTION: Field(
            label="Score Direction",
            attribute="score_direction",
            description="Componente de quebra por mudança de direção.",
            type=QVariant.Int,
            length=10,
            precision=0,
        ),
        StripOutputFieldKey.SCORE_CONTINUITY: Field(
            label="Score Continuity",
            attribute="score_continuity",
            description="Componente de quebra por descontinuidade temporal/espacial.",
            type=QVariant.Int,
            length=10,
            precision=0,
        ),
        StripOutputFieldKey.SEG_TYPE: Field(
            label="Segment Type",
            attribute="seg_type",
            description="Tipo: 'faixa' ou 'bordadura'.",
            type=QVariant.String,
            length=20,
            precision=0,
        ),
        StripOutputFieldKey.AZIMUTH_INSTANT: Field(
            label="Azimuth Instant",
            attribute="azimuth_instant",
            description="Azimute instantâneo entre pontos consecutivos.",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.AZIMUTH_MEAN: Field(
            label="Azimuth Mean",
            attribute="azimuth_mean",
            description="Média circular ponderada por velocidade.",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.DELTA_AZIMUTH: Field(
            label="Delta Azimuth",
            attribute="delta_azimuth",
            description="Diferença angular entre azimute instantâneo e média.",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.DELTA_TIME: Field(
            label="Delta Time",
            attribute="delta_time",
            description="Diferença de tempo entre pontos consecutivos (s).",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.DELTA_DISTANCE: Field(
            label="Delta Distance",
            attribute="delta_distance",
            description="Distância entre pontos consecutivos (m).",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.VELOCITY_INSTANT: Field(
            label="Velocity Instant",
            attribute="velocity_instant",
            description="Velocidade instantânea (m/s).",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.AZIMUTH_PREV: Field(
            label="Azimuth Prev",
            attribute="azimuth_prev",
            description="Azimute do segmento anterior (i-1 → i).",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.AZIMUTH_NEXT: Field(
            label="Azimuth Next",
            attribute="azimuth_next",
            description="Azimute do segmento seguinte (i → i+1).",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.DELTA_AZ_PREV: Field(
            label="Delta Azimuth Prev",
            attribute="delta_az_prev",
            description="Diferença angular entre azimute instantâneo e azimute anterior.",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
        StripOutputFieldKey.DELTA_AZ_NEXT: Field(
            label="Delta Azimuth Next",
            attribute="delta_az_next",
            description="Diferença angular entre azimute instantâneo e azimute seguinte.",
            type=QVariant.Double,
            length=20,
            precision=8,
        ),
    }
    MENU_CATEGORIES = {
        "SYSTEM": STR.MENU_SYSTEM,
        "LAYOUTS": STR.MENU_LAYOUTS,
        "FOLDER": STR.MENU_FOLDER,
        "VECTOR": STR.MENU_VECTOR,
        "AGRICULTURE": STR.MENU_AGRICULTURE,
        "RASTER": STR.MENU_RASTER,
    }
    KML_FIELDS = [
        "descriptio",
        "timestamp",
        "begin",
        "end",
        "altitudeMo",
        "tessellate",
        "extrude",
        "visibility",
        "drawOrder",
        "icon",
    ]

    # Filtros de arquivos
    FILTER_ALL = "All files (*.*)"
    FILTER_IMAGES = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff)"
    FILTER_VECTOR = "Shapefile (*.shp);;GeoPackage (*.gpkg);;GeoJSON (*.geojson *.json);;KML (*.kml);;CSV (*.csv)"
    FILTER_QGIS_STYLE = "QML files (*.qml)"
    SHP_EXTENSIONS = [".shp", ".shx", ".dbf", ".prj", ".cpg", ".qix"]
    VECTOR_DRIVERS = {
        ".shp": "ESRI Shapefile",
        ".gpkg": "GPKG",
        ".geojson": "GeoJSON",
        ".json": "GeoJSON",
        ".kml": "KML",
    }
    AVAILABLE_LANGUAGES = {
        "none": "🔧 " + STR.AUTO_DETECT,
        "es": "ES Español",
        "en": "EN English",
        "pt_BR": "BR Português",
        "de": "DE Deutsch",
    }
    VECTOR_EXTS = {
        ".shp",
        ".geojson",
        ".json",
        ".kml",
        ".kmz",
        ".gpx",
        ".csv",
        ".tab",
        ".las",
        ".laz",
        ".gpkg",
    }
    RASTER_EXTS = {".tif", ".tiff", ".ecw", ".jp2", ".asc"}

    DIVIDE_POINTS_STRIP_TYPES = ["Curva", "Reta", "Ambas"]

    DIVIDE_POINTS_OPERATIONAL_FIELDS = {
        "threshold_azimute_grave": {
            "title": STR.SEVERE_AZIMUTH_DEVIATION_THRESHOLD,
            "description": "Desvio alto de azimute que indica uma mudanca de direcao clara.",
            "type": "float",
            "default": 45.0,
        },
        "n_minimo_pontos": {
            "title": STR.MINIMUM_POINT_COUNT,
            "description": "Menor quantidade de pontos que um trecho precisa para ser aceito.",
            "type": "int",
            "default": 20,
        },
        "max_desvio": {
            "title": "Numero max de pontos desvio",
            "description": "Maximo de pontos fora do padrao que serao ignorados antes de confirmar a quebra.",
            "type": "int",
            "default": 2,
        },
        "max_distance": {
            "title": "Distância Máxima entre pontos",
            "description": "Distância máxima entre pontos para considerar uma quebra.",
            "type": "int",
            "default": 150,
        },
    }
    DIVIDE_POINTS_SENSITIVITY_FIELDS = {
        "janela_azimute": {
            "title": STR.AZIMUTH_MOVING_WINDOW,
            "description": "Numero de pontos usados para calcular a direcao media antes de detectar mudanca de rumo.",
            "type": "int",
            "default": 10,
        },
        "threshold_azimute_leve": {
            "title": STR.LIGHT_AZIMUTH_DEVIATION_THRESHOLD,
            "description": "Desvio leve de azimute que inicia a identificacao de uma possivel quebra.",
            "type": "float",
            "default": 20.0,
        },
        "score_minimo_quebra": {
            "title": STR.MINIMUM_BREAK_SCORE,
            "description": "Pontos necessarios para que o desvio seja considerado uma quebra real.",
            "type": "int",
            "default": 3,
        },
        "tolerancia_tempo": {
            "title": STR.TIME_TOLERANCE_MULTIPLIER,
            "description": "Multiplica a diferenca de tempo permitida entre fotos para evitar quebra por pequenas variacoes.",
            "type": "float",
            "default": 3.0,
        },
        "frequencia_pontos": {
            "title": STR.EXPECTED_POINT_FREQUENCY_SECONDS,
            "type": "int",
            "default": 1,
        },
        "largura_tiro": {
            "title": STR.EXPECTED_LATERAL_WIDTH_METERS,
            "type": "float",
            "default": 20.0,
        },
    }

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normaliza nomes de chaves para snake_case consistente."""
        if key is None:
            return ""
        key = re.sub(r"(?<!^)(?=[A-Z])", "_", str(key))
        key = key.replace(" ", "_").replace("-", "_").replace("/", "_")
        key = re.sub(r"_+", "_", key).strip("_")
        return key.lower()
