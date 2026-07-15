# -*- coding: utf-8 -*-
import os
from ..plugins.BasePlugin import BasePluginMTL
from ..core.services.DronePipelineService import DronePipelineService
from ..utils.StringManager import StringManager
from ..utils.Preferences import save_tool_prefs
from ..utils.ToolKeys import ToolKey
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR
from ..utils.DependenciesManager import DependenciesManager
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.adapter.StringAdapter import StringAdapter
from ..utils.mrk.MetadataFields import MetadataFields


class DroneCordinates(BasePluginMTL):

    TOOL_KEY = ToolKey.DRONE_COORDINATES

    # Nível mínimo de licença exigido para funcionalidades premium (relatório, logo, título)
    REGISTRY_LEVEL: int = 3

    CHECKBOX_OPTIONS = {
        "recursive": STR.RECURSIVE_SEARCH,
        "use_mrk": STR.USE_MRK_DATA,
        "photos": STR.PHOTOS_METADATA,
        "generate_report": STR.GENERATE_REPORT,
    }

    PREF_INITIAL_FIELDS = "initial_fields_selected"
    PREF_EXIF_FIELDS = "exif_fields_selected"
    PREF_XMP_FIELDS = "xmp_fields_selected"
    PREF_CUSTOM_FIELDS = "custom_fields_selected"
    PREF_MRK_FIELDS = "mrk_fields_selected"
    AUTO_SAVE_PREFS_ON_CLOSE = True

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface

        # Inicializa a UI e preferências via BasePluginMTL
        self.init(
            self.TOOL_KEY,
            "Drone Coordinates",
            load_system_prefs=False,
            build_ui=True,
        )

    def _build_ui(self, **kwargs):
        super()._build_ui(
            title=STR.DRONE_COORDINATES_TITLE,
            icon_path="coord.ico",
            enable_scroll=True,
        )

        # Verifica licença — controla exibição de itens do relatório
        try:
            from ..core.config.RegistryManager import RegistryManager
            lic_mgr = RegistryManager(tool_key=self.TOOL_KEY)
            is_lic_valid = lic_mgr.has_minimum_level(self.REGISTRY_LEVEL)
        except Exception as e:
            self.logger.error(
                f"Erro ao verificar licença: {e}", code="CHECK_ERROR"
            )
            is_lic_valid = False

        # ====== PASTA MRK ======
        folder_layout, self.folder_selector = WidgetFactory.create_path_selector(
            parent=self,
            title=STR.MRK_FOLDER,
            mode="folder",
            separator_bottom=True,
        )

        # ====== OPÇÕES (CollapsibleParametersWidget) ======
        opts_layout, self.opts_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title=STR.OPTIONS,
                expanded_by_default=False,
            )
        )

        # ====== LOGO / IMAGE SELECTOR (só se licença válida) ======
        if is_lic_valid:
            logo_layout, self.logo_selector = WidgetFactory.create_save_file_selector(
                parent=self,
                file_filter=StringManager.FILTER_IMAGES,
                checkbox_text=STR.USE_LOGO,
                label_text=STR.LOGO_LABEL,
                separator_top=False,
                separator_bottom=False,
                mode="file",
            )
            self.opts_collapsible.add_content_layout(logo_layout)

        # ====== PROJETO TITLE (só se licença válida) ======
        if is_lic_valid:
            title_fields = {
                "project_title": {
                    "title": STR.PROJECT_TITLE,
                    "description": STR.PROJECT_TITLE_HINT,
                    "type": "text",
                    "default": "",
                }
            }
            title_layout, self.title_input = WidgetFactory.create_input_fields_widget(
                fields_dict=title_fields,
                parent=self,
                separator_top=False,
                separator_bottom=False,
            )
            self.opts_collapsible.add_content_layout(title_layout)

        # ====== OPÇÕES (CollapsibleParametersWidget) ======

        # Monta checkboxes — remove generate_report se licença inválida
        checkbox_options = dict(self.CHECKBOX_OPTIONS)
        if not is_lic_valid:
            checkbox_options.pop("generate_report", None)

        opts_checkbox_layout, self.checkbox_map = WidgetFactory.create_checkbox_grid(
            options_data=checkbox_options,
            items_per_row=1,
            checked_by_default=False,
            separator_bottom=False,
        )
        self.opts_collapsible.add_content_layout(opts_checkbox_layout)

        # Connect checkbox toggles for dependency checks
        self.chk_photos = self.checkbox_map.get("photos")
        if self.chk_photos:
            self.chk_photos.toggled.connect(self.on_photos_changed)

        # Connect use_mrk toggle to enable/disable MRK sections
        self.chk_use_mrk = self.checkbox_map.get("use_mrk")
        if self.chk_use_mrk:
            self.chk_use_mrk.toggled.connect(self._on_use_mrk_changed)

        # ====== METADATA EXIF FIELDS ======
        exif_layout, self.exif_fields_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title="EXIF Fields",
                expanded_by_default=False,
            )
        )
        exif_items = StringAdapter.to_key_label_description(
            MetadataFields.EXIF_FIELDS)
        exif_grid_layout, self.exif_fields_grid = WidgetFactory.create_checkbox_grid(
            options_data=exif_items,
            items_per_row=2,
            checked_by_default=True,
            return_widget=True,
            separator_bottom=False,
            show_control_buttons=True,
        )
        self.exif_fields_collapsible.add_content_layout(exif_grid_layout)

        # ====== METADATA DJI FIELDS (XMP) ======
        xmp_layout, self.xmp_fields_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title="DJI Fields",
                expanded_by_default=False,
            )
        )
        xmp_items = StringAdapter.to_key_label_description(
            MetadataFields.DJI_XMP_FIELDS
        )
        xmp_grid_layout, self.xmp_fields_grid = WidgetFactory.create_checkbox_grid(
            options_data=xmp_items,
            items_per_row=2,
            checked_by_default=True,
            return_widget=True,
            separator_bottom=False,
            show_control_buttons=True,
        )
        self.xmp_fields_collapsible.add_content_layout(xmp_grid_layout)

        # ====== METADATA CUSTOM FIELDS ======
        custom_layout, self.custom_fields_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title="Custom Fields",
                expanded_by_default=False,
            )
        )
        custom_items = StringAdapter.to_key_label_description(
            MetadataFields.CUSTOM_FIELDS
        )
        custom_grid_layout, self.custom_fields_grid = (
            WidgetFactory.create_checkbox_grid(
                options_data=custom_items,
                items_per_row=2,
                checked_by_default=False,
                return_widget=True,
                separator_bottom=False,
                show_control_buttons=True,
            )
        )
        self.custom_fields_collapsible.add_content_layout(custom_grid_layout)

        # ====== METADATA INITIAL FIELDS ======
        initial_layout, self.initial_fields_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title="Initial Fields",
                expanded_by_default=False,
            )
        )
        initial_items = StringAdapter.to_key_label_description(
            MetadataFields.INITIAL_FIELDS
        )
        initial_grid_layout, self.initial_fields_grid = (
            WidgetFactory.create_checkbox_grid(
                options_data=initial_items,
                items_per_row=2,
                checked_by_default=True,
                return_widget=True,
                separator_bottom=False,
                show_control_buttons=True,
            )
        )
        self.initial_fields_collapsible.add_content_layout(initial_grid_layout)

        # ====== METADATA MRK FIELDS ======
        mrk_layout, self.mrk_fields_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title="MRK Fields",
                expanded_by_default=False,
            )
        )
        mrk_items = StringAdapter.to_key_label_description(
            MetadataFields.MRK_FIELDS)
        mrk_grid_layout, self.mrk_fields_grid = WidgetFactory.create_checkbox_grid(
            options_data=mrk_items,
            items_per_row=2,
            checked_by_default=True,
            return_widget=True,
            separator_bottom=False,
            show_control_buttons=True,
        )
        self.mrk_fields_collapsible.add_content_layout(mrk_grid_layout)

        # ====== SALVAMENTO (CollapsibleParametersWidget) ======
        save_layout, self.save_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title=STR.SAVING,
                expanded_by_default=False,
            )
        )

        save_points_layout, self.save_points_selector = (
            WidgetFactory.create_save_file_selector(
                parent=self,
                file_filter=StringManager.FILTER_VECTOR,
                checkbox_text=STR.SAVE_POINTS_CHECKBOX,
                label_text=STR.SAVE_IN,
                separator_top=False,
                separator_bottom=False,
            )
        )

        save_track_layout, self.save_track_selector = (
            WidgetFactory.create_save_file_selector(
                parent=self,
                file_filter=StringManager.FILTER_VECTOR,
                checkbox_text=STR.SAVE_TRACK_CHECKBOX,
                label_text=STR.SAVE_IN,
                separator_top=False,
                separator_bottom=False,
            )
        )

        self.save_collapsible.add_content_layout(save_points_layout)
        self.save_collapsible.add_content_layout(save_track_layout)

        # ====== ESTILOS (QML) - CollapsibleParametersWidget ======
        styles_layout, self.styles_collapsible = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title=STR.STYLES,
                expanded_by_default=False,
            )
        )

        qml_points_layout, self.qml_points_selector = WidgetFactory.create_qml_selector(
            parent=self,
            checkbox_text=STR.APPLY_STYLE_POINTS,
            label_text=STR.QML_POINTS,
            separator_top=False,
            separator_bottom=False,
        )

        qml_track_layout, self.qml_track_selector = WidgetFactory.create_qml_selector(
            parent=self,
            checkbox_text=STR.APPLY_STYLE_TRACK,
            label_text=STR.QML_TRACK,
            separator_top=False,
            separator_bottom=False,
        )

        self.styles_collapsible.add_content_layout(qml_points_layout)
        self.styles_collapsible.add_content_layout(qml_track_layout)

        # ====== BOTOES ======
        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
            )
        )

        # ====== CONTEÚO AO LAYOUT ======
        self.layout.add_items(
            [
                folder_layout,
                opts_layout,
                exif_layout,
                xmp_layout,
                custom_layout,
                initial_layout,
                mrk_layout,
                save_layout,
                styles_layout,
                buttons_layout,
            ]
        )

    def _on_use_mrk_changed(self, checked: bool):
        """Habilita/desabilita seção MRK conforme checkbox 'Obter dados MRK'."""
        # Se MRK estiver desabilitado, esconde/cinza a seção de campos MRK
        self.mrk_fields_collapsible.setVisible(checked)
        self.mrk_fields_collapsible.setEnabled(checked)
        if not checked:
            # Se não usa MRK, também limpa a seleção de campos MRK
            self.mrk_fields_grid.set_checked_keys([])

    def _ensure_photos_dependency(self, checked: bool):
        if not checked:
            return
        if DependenciesManager.check_dependency("Pillow", self.TOOL_KEY):
            return
        confirmed = QgisMessageUtil.confirm(
            self.iface,
            STR.PHOTOS_METADATA_REQUIRED_MESSAGE,
            STR.REQUIRED_LIBRARY,
        )
        if not confirmed:
            self.chk_photos.setChecked(False)
            return
        started = DependenciesManager.install_dependency_gui(
            "Pillow", self.iface, self.TOOL_KEY
        )
        if not started:
            QgisMessageUtil.modal_error(
                self.iface,
                STR.INSTALL_DEPENDENCY_FAILED.format("Pillow"),
            )
            self.chk_photos.setChecked(False)

    def on_photos_changed(self, checked: bool):
        self._ensure_photos_dependency(checked)

    def _get_selected_exif_fields(self):
        return MetadataFields.normalize_selected_keys(
            self.exif_fields_grid.get_checked_keys(),
            allowed_keys=MetadataFields.exif_keys(),
        )

    def _get_selected_xmp_fields(self):
        return MetadataFields.normalize_selected_keys(
            self.xmp_fields_grid.get_checked_keys(),
            allowed_keys=MetadataFields.xmp_keys(),
        )

    def _get_selected_custom_fields(self):
        return MetadataFields.normalize_selected_keys(
            self.custom_fields_grid.get_checked_keys(),
            allowed_keys=MetadataFields.custom_keys(),
        )

    def _get_selected_initial_fields(self):
        return MetadataFields.normalize_selected_keys(
            self.initial_fields_grid.get_checked_keys(),
            allowed_keys=MetadataFields.initial_keys(),
        )

    def _get_selected_mrk_fields(self):
        return MetadataFields.normalize_selected_keys(
            self.mrk_fields_grid.get_checked_keys(),
            allowed_keys=MetadataFields.mrk_keys(),
        )

    def _load_prefs(self):
        folder_path = self.preferences.get("folder", "")
        if folder_path:
            self.folder_selector.set_path(folder_path)
            self.logger.debug(
                "Caminho restaurado", code="PREFS_FOLDER_RESTORED", path=folder_path
            )
        self.checkbox_map["recursive"].setChecked(
            self.preferences.get("recursive", True)
        )
        self.checkbox_map["use_mrk"].setChecked(
            self.preferences.get("use_mrk", True)
        )
        self.checkbox_map["photos"].setChecked(
            self.preferences.get("photos", True))
        chk_report = self.checkbox_map.get("generate_report")
        if chk_report:
            chk_report.setChecked(
                self.preferences.get("generate_report", True))
        initial_selected = self.preferences.get(self.PREF_INITIAL_FIELDS)
        exif_selected = self.preferences.get(self.PREF_EXIF_FIELDS)
        xmp_selected = self.preferences.get(self.PREF_XMP_FIELDS)
        custom_selected = self.preferences.get(self.PREF_CUSTOM_FIELDS)
        mrk_selected = self.preferences.get(self.PREF_MRK_FIELDS)
        if isinstance(initial_selected, list):
            self.initial_fields_grid.set_checked_keys(
                MetadataFields.normalize_selected_keys(
                    initial_selected,
                    allowed_keys=MetadataFields.initial_keys(),
                )
            )
        if isinstance(exif_selected, list):
            self.exif_fields_grid.set_checked_keys(
                MetadataFields.normalize_selected_keys(
                    exif_selected,
                    allowed_keys=MetadataFields.exif_keys(),
                )
            )
        if isinstance(xmp_selected, list):
            self.xmp_fields_grid.set_checked_keys(
                MetadataFields.normalize_selected_keys(
                    xmp_selected,
                    allowed_keys=MetadataFields.xmp_keys(),
                )
            )
        if isinstance(custom_selected, list):
            self.custom_fields_grid.set_checked_keys(
                MetadataFields.normalize_selected_keys(
                    custom_selected,
                    allowed_keys=MetadataFields.custom_keys(),
                )
            )
        if isinstance(mrk_selected, list):
            self.mrk_fields_grid.set_checked_keys(
                MetadataFields.normalize_selected_keys(
                    mrk_selected,
                    allowed_keys=MetadataFields.mrk_keys(),
                )
            )
        self.save_points_selector.set_enabled(
            self.preferences.get("save_file_pts", False)
        )
        self.save_points_selector.set_file_path(
            self.preferences.get("output_path_pts", "")
        )
        self.save_track_selector.set_enabled(
            self.preferences.get("save_file", False))
        self.save_track_selector.set_file_path(
            self.preferences.get("output_path", ""))
        if hasattr(self, "logo_selector") and self.preferences.get("logo_path", ""):
            self.logo_selector.set_file_path(
                self.preferences.get("logo_path", ""))
            self.logo_selector.set_enabled(
                self.preferences.get("logo_enabled", False))
        if hasattr(self, "title_input"):
            title_val = self.preferences.get("project_title", "")
            if title_val:
                self.title_input.set_values({"project_title": title_val})
        self.qml_points_selector.set_enabled(
            self.preferences.get("apply_style_points", False)
        )
        self.qml_points_selector.set_file_path(
            self.preferences.get("qml_path_points", "")
        )
        self.qml_track_selector.set_enabled(
            self.preferences.get("apply_style_track", False)
        )
        self.qml_track_selector.set_file_path(
            self.preferences.get("qml_path_track", "")
        )
        self.opts_collapsible.set_expanded(
            self.preferences.get("opts_expanded", True))
        self.exif_fields_collapsible.set_expanded(
            self.preferences.get("exif_expanded", False)
        )
        self.xmp_fields_collapsible.set_expanded(
            self.preferences.get("xmp_expanded", False)
        )
        self.custom_fields_collapsible.set_expanded(
            self.preferences.get("custom_expanded", False)
        )
        self.initial_fields_collapsible.set_expanded(
            self.preferences.get("initial_expanded", False)
        )
        self.mrk_fields_collapsible.set_expanded(
            self.preferences.get("mrk_expanded", False)
        )
        self.save_collapsible.set_expanded(
            self.preferences.get("save_expanded", False))
        self.styles_collapsible.set_expanded(
            self.preferences.get("styles_expanded", False)
        )

        # Aplica visibilidade do MRK conforme preferência
        use_mrk = self.preferences.get("use_mrk", True)
        self.mrk_fields_collapsible.setVisible(use_mrk)
        self.mrk_fields_collapsible.setEnabled(use_mrk)

        self.logger.debug("Preferências carregadas",
                          code="PREFS_LOAD_COMPLETE")

    def _save_prefs(self):
        self.logger.debug("Salvando preferências", code="PREFS_SAVE_START")
        paths = self.folder_selector.get_paths()
        folder_path = paths[0] if paths else ""
        self.preferences["folder"] = folder_path
        self.preferences["recursive"] = self.checkbox_map["recursive"].isChecked()
        self.preferences["use_mrk"] = self.checkbox_map["use_mrk"].isChecked()
        self.preferences["photos"] = self.checkbox_map["photos"].isChecked()
        chk_report = self.checkbox_map.get("generate_report")
        if chk_report:
            self.preferences["generate_report"] = chk_report.isChecked()
        self.preferences[self.PREF_INITIAL_FIELDS] = self._get_selected_initial_fields(
        )
        self.preferences[self.PREF_EXIF_FIELDS] = self._get_selected_exif_fields()
        self.preferences[self.PREF_XMP_FIELDS] = self._get_selected_xmp_fields()
        self.preferences[self.PREF_CUSTOM_FIELDS] = self._get_selected_custom_fields()
        self.preferences[self.PREF_MRK_FIELDS] = self._get_selected_mrk_fields()
        self.preferences["save_file"] = self.save_track_selector.is_enabled()
        self.preferences["save_file_pts"] = self.save_points_selector.is_enabled()
        self.preferences["output_path"] = self.save_track_selector.get_file_path()
        self.preferences["output_path_pts"] = self.save_points_selector.get_file_path(
        )
        if hasattr(self, "title_input"):
            project_title_values = self.title_input.get_values()
            self.preferences["project_title"] = project_title_values.get(
                "project_title", ""
            )
        if hasattr(self, "logo_selector"):
            self.preferences["logo_path"] = self.logo_selector.get_file_path(
            ).strip()
            self.preferences["logo_enabled"] = self.logo_selector.is_enabled()
        self.preferences["apply_style_track"] = self.qml_track_selector.is_enabled()
        self.preferences["qml_path_track"] = self.qml_track_selector.get_file_path()
        self.preferences["apply_style_points"] = self.qml_points_selector.is_enabled()
        self.preferences["qml_path_points"] = self.qml_points_selector.get_file_path()
        self.preferences["opts_expanded"] = self.opts_collapsible.is_expanded()
        self.preferences["exif_expanded"] = self.exif_fields_collapsible.is_expanded()
        self.preferences["xmp_expanded"] = self.xmp_fields_collapsible.is_expanded()
        self.preferences["custom_expanded"] = (
            self.custom_fields_collapsible.is_expanded()
        )
        self.preferences["initial_expanded"] = (
            self.initial_fields_collapsible.is_expanded()
        )
        self.preferences["mrk_expanded"] = self.mrk_fields_collapsible.is_expanded()
        self.preferences["save_expanded"] = self.save_collapsible.is_expanded()
        self.preferences["styles_expanded"] = self.styles_collapsible.is_expanded()
        save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.debug("Preferências salvas", code="PREFS_SAVE_COMPLETE")

    def execute_tool(self):
        self.logger.info(
            "Iniciando processamento de coordenadas de drone", code="EXEC_START"
        )

        paths = self.folder_selector.get_paths()
        if not paths:
            self.logger.error("Nenhum diretório selecionado",
                              code="NO_SELECTION")
            return

        apply_photos = self.checkbox_map["photos"].isChecked()

        if apply_photos and not DependenciesManager.check_dependency(
            "Pillow", self.TOOL_KEY
        ):
            self.logger.warning(
                "Cruzamento com metadados solicitado sem Pillow disponível; será ignorado"
            )
            apply_photos = False
            self.checkbox_map["photos"].setChecked(False)

        first_path = paths[0] if paths else None
        base_folder = (
            os.path.dirname(first_path)
            if first_path and os.path.isfile(first_path)
            else first_path
        )

        # Salva preferências atuais antes de executar
        self._save_prefs()

        # Delega montagem e execução do pipeline para o DronePipelineService
        DronePipelineService.execute(
            iface=self.iface,
            input_path=base_folder,
            paths=paths,
        )


def run(iface):
    dlg = DroneCordinates(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
