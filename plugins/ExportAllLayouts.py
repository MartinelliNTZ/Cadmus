# -*- coding: utf-8 -*-
"""
ExportAllLayoutsDialog - Exportar todos os layouts em PDF/PNG

Plugin refatorado para estender BasePluginMTL com WidgetFactory para UI padronizada.
"""

import os
import re
from qgis.core import QgsProject, QgsLayoutExporter
from qgis.PyQt.QtCore import QCoreApplication, QUrl

from ..plugins.BasePlugin import BasePluginMTL
from ..utils.Preferences import load_tool_prefs, save_tool_prefs
from ..utils.PDFUtils import PDFUtils
from ..utils.DependenciesManager import DependenciesManager
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ToolKeys import ToolKey
from ..core.ui.WidgetFactory import WidgetFactory
from ..core.ui.ProgressDialog import ProgressDialog


class ExportAllLayoutsDialog(BasePluginMTL):
    """
    Plugin para exportar todos os layouts do projeto em PDF e/ou PNG.
    
    Estende BasePluginMTL para:
    - Interface padronizada com MainLayout + AppBar
    - Persistência automática de preferências via _save_prefs()
    - Carregamento automático via _load_prefs()
    - Widgets padronizados via WidgetFactory
    """

    TOOL_KEY = ToolKey.EXPORT_ALL_LAYOUTS
    
    # Mapeamento de opções para checkboxes (chave: label)
    CHECKBOX_OPTIONS = {
        "export_pdf": "Exportar PDF",
        "export_png": "Exportar PNG",
        "merge_pdf": "Unir PDFs em PDF final",
        "merge_png": "Unir PNGs em PDF final",
        "replace_existing": "Substituir arquivos existentes"
    }

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        
        # Inicializar com BasePluginMTL
        self.init(
            self.TOOL_KEY,
            "ExportAllLayoutsDialog",
            load_settings_prefs=False,
            build_ui=True
        )

    def _build_ui(self, **kwargs):
        """Constrói a interface de exportação com WidgetFactory."""
        self.logger.debug("Construindo UI de exportação de layouts")
        
        super()._build_ui(
            title="Exportar Todos os Layouts",
            icon_path="export_icon.ico",
            instructions_file="export_all_layouts_help.md",
            enable_scroll=False  # Simples, cabe na tela
        )
        
        self.logger.info("Construindo componentes de interface")

        # ========== SEÇÃO 1: Opções de Exportação (Grid Checkboxes - 2 colunas) ==========
        checkboxes_layout, self.checkbox_map = WidgetFactory.create_checkbox_grid(
            options_dict=self.CHECKBOX_OPTIONS,
            items_per_row=2,
            checked_by_default=False,
            title="Opções de Exportação",
            separator_top=False,
            separator_bottom=True
        )
        self.logger.debug("Grid de checkboxes de exportação criado")

        # ========== SEÇÃO 2: Max Width para PNGs ==========
        max_width_layout, self.max_width_input = WidgetFactory.create_input_fields_widget(
            fields_dict={
                'max_width': {
                    'title': 'Max Width para PNG (px):',
                    'type': 'int',
                    'default': 3500
                }
            },
            parent=self,
            separator_top=False,
            separator_bottom=True
        )
        self.logger.debug("Widget de Max Width criado")

        # ========== SEÇÃO 3: Pasta de Saída (Path Selector com SimpleButton) ==========
        folder_layout, self.folder_selector = WidgetFactory.create_path_selector(
            parent=self,
            title="Pasta de saída:",
            mode="folder",
            separator_top=False,
            separator_bottom=False
        )
        self.logger.debug("Path Selector de pasta de saída criado")

        # Botão simples para "Usar pasta do projeto"
        btn_project_layout, self.btn_project = WidgetFactory.create_simple_button(
            text="Usar pasta do projeto",
            parent=self,
        )
        self.btn_project.clicked.connect(self._set_folder_to_project)
        self.logger.debug("Botão 'Usar pasta do projeto' criado")

        # ========== SEÇÃO 4: Botões de Ação ==========
        buttons_layout, self.action_buttons = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=self.execute_tool,
            close_callback=self.close,
            info_callback=self.show_info_dialog,
            tool_key=self.TOOL_KEY,
            run_text="Exportar"
        )
        self.logger.debug("Botões de ação criados")

        # ========== ADICIONAR TODOS OS ITEMS AO LAYOUT ==========
        self.layout.add_items([
            checkboxes_layout,
            max_width_layout,
            folder_layout,
            btn_project_layout,
            buttons_layout
        ])
        
        self.logger.info("Interface de exportação construída com sucesso")

    def _load_prefs(self):
        """Carrega preferências salvas do arquivo JSON."""
        self.logger.debug("Carregando preferências de exportação")
        self.preferences = load_tool_prefs(self.TOOL_KEY)

        # Checkboxes (padrões true para PDF e PNG)
        self.checkbox_map["export_pdf"].setChecked(
            self.preferences.get("export_pdf", True)
        )
        self.checkbox_map["export_png"].setChecked(
            self.preferences.get("export_png", True)
        )
        self.checkbox_map["merge_pdf"].setChecked(
            self.preferences.get("merge_pdf", False)
        )
        self.checkbox_map["merge_png"].setChecked(
            self.preferences.get("merge_png", False)
        )
        self.checkbox_map["replace_existing"].setChecked(
            self.preferences.get("replace_existing", False)
        )

        # Max Width
        max_width = self.preferences.get("max_width", 3500)
        self.max_width_input.set_value('max_width', max_width)
        self.logger.debug(f"Max width carregado: {max_width}px")

        # Pasta de saída
        pasta_default = os.path.join(QgsProject.instance().homePath(), "exports")
        pasta_salva = self.preferences.get("output_folder", pasta_default)
        self.folder_selector.set_paths([pasta_salva])
        self.logger.debug(f"Pasta de saída carregada: {pasta_salva}")

    def _save_prefs(self):
        """Salva preferências em arquivo JSON."""
        self.logger.debug("Salvando preferências de exportação")

        # Checkboxes
        self.preferences['export_pdf'] = self.checkbox_map["export_pdf"].isChecked()
        self.preferences['export_png'] = self.checkbox_map["export_png"].isChecked()
        self.preferences['merge_pdf'] = self.checkbox_map["merge_pdf"].isChecked()
        self.preferences['merge_png'] = self.checkbox_map["merge_png"].isChecked()
        self.preferences['replace_existing'] = self.checkbox_map["replace_existing"].isChecked()

        # Max Width
        max_width_values = self.max_width_input.get_values()
        self.preferences['max_width'] = int(max_width_values.get('max_width', 3500))

        # Pasta
        paths = self.folder_selector.get_paths()
        pasta = paths[0] if paths else os.path.join(QgsProject.instance().homePath(), "exports")
        self.preferences['output_folder'] = pasta

        # Tamanho da janela (automático via BasePlugin)
        self.preferences['window_width'] = self.width()
        self.preferences['window_height'] = self.height()

        save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.info(f"Preferências salvas: PDF={self.preferences['export_pdf']}, PNG={self.preferences['export_png']}")

    def _set_folder_to_project(self):
        """Callback do botão 'Usar pasta do projeto'."""
        self.logger.debug("Definindo pasta para pasta do projeto")
        project_folder = QgsProject.instance().homePath()
        export_folder = os.path.join(project_folder, "exports")
        self.folder_selector.set_paths([export_folder])
        self.logger.debug(f"Pasta definida para: {export_folder}")

    def execute_tool(self):
        """
        Executa a exportação de todos os layouts.
        
        Valida dependências (PyPDF2, Pillow) oferecendo instalação automática.
        """
        self.logger.info("Iniciando exportação de layouts")

        # ========== LEITURA DE VALORES ==========
        export_pdf = self.checkbox_map["export_pdf"].isChecked()
        export_png = self.checkbox_map["export_png"].isChecked()
        merge_pdf = self.checkbox_map["merge_pdf"].isChecked()
        merge_png = self.checkbox_map["merge_png"].isChecked()
        replace_existing = self.checkbox_map["replace_existing"].isChecked()

        max_width_values = self.max_width_input.get_values()
        max_width = int(max_width_values.get('max_width', 3500))

        paths = self.folder_selector.get_paths()
        output_folder = paths[0] if paths else os.path.join(QgsProject.instance().homePath(), "exports")
        
        # Validação básica
        if not export_pdf and not export_png:
            QgisMessageUtil.modal_error(self.iface, "Selecione pelo menos um formato (PDF ou PNG)")
            return

        os.makedirs(output_folder, exist_ok=True)
        self.logger.info(f"Pasta de saída: {output_folder}")

        # ========== VALIDAÇÃO DE DEPENDÊNCIAS ==========
        if merge_pdf and not DependenciesManager.check_dependency('PyPDF2'):
            if QgisMessageUtil.confirm(
                self.iface,
                "Para unir PDFs é necessário instalar o pacote PyPDF2.\n\nDeseja instalar agora?",
                "Biblioteca necessária"
            ):
                DependenciesManager.install_dependency('PyPDF2')
            else:
                merge_pdf = False

        if merge_png and not DependenciesManager.check_dependency('Pillow'):
            if QgisMessageUtil.confirm(
                self.iface,
                "Para unir PNGs em PDF é necessário instalar o pacote Pillow.\n\nDeseja instalar agora?",
                "Biblioteca necessária"
            ):
                DependenciesManager.install_dependency('Pillow')
            else:
                merge_png = False

        # ========== EXPORTAÇÃO DOS LAYOUTS ==========
        project = QgsProject.instance()
        layouts = project.layoutManager().layouts()

        pdf_list = []
        png_list = []
        total = len(layouts)
        self.logger.info(f"Iniciando exportação de {total} layout(s)")
        
        # Criar ProgressDialog DEPOIS de calcular total
        progress = ProgressDialog("Exportando layouts...", "Cancelar", 0, total, self)
        progress.show()

        erros = []
        sucesso = 0

        for i, layout in enumerate(layouts):
            progress.set_value(i)
            QCoreApplication.processEvents()

            if progress.is_canceled():
                self.logger.warning(f"Exportação cancelada pelo usuário em layout {i+1}/{total}")
                break

            # Sanitizar nome do layout
            nome = re.sub(r'[<>:"/\\|?*]', '', layout.name().strip())
            pdf_path = os.path.join(output_folder, f"{nome}.pdf")
            png_path = os.path.join(output_folder, f"{nome}.png")

            # Evitar sobrescrita se não marcado "replace"
            if not replace_existing:
                base = nome
                count = 1
                while os.path.exists(pdf_path) or os.path.exists(png_path):
                    nome_novo = f"{base}_{count}"
                    pdf_path = os.path.join(output_folder, f"{nome_novo}.pdf")
                    png_path = os.path.join(output_folder, f"{nome_novo}.png")
                    count += 1

            try:
                exporter = QgsLayoutExporter(layout)
                ok_pdf = ok_png = True

                if export_pdf:
                    result = exporter.exportToPdf(pdf_path, QgsLayoutExporter.PdfExportSettings())
                    ok_pdf = result == QgsLayoutExporter.Success
                    if ok_pdf:
                        pdf_list.append(pdf_path)
                        self.logger.debug(f"PDF exportado: {pdf_path}")
                    else:
                        erros.append(f"Falha ao exportar PDF: {nome}")

                if export_png:
                    result = exporter.exportToImage(png_path, QgsLayoutExporter.ImageExportSettings())
                    ok_png = result == QgsLayoutExporter.Success
                    if ok_png:
                        png_list.append(png_path)
                        self.logger.debug(f"PNG exportado: {png_path}")
                    else:
                        erros.append(f"Falha ao exportar PNG: {nome}")

                if ok_pdf or ok_png:
                    sucesso += 1

            except Exception as e:
                erro_msg = f"Erro exportando {nome}: {str(e)}"
                self.logger.error(erro_msg)
                erros.append(erro_msg)

        self.logger.info(f"Loop de exportação concluído: {sucesso}/{total} layouts processados com sucesso")
        
        progress.set_value(total)
        self.logger.debug("ProgressDialog : progresso setado para 100%")
        
        progress.close()
        self.logger.debug("ProgressDialog: diálogo fechado")

        # ========== UNIR PDFs ==========
        merge_pdf_success = False
        if merge_pdf and pdf_list:
            self.logger.debug(f"Unindo {len(pdf_list)} PDFs")
            ok, msg_text = PDFUtils.merge_pdfs(
                pdf_list,
                os.path.join(output_folder, "_PDF_UNICO_FINAL.pdf")
            )
            if ok:
                self.logger.info(f"✓ PDFs unidos com sucesso: {msg_text}")
                merge_pdf_success = True
            else:
                self.logger.warning(f"Falha ao unir PDFs: {msg_text}")
                erros.append(f"Falha ao unir PDFs: {msg_text}")

        # ========== UNIR PNGs ==========
        merge_png_success = False
        if merge_png and png_list:
            self.logger.info(f"Iniciando merge de {len(png_list)} PNGs em PDF (max_width={max_width}px)")
            ok, msg_text = PDFUtils.merge_pngs_to_pdf(
                png_list,
                os.path.join(output_folder, "_PNG_MERGED_FINAL.pdf"),
                max_width
            )
            if ok:
                self.logger.info(f"✓ PNGs unidos com sucesso: {msg_text}")
                merge_png_success = True
            else:
                self.logger.warning(f"Falha ao unir PNGs: {msg_text}")
                erros.append(f"Falha ao unir PNGs: {msg_text}")

        # ========== RESULTADO FINAL ==========
        self.logger.info(f"Início da montagem de mensagem de resultado. Total: {sucesso} sucessos, {len(erros)} erros")
        
        texto = ""
        if erros:
            texto += "<b>⚠️ Erros encontrados:</b><br>" + "<br>".join(erros) + "<br><br>"
            self.logger.warning(f"Erros detectados na exportação: {len(erros)}")
        
        # Resumo de sucessos
        sucesso_text = f"<b>✓ {sucesso}</b> layout(s) exportado(s) com sucesso!"
        if merge_pdf_success:
            sucesso_text += "<br><b>✓ PDFs unidos</b> em _PDF_UNICO_FINAL.pdf"
            self.logger.debug("✓ Merge de PDFs realizado")
        if merge_png_success:
            sucesso_text += "<br><b>✓ PNGs unidos</b> em _PNG_MERGED_FINAL.pdf"
            self.logger.debug("✓ Merge de PNGs realizado")
        
        texto += sucesso_text

        self.logger.info(f"Exportação concluída: {sucesso} layout(s) bem-sucedido(s), {len(erros)} erro(s), PDF merge={merge_pdf_success}, PNG merge={merge_png_success}")

        self.logger.debug("Tentando exibir diálogo modal de resultado...")
        try:
            QgisMessageUtil.modal_result_with_folder(
                self.iface,
                "Exportação de Layouts Concluída",
                texto,
                output_folder,
                parent=self
            )
            self.logger.debug("✓ Diálogo de resultado exibido com sucesso e fechado pelo usuário")
        except Exception as modal_error:
            self.logger.error(f"Erro ao exibir diálogo de resultado: {str(modal_error)}")
            raise


def run_export_all_layouts(iface):
    """Função de entrada do plugin."""
    dlg = ExportAllLayoutsDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
