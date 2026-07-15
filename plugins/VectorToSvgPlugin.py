# -*- coding: utf-8 -*-
import os

from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsMapLayerProxyModel,
)

from .BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR
from ..utils.Preferences import Preferences
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.SVGUtils import SVGUtils
from ..utils.ToolKeys import ToolKey
from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
from ..utils.vector.VectorLayerGeometry import VectorLayerGeometry


class VectorToSvgPlugin(BasePluginMTL):
    TOOL_KEY = ToolKey.VECTOR_TO_SVG

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(
            tool_key=self.TOOL_KEY,
            class_name=self.__class__.__name__,
            load_system_prefs=False,
            build_ui=True,
        )

    def _build_ui(self, **kwargs):
        super()._build_ui(
            title=STR.VECTOR_TO_SVG_TITLE,
            icon_path="cadmus_icon.ico",
            enable_scroll=True,
        )

        layer_layout, self.layer_input = WidgetFactory.create_layer_input(
            STR.VECTOR_LAYER_LABEL,
            QgsMapLayerProxyModel.Filter.VectorLayer,
            allow_empty=False,
            enable_selected_checkbox=True,
            parent=self,
            separator_top=False,
            separator_bottom=True,
        )

        fill_layout, self.fill_color_widget = WidgetFactory.create_color_button(
            title=STR.BACKGROUND_COLOR,
            initial_color=QColor("#ffffff"),
            tooltip=STR.SELECT_FILL_COLOR,
            parent=self,
            separator_top=False,
            separator_bottom=False,
        )

        border_layout, self.border_color_widget = WidgetFactory.create_color_button(
            title=STR.BORDER_COLOR,
            initial_color=QColor("#000000"),
            tooltip=STR.SELECT_BORDER_COLOR,
            parent=self,
            separator_top=False,
            separator_bottom=False,
        )

        border_width_layout, self.border_width_spin = (
            WidgetFactory.create_double_spin_input(
                STR.BORDER_WIDTH,
                decimals=2,
                step=0.2,
                minimum=0.0,
                maximum=50.0,
                value=1.2,
                separator_top=False,
                separator_bottom=False,
            )
        )

        label_layout, self.label_color_widget = WidgetFactory.create_color_button(
            title=STR.LABEL_COLOR,
            initial_color=QColor("#000000"),
            tooltip=STR.SELECT_LABEL_COLOR,
            parent=self,
            separator_top=False,
            separator_bottom=True,
        )

        label_size_layout, self.label_size_spin = (
            WidgetFactory.create_double_spin_input(
                STR.LABEL_SIZE,
                decimals=1,
                step=1.0,
                minimum=1.0,
                maximum=200.0,
                value=14.0,
                separator_top=False,
                separator_bottom=True,
            )
        )

        options = {
            "transparent_background": STR.TRANSPARENT_BACKGROUND,
            "show_border": STR.SHOW_BORDER,
            "show_label": STR.SHOW_LABEL,
            "for_each_feature": STR.GENERATE_SVG_FOR_EACH_FEATURE,
        }
        options_layout, self.options_map = WidgetFactory.create_checkbox_grid(
            options,
            items_per_row=1,
            checked_by_default=False,
            title=None,
            separator_top=False,
            separator_bottom=True,
        )

        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
            )
        )
        folder_layout, self.folder_selector = WidgetFactory.create_path_selector(
            parent=self,
            title=STR.OUTPUT_FOLDER,
            mode="folder",
            path_button="svgs",
            separator_top=False,
            separator_bottom=False,
        )
        self.logger.debug("Path selector de pasta de saida criado")

        self.layout.add_items(
            [
                layer_layout,
                fill_layout,
                border_layout,
                label_layout,
                border_width_layout,
                label_size_layout,
                options_layout,
                folder_layout,
                buttons_layout,
            ]
        )

    def _load_prefs(self):
        self.logger.debug("Carregando preferencias do VectorToSvg")

        self.fill_color_widget.set_color(
            QColor(self.preferences.get("fill_color", "#ffffff"))
        )
        self.border_color_widget.set_color(
            QColor(self.preferences.get("border_color", "#000000"))
        )
        self.label_color_widget.set_color(
            QColor(self.preferences.get("label_color", "#000000"))
        )
        self.label_size_spin.setValue(float(self.preferences.get("label_size", 14.0)))
        self.border_width_spin.setValue(
            float(self.preferences.get("border_width", 1.2))
        )

        self.options_map["transparent_background"].setChecked(
            self.preferences.get("transparent_background", False)
        )
        self.options_map["show_border"].setChecked(
            self.preferences.get("show_border", False)
        )
        self.options_map["show_label"].setChecked(
            self.preferences.get("show_label", False)
        )
        self.options_map["for_each_feature"].setChecked(
            self.preferences.get("for_each_feature", False)
        )

        project_folder = ProjectUtils.get_project_dir(
            ProjectUtils.get_project_instance()
        )
        default_folder = os.path.join(project_folder, "svgs")
        output_folder = self.preferences.get("output_folder", default_folder)
        self.folder_selector.set_paths([output_folder])

    def _save_prefs(self):
        self.logger.debug("Salvando preferencias do VectorToSvg")

        self.preferences["fill_color"] = self.fill_color_widget.get_color().name(
            QColor.NameFormat.HexArgb
        )
        self.preferences["border_color"] = self.border_color_widget.get_color().name(
            QColor.NameFormat.HexArgb
        )
        self.preferences["label_color"] = self.label_color_widget.get_color().name(
            QColor.NameFormat.HexArgb
        )
        self.preferences["label_size"] = float(self.label_size_spin.value())
        self.preferences["border_width"] = float(self.border_width_spin.value())
        self.preferences["transparent_background"] = self.options_map[
            "transparent_background"
        ].isChecked()
        self.preferences["show_border"] = self.options_map["show_border"].isChecked()
        self.preferences["show_label"] = self.options_map["show_label"].isChecked()
        self.preferences["for_each_feature"] = self.options_map[
            "for_each_feature"
        ].isChecked()

        paths = self.folder_selector.get_paths()
        project_folder = ProjectUtils.get_project_dir(
            ProjectUtils.get_project_instance()
        )
        self.preferences["output_folder"] = (
            paths[0] if paths else os.path.join(project_folder, "svgs")
        )

        self.preferences["window_width"] = self.width()
        self.preferences["window_height"] = self.height()

        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)

    def execute_tool(self):
        self.logger.info("Iniciando exportacao de SVG a partir de camada vetorial")
        layer = ProjectUtils.get_active_vector_layer(
            self.layer_input.current_layer(), self.logger
        )
        self.start_stats(layer)

        if not layer:
            QgisMessageUtil.bar_critical(self.iface, STR.SELECT_VECTOR_LAYER)
            return

        if not VectorLayerAttributes.ensure_has_features(layer, self.logger):
            QgisMessageUtil.bar_warning(self.iface, STR.LAYER_HAS_NO_FEATURES)
            return

        output_folder = self._resolve_output_folder()
        if not output_folder:
            return

        only_selected = self.layer_input.only_selected_enabled()
        export_layer = self._resolve_export_layer(layer, only_selected)
        if not export_layer:
            return

        features = SVGUtils.collect_features_for_svg(
            export_layer, tool_key=self.TOOL_KEY
        )
        if not features:
            QgisMessageUtil.bar_warning(self.iface, STR.LAYER_HAS_NO_FEATURES)
            return

        style = self._build_style()
        for_each_feature = self.options_map["for_each_feature"].isChecked()

        try:
            if for_each_feature:
                generated = self._export_one_svg_per_feature(
                    layer, features, output_folder, style
                )
            else:
                generated = [
                    self._export_single_svg(layer, features, output_folder, style)
                ]
        except Exception as e:
            self.logger.error(f"Erro ao gerar SVG: {e}")
            QgisMessageUtil.modal_error(self.iface, f"{STR.ERROR}\n{e}")
            return

        if not generated:
            QgisMessageUtil.bar_warning(self.iface, STR.ERROR)
            return

        self.finish_stats(input_obj=export_layer)
        message = f"{len(generated)} {STR.SVGS_GENERATED_SUCCESS}"
        self.logger.info(message)
        QgisMessageUtil.modal_result_with_folder(
            self.iface,
            STR.EXPORT,
            message,
            output_folder,
            parent=self,
        )

    def _resolve_output_folder(self):
        paths = self.folder_selector.get_paths()
        output_folder = paths[0].strip() if paths else ""

        if not output_folder:
            QgisMessageUtil.bar_warning(self.iface, STR.OUTPUT_FOLDER)
            return None

        try:
            os.makedirs(output_folder, exist_ok=True)
            self.logger.debug(f"Pasta de saida garantida: {output_folder}")
            return output_folder
        except Exception as e:
            self.logger.error(f"Erro ao preparar pasta de saida '{output_folder}': {e}")
            QgisMessageUtil.modal_error(self.iface, f"{STR.ERROR}\n{e}")
            return None

    def _resolve_export_layer(self, layer, only_selected):
        if not only_selected:
            self.logger.debug(
                f"Exportando todas as feicoes da camada '{layer.name()}'."
            )
            return layer

        self.logger.debug(
            f"Opcao somente feicoes selecionadas ativa. Total selecionadas: {layer.selectedFeatureCount()}"
        )
        selected_layer, error = VectorLayerGeometry.get_selected_features(
            layer, tool_key=self.TOOL_KEY
        )
        if error:
            self.logger.warning(f"Falha ao obter feicoes selecionadas: {error}")
            QgisMessageUtil.modal_error(self.iface, error)
            return None

        return selected_layer

    def _build_style(self):
        return {
            "background_color": self.fill_color_widget.get_color().name(QColor.NameFormat.HexRgb),
            "border_color": self.border_color_widget.get_color().name(QColor.NameFormat.HexRgb),
            "label_color": self.label_color_widget.get_color().name(QColor.NameFormat.HexRgb),
            "label_size": float(self.label_size_spin.value()),
            "border_width": float(self.border_width_spin.value()),
            "transparent_background": self.options_map[
                "transparent_background"
            ].isChecked(),
            "show_border": self.options_map["show_border"].isChecked(),
            "show_label": self.options_map["show_label"].isChecked(),
        }

    def _export_single_svg(self, layer, features, output_folder, style):
        base_name = SVGUtils.sanitize_filename(layer.name())
        output_path = SVGUtils.unique_svg_path(output_folder, base_name)
        label_text = layer.name()
        svg_content = SVGUtils.build_svg_document(
            layer, features, label_text, style, tool_key=self.TOOL_KEY
        )
        SVGUtils.write_svg(output_path, svg_content, tool_key=self.TOOL_KEY)
        self.logger.info(f"SVG unico gerado: {output_path}")
        return output_path

    def _export_one_svg_per_feature(self, layer, features, output_folder, style):
        generated = []
        for index, item in enumerate(features, start=1):
            feature = item["feature"]
            base_name = self._feature_output_base_name(layer, feature, index)
            output_path = SVGUtils.unique_svg_path(output_folder, base_name)
            label_text = self._feature_label(layer, feature, index)
            svg_content = SVGUtils.build_svg_document(
                layer, [item], label_text, style, tool_key=self.TOOL_KEY
            )
            SVGUtils.write_svg(output_path, svg_content, tool_key=self.TOOL_KEY)
            generated.append(output_path)
            self.logger.debug(f"SVG por feicao gerado: {output_path}")
        return generated

    def _feature_output_base_name(self, layer, feature, index):
        field_index = feature.fields().lookupField("Name")
        if field_index != -1:
            value = feature.attribute(field_index)
            if value is not None and str(value).strip():
                return SVGUtils.sanitize_filename(str(value).strip())

        return SVGUtils.sanitize_filename(f"{layer.name()}_{index}")

    def _feature_label(self, layer, feature, index):
        field_index = feature.fields().lookupField("Name")
        if field_index != -1:
            value = feature.attribute(field_index)
            if value is not None and str(value).strip():
                return str(value).strip()
        return f"{layer.name()}_{index}"


def run(iface):
    dlg = VectorToSvgPlugin(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
