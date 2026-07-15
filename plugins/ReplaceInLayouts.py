# -*- coding: utf-8 -*-
from ..utils.Preferences import Preferences
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.LayoutsUtils import LayoutsUtils
from ..utils.ProjectUtils import ProjectUtils
from ..utils.ToolKeys import ToolKey
from .BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR


class ReplaceInLayoutsDialog(BasePluginMTL):
    CHECKBOX_OPTIONS = {
        "case_sensitive": STR.CASE_SENSITIVE,
        "full_replace": STR.FULL_LABEL_REPLACE,
    }

    TOOL_KEY = ToolKey.REPLACE_IN_LAYOUTS

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface

        self.init(
            self.TOOL_KEY,
            "ReplaceInLayoutsDialog",
            load_system_prefs=False,
            build_ui=True,
        )

    def _build_ui(self, **kwargs):
        super()._build_ui(
            title=STR.REPLACE_IN_LAYOUTS_TITLE,
            icon_path="Cadmus_icon.png",
            enable_scroll=False,
        )

        # ====== BUSCAR E SUBSTITUIR ======
        input_layout, self.input_fields_widget = (
            WidgetFactory.create_input_fields_widget(
                fields_dict={
                    "old_text": {
                        "title": STR.SEARCH_TEXT,
                        "type": "text",
                        "default": "",
                    },
                    "new_text": {
                        "title": STR.REPLACE_WITH_NEW_TEXT,
                        "type": "text",
                        "default": "",
                    },
                },
                separator_bottom=False,
            )
        )

        # ====== BOTÃO DE TROCA ======
        swap_layout, self.swap_button = WidgetFactory.create_simple_button(
            text=f"⇄ {STR.REPLACE_IN_LAYOUTS_SWAP}",
            parent=self,
            separator_top=False,
            separator_bottom=True,
            spacing=12,
        )
        self.swap_button.clicked.connect(self._swap_fields)

        # ====== OPÇÕES ======
        opts_layout, self.checkbox_map = WidgetFactory.create_checkbox_grid(
            options_dict=self.CHECKBOX_OPTIONS,
            items_per_row=1,
            checked_by_default=False,
            separator_bottom=True,
        )

        # ====== INFO ======
        info_label = WidgetFactory.create_label(
            text=STR.PROJECT_BACKUP_INFO,
            word_wrap=True,
            bold=False,
        )

        # ====== BOTÕES ======
        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
                run_text=STR.REPLACE_IN_LAYOUTS_RUN,
                close_text=STR.CLOSE,
            )
        )

        # ====== ADICIONAR AO LAYOUT ======
        self.layout.add_items(
            [input_layout, swap_layout, opts_layout, info_label, buttons_layout]
        )

    def _load_prefs(self):

        self.input_fields_widget.set_values(
            {
                "old_text": self.preferences.get("old_text", ""),
                "new_text": self.preferences.get("new_text", ""),
            }
        )
        self.checkbox_map["case_sensitive"].setChecked(
            self.preferences.get("case_sensitive", True)
        )
        self.checkbox_map["full_replace"].setChecked(self.preferences.get("full_replace", False))

    def _save_prefs(self):
        values = self.input_fields_widget.get_values()
        self.preferences["old_text"] = values.get("old_text", "")
        self.preferences["new_text"] = values.get("new_text", "")
        self.preferences["case_sensitive"] = self.checkbox_map["case_sensitive"].isChecked()
        self.preferences["full_replace"] = self.checkbox_map["full_replace"].isChecked()
        # Tamanho da janela (persistido automaticamente por BasePlugin.closeEvent)
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)

    def _swap_fields(self):
        """Inverte o conteúdo dos campos old_text e new_text."""
        values = self.input_fields_widget.get_values()
        old = values.get("old_text", "")
        new = values.get("new_text", "")

        # Troca os valores
        self.input_fields_widget.set_values({"old_text": new, "new_text": old})

    def execute_tool(self):
        values = self.input_fields_widget.get_values()
        old_text = values.get("old_text", "").strip()
        new_text = values.get("new_text", "")
        case_sensitive = self.checkbox_map["case_sensitive"].isChecked()
        full_replace = self.checkbox_map["full_replace"].isChecked()

        if not old_text:
            QgisMessageUtil.bar_warning(self.iface, STR.ENTER_TEXT_TO_SEARCH)
            return

        self._save_prefs()

        if not QgisMessageUtil.confirm_destructive(
            self,
            STR.CONFIRM_REPLACEMENTS,
            (
                f"<b>{STR.SEARCH_LABEL}</b> <i>{old_text}</i><br>"
                f"<b>{STR.REPLACE_WITH_LABEL}</b> <i>{new_text}</i>"
            ),
            red_text=STR.DESTRUCTIVE_OPERATION_WARNING,
        ):
            return

        project = ProjectUtils.get_project_instance()

        try:
            # BACKUP (se possível)
            if ProjectUtils.is_project_saved(project):
                ProjectUtils.create_project_backup(project)

            # PROCESSA LAYOUTS
            result = LayoutsUtils.replace_text_in_layouts(
                project=project,
                tool_key=self.TOOL_KEY,
                old_text=old_text,
                new_text=new_text,
                case_sensitive=case_sensitive,
                full_replace=full_replace,
            )
            total = result.get("total_changes", 0)
            layouts = result.get("total_layouts", 0)
            message = (
                f"<b>{STR.LAYOUTS_ANALYZED}</b> {layouts}<br>"
                f"<b>{STR.CHANGES_APPLIED}</b> {total}"
            )
            QgisMessageUtil.modal_success(
                self.iface, message, STR.REPLACEMENT_COMPLETED_TITLE
            )
        except Exception as e:
            QgisMessageUtil.bar_critical(self, str(e), STR.ERROR)


def run(iface):
    dlg = ReplaceInLayoutsDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
