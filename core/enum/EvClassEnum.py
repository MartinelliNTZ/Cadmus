# -*- coding: utf-8 -*-
from enum import Enum


class EvClassEnum(Enum):
    """Classificação textual do Exposure Value (EV) para fotografia aérea.

    A ordem de prioridade para fotogrametria (melhor para pior):
    5 - Nublado (luz difusa, sem sombras)
    4 - Luz solar normal (iluminacao equilibrada)
    3 - Indoor/sombra (subexposicao)
    2 - Sol muito forte/neve (superexposicao, sombras duras)
    1 - Noite/escuro (subexposicao extrema)
    """

    NOITE_ESCURO = (0, 4, "noite/escuro")
    SOL_MUITO_FORTE = (15, 999, "sol muito forte/neve")
    INDOOR_SOMBRA = (5, 8, "indoor/sombra")
    LUZ_SOLAR_NORMAL = (12, 14, "luz solar normal")
    NUBLADO = (9, 12, "nublado")

    def __init__(self, min_ev: int, max_ev: int, label: str):
        self.min_ev = min_ev
        self.max_ev = max_ev
        self.label = label

    @classmethod
    def get_label(cls, ev_value: float) -> str:
        """
        Retorna a classificação textual para um dado valor de EV.

        Args:
            ev_value: Valor de Exposure Value (EV)

        Returns:
            String com a classificação textual (ex: "nublado")
        """
        if ev_value is None or ev_value < 0:
            return "Unknown"

        for ev_class in cls:
            if ev_class.min_ev <= ev_value <= ev_class.max_ev:
                return ev_class.label

        return "Unknown"

    @classmethod
    def get_level(cls, ev_value: float) -> int:
        """
        Retorna o nivel (1-5) para um dado valor de EV conforme o config.yaml.
        Usa o label textual e o mapping do config.yaml para consistencia.

        Args:
            ev_value: Valor de Exposure Value (EV)

        Returns:
            Inteiro de 1 a 5 representando o nivel
        """
        label = cls.get_label(ev_value)
        mapping = {
            "noite/escuro": 1,
            "sol muito forte/neve": 2,
            "indoor/sombra": 3,
            "luz solar normal": 4,
            "nublado": 5,
        }
        return mapping.get(label, 3)
