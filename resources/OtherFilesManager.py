# -** coding: utf-8 -***-

import os


class OtherFilesManager:
    VECTOR_PATH = os.path.join(os.path.dirname(__file__), "vectors")
    LINE_VECTOR = 'line.gpkg'
    INDICE_GLI_STYLE = "indice_gli_8_classes.qml"
    INDICE_NDVI_STYLE = "indice_ndvi_8_classes.qml"
    INDICE_NDRE_STYLE = "indice_ndvi_8_classes.qml"
    STYLE_PATH = os.path.join(os.path.dirname(__file__), "qml")

    @classmethod
    def vector_path(cls, name: str) -> str:
        """
        Retorna o caminho completo do vetor a partir do nome do arquivo.
        """
        return os.path.join(cls.VECTOR_PATH, name)

    @classmethod
    def style_path(cls, name: str) -> str:
        """
        Retorna o caminho completo do arquivo de estilo a partir do nome do arquivo.
        """
        return os.path.join(cls.STYLE_PATH, name)
