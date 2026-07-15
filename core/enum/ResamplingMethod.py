from enum import Enum


class ResamplingMethod(Enum):
    VIZINHO_MAIS_PROXIMO = 0
    BILINEAR = 1
    CUBICO = 2
    CUBICO_SUAVIZADO = 3
    LANCZOS_WINDOWED_SINC = 4
    MEDIA = 5
    MODO = 6
    MAXIMO = 7
    MINIMO = 8
    MEDIANA = 9
    PRIMEIRO_QUARTIL = 10
    TERCEIRO_QUARTIL = 11

    def __str__(self):
        return self.name.replace("_", " ").title()
