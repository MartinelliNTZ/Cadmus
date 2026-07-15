# -*- coding: utf-8 -*-
from enum import IntEnum


class LightSourceEnum(IntEnum):
    UNKNOWN = 0
    DAYLIGHT = 1
    FLUORESCENT = 2
    TUNGSTEN = 3
    FLASH = 4
    FINE_WEATHER = 9
    CLOUDY_WEATHER = 10
    SHADE = 11
    DAYLIGHT_FLUORESCENT = 12
    DAY_WHITE_FLUORESCENT = 13
    COOL_WHITE_FLUORESCENT = 14
    WHITE_FLUORESCENT = 15
    WARM_WHITE_FLUORESCENT = 16
    STANDARD_LIGHT_A = 17
    STANDARD_LIGHT_B = 18
    STANDARD_LIGHT_C = 19
    D55 = 20
    D65 = 21
    D75 = 22
    D50 = 23
    ISO_STUDIO_TUNGSTEN = 24
    OTHER_LIGHT_SOURCE = 255

    @classmethod
    def get_label(cls, code: int) -> str:
        entry = _LIGHT_SOURCE_META.get(int(code))
        return entry["value"] if entry else "Unknown"

    @classmethod
    def get_description(cls, code: int) -> str:
        entry = _LIGHT_SOURCE_META.get(int(code))
        return entry["description"] if entry else "Fonte de luz desconhecida."


_LIGHT_SOURCE_META = {
    0: {
        "value": "Unknown",
        "description": "Fonte de luz desconhecida ou nao especificada.",
    },
    1: {
        "value": "Daylight",
        "description": "Luz do dia natural (aprox. 5200K-6500K).",
    },
    2: {
        "value": "Fluorescent",
        "description": "Iluminacao fluorescente.",
    },
    3: {
        "value": "Tungsten",
        "description": "Iluminacao incandescente/tungstenio.",
    },
    4: {
        "value": "Flash",
        "description": "Fonte de luz proveniente de flash.",
    },
    9: {"value": "Fine Weather", "description": "Tempo claro."},
    10: {"value": "Cloudy Weather", "description": "Tempo nublado."},
    11: {"value": "Shade", "description": "Area de sombra."},
    12: {"value": "Daylight Fluorescent", "description": "Fluorescente daylight."},
    13: {"value": "Day White Fluorescent", "description": "Fluorescente branca diurna."},
    14: {"value": "Cool White Fluorescent", "description": "Fluorescente branca fria."},
    15: {"value": "White Fluorescent", "description": "Fluorescente branca."},
    16: {"value": "Warm White Fluorescent", "description": "Fluorescente branca quente."},
    17: {"value": "Standard Light A", "description": "Iluminante padrao A."},
    18: {"value": "Standard Light B", "description": "Iluminante padrao B."},
    19: {"value": "Standard Light C", "description": "Iluminante padrao C."},
    20: {"value": "D55", "description": "Iluminante D55 (5500K)."},
    21: {"value": "D65", "description": "Iluminante D65 (6500K)."},
    22: {"value": "D75", "description": "Iluminante D75 (7500K)."},
    23: {"value": "D50", "description": "Iluminante D50 (5000K)."},
    24: {"value": "ISO Studio Tungsten", "description": "Tungstenio de estudio ISO."},
    255: {"value": "Other Light Source", "description": "Outra fonte de luz."},
}
