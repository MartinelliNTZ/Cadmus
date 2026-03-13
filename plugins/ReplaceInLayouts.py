# -*- coding: utf-8 -*-

from ..utils import load_tool_prefs, save_tool_prefs
from ..utils import QgisMessageUtil
from ..utils import LayoutsUtils
from ..utils import ProjectUtils
from ..utils import ToolKey
from .BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory


class ReplaceInLayoutsDialog(BasePluginMTL):
    CHECKBOX_OPTIONS = {
        "case_sensitive": "Diferenciar maiúsculas/minúsculas",
        "full_replace": "Substituir o label inteiro quando encontrar o texto"
    }

    TOOL_KEY = ToolKey.REPLACE_IN_LAYOUTS

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        
        self.init(
            self.TOOL_KEY,
            "ReplaceInLayoutsDialog",
            load_settings_prefs=False,
            build_ui=True,
        )

    def _build_ui(self, **kwargs):
        super()._build_ui(
            title="Substituir Texto em Layouts",
            icon_path="Cadmus_icon.png",
            instructions_file="replace_in_layouts_help.md",
            enable_scroll=False,
        )

        # ====== BUSCAR E SUBSTITUIR ======
        input_layout, self.input_fields_widget = WidgetFactory.create_input_fields_widget(
            fields_dict={
                'old_text': {
                    'title': 'Texto a buscar:',
                    'type': 'text',
                    'default': ''
                },
                'new_text': {
                    'title': 'Texto a substituir (novo):',
                    'type': 'text',
                    'default': ''
                }
            },
            separator_bottom=False
        )

        # ====== BOTÃO DE TROCA ======
        swap_layout, self.swap_button = WidgetFactory.create_simple_button(
            text="⇅ Inverter",
            parent=self,
            separator_top=False,
            separator_bottom=True,
            spacing=12
        )
        self.swap_button.clicked.connect(self._swap_fields)

        # ====== OPÇÕES ======
        opts_layout, self.checkbox_map = WidgetFactory.create_checkbox_grid(
            options_dict=self.CHECKBOX_OPTIONS,
            items_per_row=1,
            checked_by_default=False,
            separator_bottom=True
        )

        # ====== INFO ======
        info_label = WidgetFactory.create_label(
            text="Backup: será criada uma cópia do projeto (.qgz) na pasta backup ao lado do arquivo do projeto.",
            word_wrap=True,
            bold=False
        )

        # ====== BOTÕES ======
        buttons_layout, self.action_buttons = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=self.execute_tool,
            close_callback=self.close,
            info_callback=self.show_info_dialog,
            tool_key=self.TOOL_KEY,
            run_text="Executar substituição",
            close_text="Fechar"
        )

        # ====== ADICIONAR AO LAYOUT ======
        self.layout.add_items([
            input_layout,
            swap_layout,
            opts_layout,
            info_label,
            buttons_layout
        ])



    def _load_prefs(self):
        prefs = load_tool_prefs(self.TOOL_KEY)

        self.input_fields_widget.set_values({
            'old_text': prefs.get("old_text", ""),
            'new_text': prefs.get("new_text", "")
        })
        self.checkbox_map["case_sensitive"].setChecked(
            prefs.get("case_sensitive", True)
        )
        self.checkbox_map["full_replace"].setChecked(
            prefs.get("full_replace", False)
        )

    def _save_prefs(self):
        values = self.input_fields_widget.get_values()
        save_tool_prefs(
            self.TOOL_KEY,
            {
                "old_text": values.get('old_text', ''),
                "new_text": values.get('new_text', ''),
                "case_sensitive": self.checkbox_map["case_sensitive"].isChecked(),
                "full_replace": self.checkbox_map["full_replace"].isChecked(),
                # Tamanho da janela (persistido automaticamente por BasePlugin.closeEvent)
                "window_width": self.width(),
                "window_height": self.height(),
            }
        )

    def _swap_fields(self):
        """Inverte o conteúdo dos campos old_text e new_text."""
        values = self.input_fields_widget.get_values()
        old = values.get('old_text', '')
        new = values.get('new_text', '')
        
        # Troca os valores
        self.input_fields_widget.set_values({
            'old_text': new,
            'new_text': old
        })

    def execute_tool(self):
        values = self.input_fields_widget.get_values()
        old_text = values.get('old_text', '').strip()
        new_text = values.get('new_text', '')
        case_sensitive = self.checkbox_map["case_sensitive"].isChecked()
        full_replace = self.checkbox_map["full_replace"].isChecked()

        if not old_text:
            QgisMessageUtil.bar_warning(
                self.iface,
                "Informe o texto a buscar."
            )
            return

        self._save_prefs()

        if not QgisMessageUtil.confirm_destructive(
            self,
            "Confirme substituições",
            (                
                f"<b>Buscar:</b> <i>{old_text}</i><br>"
                f"<b>Substituir por:</b> <i>{new_text}</i>"
            ),
            red_text="Atenção — operação destrutiva"
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
                full_replace=full_replace
            )
            total = result.get("total_changes", 0)
            layouts = result.get("total_layouts", 0)
            message = f"<b>Layouts analisados:</b> {layouts}<br>" f"<b>Substituições aplicadas:</b> {total}"
            QgisMessageUtil.modal_success(
                self.iface,
                message,
                "Substituição concluída"
            )       
        except Exception as e:
            QgisMessageUtil.bar_critical(
                self,
                str(e),
                "Erro"
            )


def run_replace_in_layouts(iface):
    dlg = ReplaceInLayoutsDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
