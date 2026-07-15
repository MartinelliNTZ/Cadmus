# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET  # nosec B405  # defusedxml nao disponivel no QGIS 3.16; XML gerado internamente
from xml.dom import minidom  # nosec B408  # usado apenas para pretty-print, nao para parsing externo
from typing import Optional, Dict

from ..utils.BaseUtil import BaseUtil
from ..utils.ToolKeys import ToolKey
from ..core.config.LogUtils import LogUtils
logger = LogUtils(tool="Untraceable", class_name="None")


class XmlUtil(BaseUtil):
    """
    Utilitário para manipulação de XML e QML (QGIS Style Layer).

    Responsabilidades:
    - Criar, carregar e salvar documentos XML
    - Construir estilos QML para camadas raster (multiband, singleband)
    - Manipular elementos e atributos XML
    - Gerar XML formatado (pretty-print)
    """

    @staticmethod
    def create_element(
        tag: str, attrib: Optional[Dict[str, str]] = None, text: str = None
    ) -> ET.Element:
        """Cria um elemento XML com atributos e texto opcionais."""
        elem = ET.Element(tag, attrib or {})
        if text is not None:
            elem.text = text
        return elem

    @staticmethod
    def add_sub_element(
        parent: ET.Element,
        tag: str,
        attrib: Optional[Dict[str, str]] = None,
        text: str = None,
    ) -> ET.Element:
        """Adiciona um sub-elemento a um elemento pai."""
        child = XmlUtil.create_element(tag, attrib, text)
        parent.append(child)
        return child

    @staticmethod
    def pretty_xml(root: ET.Element, with_declaration: bool = False) -> str:
        """Converte um ElementTree em string XML formatada (pretty-print).

        Args:
            root: Elemento raiz
            with_declaration: Se True, inclui <?xml version="1.0" ?>.
                              QML nao deve ter declaracao - use False.
        """
        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)  # nosec B318  # string gerada internamente por ET.tostring, nao externa
        result = reparsed.toprettyxml(indent="  ")
        if not with_declaration:
            # Remove a primeira linha <?xml version="1.0" ?> se presente
            lines = result.splitlines()
            if lines and "<?xml" in lines[0]:
                result = "\n".join(lines[1:])
        return result

    @staticmethod
    def save_xml(root: ET.Element, file_path: str) -> bool:
        """Salva um documento XML em arquivo com formatação pretty-print."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            xml_str = XmlUtil.pretty_xml(root, with_declaration=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(xml_str)
            return True
        except Exception as e:
            logger.debug(f"save_xml: failed with error: {e}")
            return False

    @staticmethod
    def load_xml(file_path: str) -> Optional[ET.Element]:
        """Carrega um arquivo XML e retorna o elemento raiz."""
        try:
            tree = ET.parse(file_path)  # nosec B314  # defusedxml nao disponivel; arquivos QML gerados internamente
            return tree.getroot()
        except Exception as e:
            logger.debug(f"load_xml: failed with error: {e}")
            return None

    @staticmethod
    def save_qml_style(root: ET.Element, file_path: str) -> bool:
        """
        Salva um estilo QML no formato que o QGIS espera:
        - SEM declaracao <?xml ...?>
        - PRIMEIRA linha: <!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
        - Em seguida: elemento raiz <qgis> formatado
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Gera XML pretty sem declaracao
            xml_str = XmlUtil.pretty_xml(root, with_declaration=False)
            # Remove qualquer DOCTYPE existente (se o minidom gerou um)
            lines = xml_str.splitlines()
            cleaned_lines = [las for las in lines if "<!DOCTYPE" not in las]
            # Reconstroi com o DOCTYPE na primeira linha
            doctype = "<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>"
            # Remove linhas vazias do inicio
            while cleaned_lines and cleaned_lines[0].strip() == "":
                cleaned_lines.pop(0)
            # Remove leading blank lines
            final_lines = [doctype, ""] + cleaned_lines
            result = "\n".join(final_lines)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result)
            return True
        except Exception as e:
            logger.debug(f"save_qml_style: failed with error: {e}")
            return False

    @staticmethod
    def build_raster_multiband_qml(
        min_value: float,
        max_value: float,
        red_band: int = 1,
        green_band: int = 2,
        blue_band: int = 3,
        alpha_band: int = -1,
        opacity: float = 1.0,
        algorithm: str = "StretchToMinimumMaximum",
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> ET.Element:
        """
        Constrói um documento QML para renderizador multiband colorido.

        Args:
            min_value: Valor mínimo para contraste (aplicado a todas as bandas RGB)
            max_value: Valor máximo para contraste (aplicado a todas as bandas RGB)
            red_band: Número da banda vermelha (1-indexed)
            green_band: Número da banda verde (1-indexed)
            blue_band: Número da banda azul (1-indexed)
            alpha_band: Número da banda alpha (-1 = none)
            opacity: Opacidade do raster (0.0 a 1.0)
            algorithm: Algoritmo de contraste (ex: StretchToMinimumMaximum)
            tool_key: Chave da ferramenta para logging

        Returns:
            ElementTree.Element com o documento QML completo
        """
        logger = BaseUtil._get_logger(tool_key, "XmlUtil")

        # Elemento raiz qgis
        qgis_attrib = {
            "autoRefreshTime": "0",
            "version": "3.34.12-Prizren",
            "maxScale": "0",
            "hasScaleBasedVisibilityFlag": "0",
            "minScale": "1e+08",
            "autoRefreshMode": "Disabled",
            "styleCategories": "AllStyleCategories",
        }
        root = ET.Element("qgis", qgis_attrib)

        # flags
        flags = ET.SubElement(root, "flags")
        ET.SubElement(flags, "Identifiable").text = "1"
        ET.SubElement(flags, "Removable").text = "1"
        ET.SubElement(flags, "Searchable").text = "1"
        ET.SubElement(flags, "Private").text = "0"

        # temporal
        temporal = ET.SubElement(
            root, "temporal", {"fetchMode": "0", "enabled": "0", "mode": "0"}
        )
        fixed_range = ET.SubElement(temporal, "fixedRange")
        ET.SubElement(fixed_range, "start")
        ET.SubElement(fixed_range, "end")

        # elevation
        elevation = ET.SubElement(
            root,
            "elevation",
            {
                "zoffset": "0",
                "symbology": "Line",
                "enabled": "0",
                "band": "1",
                "zscale": "1",
            },
        )
        data_def_props = ET.SubElement(elevation, "data-defined-properties")
        option = ET.SubElement(data_def_props, "Option", {"type": "Map"})
        ET.SubElement(
            option, "Option", {"type": "QString", "name": "name", "value": ""}
        )
        name_props = ET.SubElement(
            option, "name", {"type": "QString", "name": "name", "value": ""}
        )
        type_props = ET.SubElement(
            option, "type", {"type": "QString",
                             "name": "type", "value": "collection"}
        )

        # customproperties
        customproperties = ET.SubElement(root, "customproperties")
        option_cp = ET.SubElement(customproperties, "Option", {"type": "Map"})
        ET.SubElement(
            option_cp,
            "Option",
            {"type": "bool", "name": "WMSBackgroundLayer", "value": "false"},
        )
        ET.SubElement(
            option_cp,
            "Option",
            {"type": "bool", "name": "WMSPublishDataSourceUrl", "value": "false"},
        )
        ET.SubElement(
            option_cp,
            "Option",
            {"type": "int", "name": "embeddedWidgets/count", "value": "0"},
        )
        ET.SubElement(
            option_cp,
            "Option",
            {"type": "QString", "name": "identify/format", "value": "Value"},
        )

        # mapTip
        ET.SubElement(root, "mapTip", {"enabled": "1"})

        # pipe-data-defined-properties
        pipe_ddp = ET.SubElement(root, "pipe-data-defined-properties")
        option_pipe = ET.SubElement(pipe_ddp, "Option", {"type": "Map"})
        ET.SubElement(
            option_pipe, "Option", {
                "type": "QString", "name": "name", "value": ""}
        )
        props_pipe = ET.SubElement(option_pipe, "properties")
        type_pipe = ET.SubElement(
            option_pipe,
            "type",
            {"type": "QString", "name": "type", "value": "collection"},
        )

        # pipe
        pipe = ET.SubElement(root, "pipe")

        # provider
        provider = ET.SubElement(pipe, "provider")
        resampling = ET.SubElement(
            provider,
            "resampling",
            {
                "zoomedOutResamplingMethod": "nearestNeighbour",
                "enabled": "false",
                "maxOversampling": "2",
                "zoomedInResamplingMethod": "nearestNeighbour",
            },
        )

        # rasterrenderer
        renderer_attrib = {
            "blueBand": str(blue_band),
            "alphaBand": str(alpha_band),
            "type": "multibandcolor",
            "redBand": str(red_band),
            "nodataColor": "",
            "greenBand": str(green_band),
            "opacity": str(opacity),
        }
        rasterrenderer = ET.SubElement(pipe, "rasterrenderer", renderer_attrib)
        ET.SubElement(rasterrenderer, "rasterTransparency")

        # minMaxOrigin
        min_max_origin = ET.SubElement(rasterrenderer, "minMaxOrigin")
        ET.SubElement(min_max_origin, "limits").text = "None"
        ET.SubElement(min_max_origin, "extent").text = "WholeRaster"
        ET.SubElement(min_max_origin, "statAccuracy").text = "Estimated"
        ET.SubElement(min_max_origin, "cumulativeCutLower").text = "0.02"
        ET.SubElement(min_max_origin, "cumulativeCutUpper").text = "0.98"
        ET.SubElement(min_max_origin, "stdDevFactor").text = "2"

        min_str = f"{min_value:.7f}"
        max_str = f"{max_value:.7f}"

        # Red contrast enhancement
        red_ce = ET.SubElement(rasterrenderer, "redContrastEnhancement")
        ET.SubElement(red_ce, "minValue").text = min_str
        ET.SubElement(red_ce, "maxValue").text = max_str
        ET.SubElement(red_ce, "algorithm").text = algorithm

        # Green contrast enhancement
        green_ce = ET.SubElement(rasterrenderer, "greenContrastEnhancement")
        ET.SubElement(green_ce, "minValue").text = min_str
        ET.SubElement(green_ce, "maxValue").text = max_str
        ET.SubElement(green_ce, "algorithm").text = algorithm

        # Blue contrast enhancement
        blue_ce = ET.SubElement(rasterrenderer, "blueContrastEnhancement")
        ET.SubElement(blue_ce, "minValue").text = min_str
        ET.SubElement(blue_ce, "maxValue").text = max_str
        ET.SubElement(blue_ce, "algorithm").text = algorithm

        # brightnesscontrast
        brightness_contrast = ET.SubElement(
            pipe,
            "brightnesscontrast",
            {
                "brightness": "0",
                "gamma": "1",
                "contrast": "0",
            },
        )

        # huesaturation
        huesaturation = ET.SubElement(
            pipe,
            "huesaturation",
            {
                "colorizeGreen": "128",
                "grayscaleMode": "0",
                "invertColors": "0",
                "colorizeStrength": "100",
                "colorizeBlue": "128",
                "colorizeRed": "255",
                "saturation": "0",
                "colorizeOn": "0",
            },
        )

        # rasterresampler
        ET.SubElement(pipe, "rasterresampler", {"maxOversampling": "2"})

        # resamplingStage
        ET.SubElement(pipe, "resamplingStage").text = "resamplingFilter"

        # blendMode
        ET.SubElement(root, "blendMode").text = "0"

        # ── Logging de todas as variáveis do método ──
        logger.debug(
            f"build_raster_multiband_qml executado | "
            f"name_props={name_props} | "
            f"type_props={type_props} | "
            f"props_pipe={props_pipe} | "
            f"type_pipe={type_pipe} | "
            f"resampling={resampling} | "
            f"brightness_contrast={brightness_contrast} | "
            f"huesaturation={huesaturation}"
        )
        return root
