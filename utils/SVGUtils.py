# -*- coding: utf-8 -*-
import os
import re
from typing import List, Optional
from xml.sax.saxutils import (
    escape,
)  # nosec B406  # XML escape para gerar SVG, não para parsing
from ..core.config.LogUtils import LogUtils
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsRenderContext,
    QgsSymbol,
    QgsVectorLayer,
    QgsWkbTypes,
)
from .ToolKeys import ToolKey
from .BaseUtil import BaseUtil

logger = LogUtils(tool="Untraceable", class_name="SVGUtils")


class SVGUtils(BaseUtil):
    SVG_SIZE = 2048
    MARGIN = 48
    DEFAULT_STROKE_COLOR = "#202020"
    DEFAULT_FILL_COLOR = "#4c78a8"
    DEFAULT_POINT_RADIUS = 5.0
    DEFAULT_LINE_WIDTH = 2.0
    DEFAULT_POLYGON_STROKE_WIDTH = 1.2
    DEFAULT_LABEL_FONT_FAMILY = "Arial"
    DEFAULT_LABEL_FONT_SIZE = 14.0

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="SVGUtils")

    @staticmethod
    def collect_features_for_svg(
        layer: QgsVectorLayer,
        tool_key: str = ToolKey.UNTRACEABLE,
        target_crs: str = "EPSG:4326",
    ) -> List[dict]:
        logger = SVGUtils._get_logger(tool_key)
        prepared = []

        if not layer or not layer.isValid():
            logger.warning("collect_features_for_svg recebeu camada invalida")
            return prepared

        destination_crs = QgsCoordinateReferenceSystem(target_crs)
        transform = None

        if (
            destination_crs.isValid()
            and layer.crs().isValid()
            and layer.crs() != destination_crs
        ):
            try:
                transform = QgsCoordinateTransform(
                    layer.crs(),
                    destination_crs,
                    QgsProject.instance().transformContext(),
                )
            except Exception as e:
                logger.warning(
                    f"Falha ao preparar transformacao da camada '{layer.name()}': {e}"
                )
                transform = None

        for feature in layer.getFeatures():
            geometry = feature.geometry()
            if not geometry or geometry.isEmpty():
                continue

            geometry = QgsGeometry(geometry)
            if transform is not None:
                try:
                    geometry.transform(transform)
                except Exception as e:
                    logger.warning(
                        f"Falha ao reprojetar feicao {feature.id()} para {target_crs}: {e}"
                    )
                    continue

            prepared.append({"feature": QgsFeature(feature), "geometry": geometry})

        logger.debug(
            f"collect_features_for_svg preparou {len(prepared)} feicoes para '{layer.name()}'"
        )
        return prepared

    @staticmethod
    def build_svg_document(
        layer: QgsVectorLayer,
        features: List[dict],
        label_text: str,
        style: dict,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> str:
        logger = SVGUtils._get_logger(tool_key)

        if not features:
            raise ValueError("Nenhuma feicao foi informada para gerar o SVG.")

        min_x, min_y, max_x, max_y = SVGUtils.combined_bounds(features)
        width = max(max_x - min_x, 1e-9)
        height = max(max_y - min_y, 1e-9)
        draw_size = SVGUtils.SVG_SIZE - 2 * SVGUtils.MARGIN
        scale = min(draw_size / width, draw_size / height)
        offset_x = min_x - (draw_size - width * scale) / (2 * scale)
        offset_y = min_y - (draw_size - height * scale) / (2 * scale)

        svg = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVGUtils.SVG_SIZE}" '
                f'height="{SVGUtils.SVG_SIZE}" viewBox="0 0 {SVGUtils.SVG_SIZE} {SVGUtils.SVG_SIZE}">'
            ),
            SVGUtils.background_svg(style),
        ]

        svg.append('  <g id="features">')
        render_context = QgsRenderContext()
        for item in features:
            feature = item["feature"]
            geometry = item["geometry"]
            symbol_style = SVGUtils.symbol_style_for_feature(
                layer,
                feature,
                geometry,
                render_context,
                style=style,
                tool_key=tool_key,
            )
            elements = SVGUtils.geometry_to_svg_elements(
                geometry, offset_x, offset_y, scale, symbol_style
            )
            svg.extend(f"    {element}" for element in elements)
        svg.append("  </g>")

        if style.get("show_label", False):
            label_elements = SVGUtils.feature_label_svgs(
                layer=layer,
                features=features,
                offset_x=offset_x,
                offset_y=offset_y,
                scale=scale,
                style=style,
                tool_key=tool_key,
            )
            if label_elements:
                svg.append('  <g id="labels">')
                svg.extend(f"    {element}" for element in label_elements)
                svg.append("  </g>")

        svg.append("</svg>")
        logger.debug(
            f"build_svg_document concluiu SVG para '{layer.name()}' com {len(features)} feicoes"
        )
        return "\n".join(svg)

    @staticmethod
    def background_svg(style: dict) -> str:
        if style.get("transparent_background", False):
            return (
                f'  <rect width="{SVGUtils.SVG_SIZE}" height="{SVGUtils.SVG_SIZE}" '
                'fill="none"/>'
            )
        return (
            f'  <rect width="{SVGUtils.SVG_SIZE}" height="{SVGUtils.SVG_SIZE}" '
            f'fill="{style.get("background_color", "#ffffff")}"/>'
        )

    @staticmethod
    def combined_bounds(features: List[dict]):
        min_x = None
        min_y = None
        max_x = None
        max_y = None

        for item in features:
            bbox = item["geometry"].boundingBox()
            if min_x is None:
                min_x = bbox.xMinimum()
                min_y = bbox.yMinimum()
                max_x = bbox.xMaximum()
                max_y = bbox.yMaximum()
                continue

            min_x = min(min_x, bbox.xMinimum())
            min_y = min(min_y, bbox.yMinimum())
            max_x = max(max_x, bbox.xMaximum())
            max_y = max(max_y, bbox.yMaximum())

        return min_x, min_y, max_x, max_y

    @staticmethod
    def geometry_to_svg_elements(
        geometry: QgsGeometry,
        offset_x: float,
        offset_y: float,
        scale: float,
        symbol_style: dict,
    ) -> List[str]:
        wkb_type = QgsWkbTypes.flatType(geometry.wkbType())
        if wkb_type == QgsWkbTypes.GeometryCollection:
            elements = []
            for sub_geometry in geometry.asGeometryCollection():
                elements.extend(
                    SVGUtils.geometry_to_svg_elements(
                        sub_geometry, offset_x, offset_y, scale, symbol_style
                    )
                )
            return elements

        if wkb_type == QgsWkbTypes.GeometryType.Point:
            return [
                SVGUtils.point_svg(
                    geometry.asPoint(), offset_x, offset_y, scale, symbol_style
                )
            ]
        if wkb_type == QgsWkbTypes.GeometryType.MultiPoint:
            return [
                SVGUtils.point_svg(point, offset_x, offset_y, scale, symbol_style)
                for point in geometry.asMultiPoint()
            ]
        if wkb_type == QgsWkbTypes.LineString:
            return [
                SVGUtils.line_svg(
                    geometry.asPolyline(), offset_x, offset_y, scale, symbol_style
                )
            ]
        if wkb_type == QgsWkbTypes.MultiLineString:
            return [
                SVGUtils.line_svg(line, offset_x, offset_y, scale, symbol_style)
                for line in geometry.asMultiPolyline()
            ]
        if wkb_type == QgsWkbTypes.GeometryType.Polygon:
            return [
                SVGUtils.polygon_svg(
                    geometry.asPolygon(), offset_x, offset_y, scale, symbol_style
                )
            ]
        if wkb_type == QgsWkbTypes.GeometryType.MultiPolygon:
            return [
                SVGUtils.polygon_svg(polygon, offset_x, offset_y, scale, symbol_style)
                for polygon in geometry.asMultiPolygon()
            ]
        return []

    @staticmethod
    def polygon_svg(polygon, offset_x, offset_y, scale, symbol_style):
        path_parts = []
        for ring in polygon:
            path_parts.append(
                SVGUtils.ring_to_path(ring, offset_x, offset_y, scale, close=True)
            )
        path_data = "".join(path_parts)
        return (
            f'<path d="{path_data}" fill="{symbol_style["fill"]}" '
            'fill-rule="evenodd" '
            f'fill-opacity="{symbol_style["fill_opacity"]:.3f}" '
            f'stroke="{symbol_style["stroke"]}" '
            f'stroke-width="{symbol_style["stroke_width"]:.3f}" '
            f'stroke-opacity="{symbol_style["stroke_opacity"]:.3f}" '
            'stroke-linejoin="round"/>'
        )

    @staticmethod
    def line_svg(line, offset_x, offset_y, scale, symbol_style):
        path_data = SVGUtils.ring_to_path(line, offset_x, offset_y, scale, close=False)
        return (
            f'<path d="{path_data}" fill="none" '
            f'stroke="{symbol_style["stroke"]}" '
            f'stroke-width="{symbol_style["stroke_width"]:.3f}" '
            f'stroke-opacity="{symbol_style["stroke_opacity"]:.3f}" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )

    @staticmethod
    def point_svg(point, offset_x, offset_y, scale, symbol_style):
        pixel_x, pixel_y = SVGUtils.to_svg_xy(point, offset_x, offset_y, scale)
        return (
            f'<circle cx="{pixel_x:.3f}" cy="{pixel_y:.3f}" '
            f'r="{symbol_style["point_radius"]:.3f}" '
            f'fill="{symbol_style["fill"]}" '
            f'fill-opacity="{symbol_style["fill_opacity"]:.3f}" '
            f'stroke="{symbol_style["stroke"]}" '
            f'stroke-width="{symbol_style["stroke_width"]:.3f}" '
            f'stroke-opacity="{symbol_style["stroke_opacity"]:.3f}"/>'
        )

    @staticmethod
    def ring_to_path(ring, offset_x, offset_y, scale, close: bool) -> str:
        commands = []
        for index, point in enumerate(ring):
            svg_x, svg_y = SVGUtils.to_svg_xy(point, offset_x, offset_y, scale)
            prefix = "M" if index == 0 else "L"
            commands.append(f"{prefix}{svg_x:.3f},{svg_y:.3f}")
        if close and commands:
            commands.append("Z")
        return "".join(commands)

    @staticmethod
    def to_svg_xy(point, offset_x, offset_y, scale):
        if isinstance(point, QgsPointXY):
            x_value = point.x()
            y_value = point.y()
        else:
            x_value = point.x()
            y_value = point.y()

        pixel_x = (x_value - offset_x) * scale + SVGUtils.MARGIN
        pixel_y = SVGUtils.SVG_SIZE - SVGUtils.MARGIN - (y_value - offset_y) * scale
        return pixel_x, pixel_y

    @staticmethod
    def symbol_style_for_feature(
        layer: QgsVectorLayer,
        feature: QgsFeature,
        geometry: QgsGeometry,
        render_context: QgsRenderContext,
        style: Optional[dict] = None,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> dict:
        logger = SVGUtils._get_logger(tool_key)
        symbol = None
        renderer = layer.renderer()
        if renderer is not None:
            try:
                if hasattr(renderer, "startRender"):
                    renderer.startRender(render_context, layer.fields())
                if hasattr(renderer, "symbolForFeature"):
                    symbol = renderer.symbolForFeature(feature, render_context)
                elif hasattr(renderer, "symbol"):
                    symbol = renderer.symbol()
            except Exception as e:
                logger.warning(
                    f"Falha ao obter simbolo da feicao {feature.id()} da camada '{layer.name()}': {e}"
                )
            finally:
                try:
                    if hasattr(renderer, "stopRender"):
                        renderer.stopRender(render_context)
                except Exception as e:
                    logger.warning(f"Falha ao finalizar render context: {e}")

        if symbol is None:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())

        if symbol is None:
            return SVGUtils.default_symbol_style(geometry)

        fill_color = SVGUtils.qcolor_to_svg(getattr(symbol, "color", lambda: None)())
        opacity = float(getattr(symbol, "opacity", lambda: 1.0)() or 1.0)
        stroke_color = fill_color or SVGUtils.DEFAULT_STROKE_COLOR
        stroke_opacity = opacity
        stroke_width = SVGUtils.DEFAULT_LINE_WIDTH
        point_radius = SVGUtils.DEFAULT_POINT_RADIUS

        try:
            symbol_layer = (
                symbol.symbolLayer(0) if symbol.symbolLayerCount() > 0 else None
            )
        except Exception as e:
            logger.debug(f"symbol_style_for_feature: failed with error: {e}")
            symbol_layer = None

        if symbol_layer is not None:
            stroke_candidate = SVGUtils.extract_symbol_color(
                symbol_layer,
                ("strokeColor", "outlineColor", "borderColor", "color"),
            )
            if stroke_candidate:
                stroke_color = stroke_candidate

            stroke_width = SVGUtils.extract_symbol_number(
                symbol_layer,
                ("strokeWidth", "outlineWidth", "width", "borderWidth"),
                stroke_width,
            )
            point_radius = (
                SVGUtils.extract_symbol_number(
                    symbol_layer,
                    ("size", "radius", "width"),
                    point_radius * 2.0,
                )
                / 2.0
            )

            fill_candidate = SVGUtils.extract_symbol_color(
                symbol_layer,
                ("fillColor", "color"),
            )
            if fill_candidate:
                fill_color = fill_candidate

        if geometry.type() == QgsWkbTypes.PointGeometry:
            stroke_width = max(stroke_width, 0.5)
            point_radius = max(point_radius, 1.0)
        elif geometry.type() == QgsWkbTypes.LineGeometry:
            fill_color = "none"
            stroke_width = max(stroke_width, 0.5)
        else:
            stroke_width = max(stroke_width, 0.5)
            if fill_color in (None, "", "none"):
                fill_color = SVGUtils.DEFAULT_FILL_COLOR

        show_border = True if style is None else style.get("show_border", True)
        configured_border_color = None if style is None else style.get("border_color")
        configured_border_width = None if style is None else style.get("border_width")
        border_width = configured_border_width
        if border_width is None or float(border_width) < 0:
            border_width = SVGUtils.default_border_width_for_geometry(geometry)
        else:
            border_width = float(border_width)

        return {
            "fill": fill_color or SVGUtils.DEFAULT_FILL_COLOR,
            "fill_opacity": opacity if fill_color != "none" else 0.0,
            "stroke": (
                (
                    configured_border_color
                    or stroke_color
                    or SVGUtils.DEFAULT_STROKE_COLOR
                )
                if show_border
                else "none"
            ),
            "stroke_width": border_width if show_border else 0.0,
            "stroke_opacity": stroke_opacity if show_border else 0.0,
            "point_radius": point_radius,
        }

    @staticmethod
    def feature_label_svgs(
        layer: QgsVectorLayer,
        features: List[dict],
        offset_x: float,
        offset_y: float,
        scale: float,
        style: dict,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> List[str]:
        logger = SVGUtils._get_logger(tool_key)
        label_settings = SVGUtils.resolve_label_settings(layer, tool_key=tool_key)
        if not label_settings:
            return []

        elements = []
        for item in features:
            feature = item["feature"]
            geometry = item["geometry"]
            label_text = SVGUtils.evaluate_label_expression(
                layer, feature, label_settings, tool_key=tool_key
            )
            if not label_text:
                continue

            anchor_point = SVGUtils.label_anchor_point(geometry)
            if anchor_point is None:
                continue

            pixel_x, pixel_y = SVGUtils.to_svg_xy(
                anchor_point, offset_x, offset_y, scale
            )
            escaped = escape(str(label_text))
            elements.append(
                f'<text x="{pixel_x:.3f}" y="{pixel_y:.3f}" '
                f'font-family="{SVGUtils.label_font_family(label_settings)}" '
                f'font-size="{SVGUtils.label_font_size(label_settings, style):.3f}" '
                f'fill="{style.get("label_color", "#000000")}" '
                'text-anchor="middle" dominant-baseline="middle">'
                f"{escaped}</text>"
            )

        logger.debug(
            f"feature_label_svgs gerou {len(elements)} rotulo(s) para '{layer.name()}'"
        )
        return elements

    @staticmethod
    def resolve_label_settings(
        layer: QgsVectorLayer, tool_key: str = ToolKey.UNTRACEABLE
    ):
        logger = SVGUtils._get_logger(tool_key)
        if not layer or not layer.isValid():
            return None

        try:
            labels_enabled = layer.labelsEnabled()
        except Exception as e:
            logger.warning(f"Falha ao verificar labelsEnabled da camada: {e}")
            labels_enabled = False

        labeling = layer.labeling() if hasattr(layer, "labeling") else None
        if labeling is not None and labels_enabled:
            try:
                provider_ids = (
                    labeling.subProviders() if hasattr(labeling, "subProviders") else []
                )
            except Exception as e:
                logger.debug(
                    f"_read_label_settings_from_labeling: failed with error: {e}"
                )
                provider_ids = []

            provider_id = provider_ids[0] if provider_ids else ""

            settings = SVGUtils._read_label_settings_from_labeling(
                layer, labeling, provider_id, logger
            )
            if settings is not None and getattr(settings, "fieldName", ""):
                return settings

        fallback = SVGUtils._read_label_settings_from_custom_properties(layer, logger)
        if fallback is not None:
            return fallback

        logger.debug("Nao foi possivel resolver configuracao de rotulo da camada")
        return None

    @staticmethod
    def _read_label_settings_from_labeling(layer, labeling, provider_id, logger):
        try:
            return labeling.settings(provider_id)
        except TypeError:
            try:
                return labeling.settings(layer, provider_id)
            except Exception as e:
                logger.warning(
                    f"Falha ao obter settings(layer, provider_id) do labeling: {e}"
                )
                return None
        except Exception as e:
            logger.warning(f"Falha ao obter settings(provider_id) do labeling: {e}")
            return None

    @staticmethod
    def _read_label_settings_from_custom_properties(layer, logger):
        field_name = str(layer.customProperty("labeling/fieldName", "") or "").strip()
        if not field_name:
            try:
                display_expression = str(layer.displayExpression() or "").strip()
            except Exception as e:
                logger.debug(
                    f"_read_label_settings_from_custom_properties: failed with error: {e}"
                )
                display_expression = ""

            if display_expression:
                logger.debug(
                    f"Usando fallback displayExpression para rotulo: {display_expression}"
                )
                return {
                    "fieldName": display_expression,
                    "isExpression": True,
                    "fontFamily": SVGUtils.DEFAULT_LABEL_FONT_FAMILY,
                    "fontSize": SVGUtils.DEFAULT_LABEL_FONT_SIZE,
                }

            name_index = layer.fields().lookupField("Name")
            if name_index != -1:
                logger.debug("Usando fallback do campo 'Name' para rotulo")
                return {
                    "fieldName": "Name",
                    "isExpression": False,
                    "fontFamily": SVGUtils.DEFAULT_LABEL_FONT_FAMILY,
                    "fontSize": SVGUtils.DEFAULT_LABEL_FONT_SIZE,
                }

            logger.debug(
                "Nenhum fallback de rotulo encontrado em customProperty/displayExpression/Name"
            )
            return None

        is_expression = str(
            layer.customProperty("labeling/isExpression", "false") or "false"
        ).lower() in ("1", "true", "yes")
        family = (
            str(
                layer.customProperty(
                    "labeling/fontFamily", SVGUtils.DEFAULT_LABEL_FONT_FAMILY
                )
                or SVGUtils.DEFAULT_LABEL_FONT_FAMILY
            ).strip()
            or SVGUtils.DEFAULT_LABEL_FONT_FAMILY
        )

        try:
            size = float(
                layer.customProperty(
                    "labeling/fontSize", SVGUtils.DEFAULT_LABEL_FONT_SIZE
                )
                or SVGUtils.DEFAULT_LABEL_FONT_SIZE
            )
        except Exception as e:
            logger.debug(
                f"_read_label_settings_from_custom_properties: failed with error: {e}"
            )
            size = SVGUtils.DEFAULT_LABEL_FONT_SIZE

        logger.debug(
            f"Usando fallback de customProperty para rotulo. fieldName={field_name}, is_expression={is_expression}"
        )
        return {
            "fieldName": field_name,
            "isExpression": is_expression,
            "fontFamily": family,
            "fontSize": size,
        }

    @staticmethod
    def evaluate_label_expression(
        layer: QgsVectorLayer,
        feature: QgsFeature,
        label_settings,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Optional[str]:
        logger = SVGUtils._get_logger(tool_key)
        if label_settings is None:
            return None

        try:
            expression_text = (
                SVGUtils._label_setting_value(label_settings, "fieldName", "") or ""
            )
            is_expression = bool(
                SVGUtils._label_setting_value(label_settings, "isExpression", False)
            )
            if not expression_text:
                return None

            if not is_expression:
                escaped_field = expression_text.replace('"', '""')
                expression_text = f'"{escaped_field}"'

            expression = QgsExpression(expression_text)
            context = QgsExpressionContext()
            context.appendScopes(
                QgsExpressionContextUtils.globalProjectLayerScopes(layer)
            )
            context.setFeature(feature)
            value = expression.evaluate(context)

            if expression.hasEvalError():
                logger.warning(
                    f"Erro ao avaliar rotulo da feicao {feature.id()}: {expression.evalErrorString()}"
                )
                return None

            if value is None:
                logger.debug(
                    f"Rotulo vazio para feicao {feature.id()} apos avaliar expressao: {expression_text}"
                )
                return None

            text = str(value).strip()
            if not text:
                logger.debug(
                    f"Rotulo em branco para feicao {feature.id()} apos avaliar expressao: {expression_text}"
                )
            return text or None
        except Exception as e:
            logger.warning(
                f"Falha ao avaliar configuracao de rotulo da feicao {feature.id()}: {e}"
            )
            return None

    @staticmethod
    def label_anchor_point(geometry: QgsGeometry, logger: LogUtils = None):
        if not geometry or geometry.isEmpty():
            return None

        try:
            geom_type = geometry.type()
            if geom_type == QgsWkbTypes.PointGeometry:
                if geometry.isMultipart():
                    multi_points = geometry.asMultiPoint()
                    return multi_points[0] if multi_points else None
                return geometry.asPoint()

            point_on_surface = geometry.pointOnSurface()
            if point_on_surface and not point_on_surface.isEmpty():
                return point_on_surface.asPoint()

            centroid = geometry.centroid()
            if centroid and not centroid.isEmpty():
                return centroid.asPoint()
        except Exception as e:
            from ..core.config.LogUtils import LogUtils

            logger = LogUtils(tool="Untraceable", class_name="None")
            logger.debug(f"label_anchor_point: failed with error: {e}")
            return None

        return None

    @staticmethod
    def label_font_family(label_settings) -> str:
        family = SVGUtils._label_setting_value(
            label_settings, "fontFamily", SVGUtils.DEFAULT_LABEL_FONT_FAMILY
        )
        if family:
            return str(family)

        try:
            text_format = label_settings.format()
            family = text_format.font().family()
            return family or SVGUtils.DEFAULT_LABEL_FONT_FAMILY
        except Exception as e:
            from ..core.config.LogUtils import LogUtils

            logger = LogUtils(tool="Untraceable", class_name="None")
            logger.debug(f"label_font_family: failed with error: {e}")
            return SVGUtils.DEFAULT_LABEL_FONT_FAMILY

    @staticmethod
    def label_font_size(label_settings, style: Optional[dict] = None) -> float:
        from ..core.config.LogUtils import LogUtils

        logger = LogUtils(tool="Untraceable", class_name="None")
        if style is not None:
            configured_size = style.get("label_size")
            try:
                configured_size = float(configured_size)
                if configured_size > 0:
                    return configured_size
            except Exception as e:

                logger.debug(f"label_font_size: failed with error: {e}")
                pass

        size = SVGUtils._label_setting_value(
            label_settings, "fontSize", SVGUtils.DEFAULT_LABEL_FONT_SIZE
        )
        try:
            size = float(size)
            if size > 0:
                return size
        except Exception as e:
            logger.debug(f"label_font_size: failed with error: {e}")
            pass

        try:
            text_format = label_settings.format()
            font = text_format.font()
            point_size = float(font.pointSizeF())
            if point_size > 0:
                return point_size
        except Exception as e:
            logger.debug(f"label_font_size: failed with error: {e}")
        return SVGUtils.DEFAULT_LABEL_FONT_SIZE

    @staticmethod
    def _label_setting_value(label_settings, key, default=None):
        if isinstance(label_settings, dict):
            return label_settings.get(key, default)
        return getattr(label_settings, key, default)

    @staticmethod
    def default_border_width_for_geometry(geometry: QgsGeometry) -> float:
        if geometry is None:
            return SVGUtils.DEFAULT_POLYGON_STROKE_WIDTH

        if geometry.type() == QgsWkbTypes.PointGeometry:
            return 1.0
        if geometry.type() == QgsWkbTypes.LineGeometry:
            return 2.0
        return SVGUtils.DEFAULT_POLYGON_STROKE_WIDTH

    @staticmethod
    def default_symbol_style(geometry: QgsGeometry) -> dict:
        if geometry.type() == QgsWkbTypes.PointGeometry:
            return {
                "fill": SVGUtils.DEFAULT_FILL_COLOR,
                "fill_opacity": 1.0,
                "stroke": SVGUtils.DEFAULT_STROKE_COLOR,
                "stroke_width": 1.0,
                "stroke_opacity": 1.0,
                "point_radius": SVGUtils.DEFAULT_POINT_RADIUS,
            }
        if geometry.type() == QgsWkbTypes.LineGeometry:
            return {
                "fill": "none",
                "fill_opacity": 0.0,
                "stroke": SVGUtils.DEFAULT_STROKE_COLOR,
                "stroke_width": SVGUtils.DEFAULT_LINE_WIDTH,
                "stroke_opacity": 1.0,
                "point_radius": SVGUtils.DEFAULT_POINT_RADIUS,
            }
        return {
            "fill": SVGUtils.DEFAULT_FILL_COLOR,
            "fill_opacity": 0.8,
            "stroke": SVGUtils.DEFAULT_STROKE_COLOR,
            "stroke_width": SVGUtils.DEFAULT_POLYGON_STROKE_WIDTH,
            "stroke_opacity": 1.0,
            "point_radius": SVGUtils.DEFAULT_POINT_RADIUS,
        }

    @staticmethod
    def extract_symbol_color(symbol_layer, method_names) -> Optional[str]:
        from ..core.config.LogUtils import LogUtils

        logger = LogUtils(tool="Untraceable", class_name="None")
        for method_name in method_names:
            method = getattr(symbol_layer, method_name, None)
            if callable(method):
                try:
                    return SVGUtils.qcolor_to_svg(method())
                except Exception as e:
                    logger.debug(f"extract_symbol_color: failed with error: {e}")
                    continue
        return None

    @staticmethod
    def extract_symbol_number(symbol_layer, method_names, fallback: float) -> float:
        for method_name in method_names:
            method = getattr(symbol_layer, method_name, None)
            if callable(method):
                try:
                    value = float(method())
                    if value > 0:
                        return value
                except Exception as e:
                    logger.debug(f"extract_symbol_number: failed with error: {e}")
                    continue
        return fallback

    @staticmethod
    def qcolor_to_svg(value) -> Optional[str]:
        if isinstance(value, QColor) and value.isValid():
            return value.name(QColor.NameFormat.HexRgb)
        return None

    @staticmethod
    def sanitize_filename(value: str) -> str:
        sanitized = re.sub(r'[<>:"/\\|?*]+', "_", str(value or "").strip())
        sanitized = re.sub(r"\s+", "_", sanitized)
        sanitized = re.sub(r"_+", "_", sanitized).strip("._")
        return sanitized or "svg"

    @staticmethod
    def unique_svg_path(output_folder: str, base_name: str) -> str:
        candidate = os.path.join(output_folder, f"{base_name}.svg")
        counter = 1
        while os.path.exists(candidate):
            candidate = os.path.join(output_folder, f"{base_name}_{counter}.svg")
            counter += 1
        return candidate

    @staticmethod
    def write_svg(
        output_path: str, svg_content: str, tool_key: str = ToolKey.UNTRACEABLE
    ):
        logger = SVGUtils._get_logger(tool_key)
        with open(output_path, "w", encoding="utf-8") as stream:
            stream.write(svg_content)
        logger.debug(f"SVG gravado em disco: {output_path}")
