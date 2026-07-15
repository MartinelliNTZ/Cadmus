# -*- coding: utf-8 -*-
from qgis.core import QgsCoordinateReferenceSystem

from ..utils.StringManager import StringManager
from ..plugins.BasePlugin import BasePluginMTL
from ..utils.Preferences import Preferences
from ..utils.ToolKeys import ToolKey
from ..utils.ExplorerUtils import ExplorerUtils
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR, TranslationManager
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..core.config.MenuManager import MenuManager


class SettingsPlugin(BasePluginMTL):
    """
    Plugin de configurações do Cadmus.

    Permite ao usuário:
    - Acessar preferências do aplicativo
    - Configurar método de cálculo vetorial (Elipsoidal, Cartesiana, Ambos)
    """

    CALCULATION_METHODS = [
        STR.ELLIPSOIDAL,
        STR.CARTESIAN,
        STR.BOTH,
    ]
    DEFAULT_CRS_AUTHID = "EPSG:4326"
    AUTO_SAVE_PREFS_ON_CLOSE = False
    system_preferences = {}
    prefer_VectorFields = {}
    toolbar_category_checks = {}

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(ToolKey.SETTINGS, "SettingsPlugin", load_system_prefs=True)
        self.logger.info("SettingsPlugin inicializado")

    def _build_ui(self, **kwargs):
        """Constrói a interface de configurações."""
        self.logger.debug("Construindo interface de configurações")

        super()._build_ui(
            title=STR.SETTINGS_TITLE,
            icon_path="settings.ico",
        )

        self.logger.info("Construindo componentes de interface")

        pref_button_layout, self.pref_button = WidgetFactory.create_simple_button(
            text=STR.OPEN_PREFERENCES_FOLDER,
            parent=self,
            spacing=2,
        )
        self.pref_button.clicked.connect(self._open_preferences_folder)

        self.logger.debug("Botão de preferências adicionado")

        calc_layout, self.radio_calc = WidgetFactory.create_radio_button_grid(
            items=self.CALCULATION_METHODS,
            columns=3,
            title=f"⚙️ {STR.VECTOR_CALCULATION_METHOD}",
            checked_index=0,
            tool_key=ToolKey.SETTINGS,
            separator_top=False,
            separator_bottom=False,
            parent=self,
        )
        self.logger.debug("Widget de cálculo vetorial adicionado")

        langs = StringManager.AVAILABLE_LANGUAGES
        selected_lang = self.system_preferences.get("plugin_language", "none")
        lang_layout, self.lang_selector = WidgetFactory.create_dropdown_selector(
            title=f"⚙️ {STR.PLUGIN_LANGUAGE}",
            options_dict=langs,
            selected_key=selected_lang,
            separator_top=False,
            separator_bottom=False,
            parent=self,
        )

        crs_layout, self.crs_selector = WidgetFactory.create_crs_selector(
            title=STR.DEFAULT_CRS,
            tool_key=ToolKey.SETTINGS,
            default_auth_id=self.system_preferences.get(
                "default_crs_authid", self.DEFAULT_CRS_AUTHID
            ),
            separator_top=False,
            separator_bottom=False,
            parent=self,
        )
        self.logger.debug("Widget exclusivo de selecao de SRC adicionado")

        prec_layout, self.spin_precision = WidgetFactory.create_double_spin_input(
            f"🎯 {STR.VECTOR_FIELDS_PRECISION}",
            decimals=0,
            step=1,
            minimum=0,
            maximum=10,
            value=2,
            separator_top=False,
            separator_bottom=False,
        )
        self.logger.debug("Widget de precisão de campos vetoriais adicionado")

        thresh_layout, self.spin_threshold = WidgetFactory.create_double_spin_input(
            f"📦 {STR.ASYNC_THRESHOLD}",
            decimals=0,
            step=1,
            minimum=1,
            maximum=100000000,
            value=1000,
            separator_top=False,
            separator_bottom=False,
        )
        self.logger.debug("Widget de limiar assíncrono por feições adicionado")

        toolbar_layout, self.toolbar_category_checks = (
            WidgetFactory.create_checkbox_grid(
                options_dict=MenuManager.toolbar_category_options(),
                items_per_row=3,
                checked_by_default=True,
                title=STR.TOOLBAR_VISIBLE_CATEGORIES,
                separator_top=False,
                separator_bottom=False,
            )
        )
        self.logger.debug("Grid de categorias visiveis da toolbar adicionado")

        geral_layout, self.geral_collapsable = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title=STR.GENERAL,
                expanded_by_default=True,
                separator_top=False,
                separator_bottom=False,
            )
        )

        projects_layout, self.project_folder_selector = (
            WidgetFactory.create_path_selector(
                title=STR.PROJECTS_FOLDER,
                mode="folder",
                parent=self,
                separator_top=False,
                separator_bottom=False,
            )
        )

        self.geral_collapsable.add_content_layout(projects_layout)
        self.geral_collapsable.add_content_layout(crs_layout)
        self.geral_collapsable.add_content_layout(lang_layout)
        self.geral_collapsable.add_content_layout(prec_layout)
        self.geral_collapsable.add_content_layout(thresh_layout)
        self.geral_collapsable.add_content_layout(pref_button_layout)

        lic_layout, self.lic_btn = WidgetFactory.create_simple_button(
            text="_",
            parent=self,
            spacing=6,
        )
        self.lic_btn.clicked.connect(self._open_lic_dialog)
        self.geral_collapsable.add_content_layout(lic_layout)

        self.geral_collapsable.add_content_layout(toolbar_layout)

        calc_layout_collapsible, self.calc_collapsable = (
            WidgetFactory.create_collapsible_parameters(
                parent=self,
                title=STR.VECTOR_CALCULATIONS_PLUGIN,
                expanded_by_default=False,
                separator_top=False,
                separator_bottom=False,
            )
        )
        self.calc_collapsable.add_content_layout(calc_layout)

        field_names_layout, self.area_fields_inputs = (
            WidgetFactory.create_input_fields_widget(
                fields_dict={
                    "cartesian_suffix": {
                        "title": STR.CARTESIAN_SUFFIX,
                        "type": "text",
                        "default": "",
                    },
                    "ellipsoidal_suffix": {
                        "title": STR.ELLIPSOIDAL_SUFFIX,
                        "type": "text",
                        "default": "_eli",
                    },
                },
                parent=self,
                separator_top=False,
                separator_bottom=False,
            )
        )
        self.calc_collapsable.add_content_layout(field_names_layout)

        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=ToolKey.SETTINGS,
                run_text=STR.SAVE,
            )
        )

        self.layout.add_items(
            [
                geral_layout,
                calc_layout_collapsible,
                buttons_layout,
            ]
        )
        self.logger.info("Interface de configurações construída com sucesso")

    def _load_prefs(self):
        """Carrega preferências salvas."""
        self.logger.debug("Carregando preferências")
        self.prefer_VectorFields = Preferences.load_tool_prefs(ToolKey.VECTOR_FIELDS)

        calc_method = self.system_preferences.get("calculation_method", STR.ELLIPSOIDAL)
        if calc_method in self.CALCULATION_METHODS:
            self.radio_calc.set_selected_index(
                self.CALCULATION_METHODS.index(calc_method)
            )
            self.logger.debug(f"Método de cálculo carregado: {calc_method}")
        else:
            self.logger.warning(
                f"Método de cálculo inválido: {calc_method}, usando padrão"
            )
            self.radio_calc.set_selected_index(0)

        selected_language = self.system_preferences.get("plugin_language", "none")
        if selected_language in StringManager.AVAILABLE_LANGUAGES:
            self.lang_selector.set_selected_key(selected_language)
            self.logger.debug(f"Idioma selecionado carregado: {selected_language}")
        else:
            self.logger.warning(f"Idioma inválido: {selected_language}, usando padrão")
            self.lang_selector.set_selected_key("pt_BR")

        selected_crs_authid = self.system_preferences.get(
            "default_crs_authid", self.DEFAULT_CRS_AUTHID
        )
        if not self.crs_selector.set_crs_authid(selected_crs_authid):
            self.logger.warning(f"SRC invalido: {selected_crs_authid}, usando padrao")
            self.crs_selector.set_crs_authid(self.DEFAULT_CRS_AUTHID)
        self.logger.debug(f"SRC padrao carregado: {self.crs_selector.get_crs_authid()}")

        if "async_threshold_features" in self.system_preferences:
            thresh_feats = self.system_preferences.get("async_threshold_features", 1000)
        else:
            old_bytes = self.system_preferences.get("async_threshold_bytes")
            if old_bytes is not None:
                self.logger.warning(
                    "Preferência antiga 'async_threshold_bytes' encontrada, substituindo por limite de feições padrão"
                )
            thresh_feats = 1000

        thresh_value = (
            int(thresh_feats)
            if isinstance(thresh_feats, int)
            else (int(thresh_feats) if str(thresh_feats).isdigit() else 1000)
        )
        self.spin_threshold.setValue(thresh_value)
        self.logger.debug(f"Limiar assíncrono carregado: {thresh_value} feições")

        prec = self.system_preferences.get("vector_field_precision", 2)
        precision_value = (
            int(prec)
            if isinstance(prec, int)
            else (int(prec) if str(prec).isdigit() else 2)
        )
        self.spin_precision.setValue(precision_value)
        self.logger.debug(f"Precisão de campos vetoriais carregada: {precision_value}")

        self.area_fields_inputs.set_values(
            {
                "cartesian_suffix": self.prefer_VectorFields.get(
                    "cartesian_suffix", ""
                ),
                "ellipsoidal_suffix": self.prefer_VectorFields.get(
                    "ellipsoidal_suffix", "_eli"
                ),
            }
        )

        toolbar_visibility = MenuManager.normalize_toolbar_category_visibility(
            self.system_preferences.get(MenuManager.TOOLBAR_VISIBILITY_PREF_KEY)
        )
        for category, checkbox in self.toolbar_category_checks.items():
            checkbox.setChecked(toolbar_visibility.get(category, True))

        project_folder = self.preferences.get("projects_folder", "")
        if project_folder:
            self.project_folder_selector.set_path(project_folder)

        self.calc_collapsable.set_expanded(self.preferences.get("calc_expanded", False))
        self.geral_collapsable.set_expanded(
            self.preferences.get("geral_expanded", True)
        )

    def _save_prefs(self):
        """Salva preferências."""
        self.logger.debug("Salvando preferências")
        self.preferences["calc_expanded"] = self.calc_collapsable.is_expanded()
        self.preferences["geral_expanded"] = self.geral_collapsable.is_expanded()

        selected_text = self.radio_calc.get_selected_text()
        self.system_preferences["calculation_method"] = selected_text
        selected_crs = self.crs_selector.get_crs()
        if not selected_crs or not selected_crs.isValid():
            selected_crs = QgsCoordinateReferenceSystem(self.DEFAULT_CRS_AUTHID)
            self.crs_selector.set_crs(selected_crs)
        self.system_preferences["default_crs_authid"] = selected_crs.authid()
        self.logger.debug(f"SRC padrao salvo: {selected_crs.authid()}")

        feats_value = int(self.spin_threshold.value())
        self.system_preferences["async_threshold_features"] = feats_value
        self.logger.debug(f"Limiar assíncrono por feições salvo: {feats_value} feições")

        precision_val = int(self.spin_precision.value())
        self.system_preferences["vector_field_precision"] = precision_val
        self.logger.debug(f"Precisão de campos vetoriais salva: {precision_val} casas")

        selected_language = self.lang_selector.get_selected_key()
        if selected_language != "none":
            self.system_preferences["plugin_language"] = selected_language
            self.logger.debug(f"Idioma selecionado salvo: {selected_language}")
        else:
            if "plugin_language" in self.system_preferences:
                del self.system_preferences["plugin_language"]
                self.logger.debug("Idioma selecionado removido para auto-detectar")

        toolbar_visibility = {
            category: bool(checkbox.isChecked())
            for category, checkbox in self.toolbar_category_checks.items()
        }

        # Detecta se houve alteração na visibilidade para disparar refresh dinâmico
        old_visibility = self.system_preferences.get(
            MenuManager.TOOLBAR_VISIBILITY_PREF_KEY, {}
        )
        needs_toolbar_refresh = old_visibility != toolbar_visibility

        self.system_preferences[MenuManager.TOOLBAR_VISIBILITY_PREF_KEY] = (
            toolbar_visibility
        )
        self.logger.debug(
            f"Categorias visiveis na toolbar salvas: {toolbar_visibility}"
        )

        paths = self.project_folder_selector.get_paths()
        self.preferences["projects_folder"] = paths[0] if paths else ""

        cartesian_suffix = (
            self.area_fields_inputs.get_value("cartesian_suffix") or ""
        ).strip()
        ellipsoidal_suffix = (
            self.area_fields_inputs.get_value("ellipsoidal_suffix") or "_eli"
        ).strip()

        if cartesian_suffix == ellipsoidal_suffix:
            QgisMessageUtil.modal_warning(
                self.iface,
                STR.AREA_SUFFIXES_CANNOT_MATCH,
            )
            self.logger.warning("Salvamento cancelado: sulfixos de area duplicados")
            return False

        self.prefer_VectorFields["cartesian_suffix"] = cartesian_suffix
        self.prefer_VectorFields["ellipsoidal_suffix"] = ellipsoidal_suffix

        self._persist_window_size()
        self.on_finish_plugin()
        Preferences.save_tool_prefs(ToolKey.SYSTEM, self.system_preferences)
        Preferences.save_tool_prefs(ToolKey.VECTOR_FIELDS, self.prefer_VectorFields)
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.info(
            f"Preferências salvas:{self.system_preferences}==={self.preferences}"
        )

        # Se a visibilidade mudou, emite um evento abstrato para ajustes de toolbar
        if needs_toolbar_refresh:
            try:
                from ..core.config.PyQtSignalManager import get_plugin_signal_hub

                hub = get_plugin_signal_hub()
                hub.toolbar_category_visibility_changed.emit(toolbar_visibility)
                self.logger.debug(
                    "Sinal de alteração de visibilidade da toolbar emitido pelo SettingsPlugin"
                )
            except Exception as e:
                self.logger.error(
                    f"Erro ao emitir sinal de alteração de visibilidade da toolbar: {e}"
                )

        return True

    def execute_tool(self):
        """Executa as configurações e fecha o diálogo."""
        self.logger.info("Aplicando configurações")
        if not self._save_prefs():
            return

        selected_method = self.radio_calc.get_selected_text()
        QgisMessageUtil.modal_info(
            self.iface,
            message=(
                f"{STR.CALCULATION_METHOD_LABEL} {selected_method}. "
                f"{STR.DEFAULT_CRS}: {self.crs_selector.get_crs_authid()}. "
                f"{STR.SETTINGS_SAVED_MESSAGE}"
            ),
        )

        # Recarregar strings de tradução com o novo idioma
        TranslationManager.reload_strings()
        self.logger.info(
            f"TranslationManager recarregado com locale: "
            f"{self.system_preferences.get('plugin_language', 'pt_BR')}"
        )

        self.logger.info("Configurações aplicadas e salvas")
        self.close()

    def _open_lic_dialog(self):
        """
        Abre o diálogo de gerenciamento de licença.
        A licença é salva/gerenciada pelo LicDialog diretamente via LicManager.
        """
        self.logger.debug("Abrindo diálogo de gerenciamento de licença")
        from ..core.ui.RegistryDialog import RegistryDialog

        dialog = RegistryDialog(iface=self.iface, parent=self)
        if hasattr(dialog, "exec_"):
            dialog.exec_()
        else:
            dialog.exec()

    def _open_preferences_folder(self):
        """Abre a pasta de preferências do Cadmus."""
        self.logger.debug("Abrindo pasta de preferências")

        from ..utils.Preferences import PREF_FOLDER

        if ExplorerUtils.open_folder(PREF_FOLDER, self.TOOL_KEY):
            self.logger.info(f"Abrindo pasta: {PREF_FOLDER}")
        else:
            self.logger.warning(f"Pasta de preferências não encontrada: {PREF_FOLDER}")
            QgisMessageUtil.modal_warning(
                iface=self.iface,
                message=f"{STR.PREFERENCES_FOLDER_NOT_FOUND} {PREF_FOLDER}",
            )


def run(iface):
    """Função de entrada do plugin."""
    dlg = SettingsPlugin(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
