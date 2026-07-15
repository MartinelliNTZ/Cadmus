# -*- coding: utf-8 -*-
import os
import re

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsLayoutExporter, QgsProject

from ..core.ui.ProgressDialog import ProgressDialog
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR
from ..plugins.BasePlugin import BasePluginMTL
from ..utils.DependenciesManager import DependenciesManager
from ..utils.PDFUtils import PDFUtils
from ..utils.Preferences import Preferences
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ToolKeys import ToolKey


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

    CHECKBOX_OPTIONS = {
        "export_pdf": STR.EXPORT_PDF,
        "export_png": STR.EXPORT_PNG,
        "merge_pdf": STR.MERGE_PDFS_FINAL,
        "merge_png": STR.MERGE_PNGS_FINAL,
        "replace_existing": STR.REPLACE_EXISTING_FILES,
    }

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self._suppress_merge_dependency_check = False

        self.init(
            self.TOOL_KEY,
            "ExportAllLayoutsDialog",
            load_system_prefs=False,
            build_ui=True,
        )

    def _build_ui(self, **kwargs):
        self.logger.debug("Construindo UI de exportação de layouts")

        super()._build_ui(
            title=STR.EXPORT_ALL_LAYOUTS_TITLE,
            icon_path="export_icon.ico",
            enable_scroll=False,
        )

        self.logger.info("Construindo componentes de interface")

        checkboxes_layout, self.checkbox_map = WidgetFactory.create_checkbox_grid(
            options_dict=self.CHECKBOX_OPTIONS,
            items_per_row=2,
            checked_by_default=False,
            title=STR.EXPORT_OPTIONS,
            separator_top=False,
            separator_bottom=True,
        )
        self.logger.debug("Grid de checkboxes de exportação criado")

        self.chk_merge_pdf = self.checkbox_map.get("merge_pdf")
        if self.chk_merge_pdf:
            self.chk_merge_pdf.toggled.connect(self.on_merge_pdf_changed)

        self.chk_merge_png = self.checkbox_map.get("merge_png")
        if self.chk_merge_png:
            self.chk_merge_png.toggled.connect(self.on_merge_png_changed)

        max_width_layout, self.max_width_input = (
            WidgetFactory.create_input_fields_widget(
                fields_dict={
                    "max_width": {
                        "title": STR.MAX_WIDTH_PNG,
                        "type": "int",
                        "default": 3500,
                    }
                },
                parent=self,
                separator_top=False,
                separator_bottom=True,
            )
        )
        self.logger.debug("Widget de Max Width criado")

        folder_layout, self.folder_selector = WidgetFactory.create_path_selector(
            parent=self,
            title=STR.OUTPUT_FOLDER,
            mode="folder",
            path_button="exports",
            separator_top=False,
            separator_bottom=False,
        )
        self.logger.debug("Path Selector de pasta de saída criado")

        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
                run_text=STR.EXPORT,
            )
        )
        self.logger.debug("Botões de ação criados")

        self.layout.add_items(
            [
                checkboxes_layout,
                max_width_layout,
                folder_layout,
                buttons_layout,
            ]
        )

        self.logger.info("Interface de exportação construída com sucesso")

    def _ensure_merge_dependency(
        self, *, checkbox_key: str, dependency_name: str, message: str
    ) -> bool:
        if DependenciesManager.check_dependency(dependency_name, self.TOOL_KEY):
            self.logger.info(
                f"Dependência {dependency_name} disponível para {checkbox_key}"
            )
            return True

        confirmed = QgisMessageUtil.confirm(
            self.iface,
            message,
            STR.REQUIRED_LIBRARY,
        )

        if not confirmed:
            self.logger.info(
                f"Usuário recusou instalação de {dependency_name}; desmarcando {checkbox_key}"
            )
            self.checkbox_map.get(checkbox_key).setChecked(False)
            return False

        started = DependenciesManager.install_dependency_gui(
            dependency_name, self.iface, self.TOOL_KEY
        )

        if not started:
            self.logger.warning(
                f"Não foi possível iniciar instalação de {dependency_name}; desmarcando {checkbox_key}"
            )
            QgisMessageUtil.modal_error(
                self.iface,
                f"Não foi possível iniciar a instalação da biblioteca {dependency_name}.",
            )
            self.checkbox_map.get(checkbox_key).setChecked(False)
            return False

        self.logger.info(
            f"Instalação de {dependency_name} iniciada a partir do checkbox {checkbox_key}"
        )
        return True

    def on_merge_pdf_changed(self, checked: bool):
        self.logger.debug(f"Estado do checkbox 'merge_pdf' alterado para: {checked}")
        if self._suppress_merge_dependency_check or not checked:
            return

        self._ensure_merge_dependency(
            checkbox_key="merge_pdf",
            dependency_name="colorama",
            message=STR.PYPDF2_REQUIRED_MESSAGE,
        )

    def on_merge_png_changed(self, checked: bool):
        self.logger.debug(f"Estado do checkbox 'merge_png' alterado para: {checked}")
        if self._suppress_merge_dependency_check or not checked:
            return

        self._ensure_merge_dependency(
            checkbox_key="merge_png",
            dependency_name="Pillow",
            message=STR.PILLOW_REQUIRED_MESSAGE,
        )

    def _load_prefs(self):
        # self.logger.debug("Carregando preferências de exportação")
        # self.preferences = load_tool_prefs(self.TOOL_KEY)

        self._suppress_merge_dependency_check = True
        try:
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
        finally:
            self._suppress_merge_dependency_check = False

        max_width = self.preferences.get("max_width", 3500)
        self.max_width_input.set_value("max_width", max_width)
        self.logger.debug(f"Max width carregado: {max_width}px")

        pasta_default = os.path.join(QgsProject.instance().homePath(), "exports")
        pasta_salva = self.preferences.get("output_folder", pasta_default)
        self.folder_selector.set_paths([pasta_salva])
        self.logger.debug(f"Pasta de saída carregada: {pasta_salva}")

    def _save_prefs(self):
        self.logger.debug("Salvando preferências de exportação")

        self.preferences["export_pdf"] = self.checkbox_map["export_pdf"].isChecked()
        self.preferences["export_png"] = self.checkbox_map["export_png"].isChecked()
        self.preferences["merge_pdf"] = self.checkbox_map["merge_pdf"].isChecked()
        self.preferences["merge_png"] = self.checkbox_map["merge_png"].isChecked()
        self.preferences["replace_existing"] = self.checkbox_map[
            "replace_existing"
        ].isChecked()

        max_width_values = self.max_width_input.get_values()
        self.preferences["max_width"] = int(max_width_values.get("max_width", 3500))

        paths = self.folder_selector.get_paths()
        pasta = (
            paths[0]
            if paths
            else os.path.join(QgsProject.instance().homePath(), "exports")
        )
        self.preferences["output_folder"] = pasta

        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.info(
            f"Preferências salvas: PDF={self.preferences['export_pdf']}, PNG={self.preferences['export_png']}"
        )

    def execute_tool(self):
        self.logger.info("Iniciando exportação de layouts")

        export_pdf = self.checkbox_map["export_pdf"].isChecked()
        export_png = self.checkbox_map["export_png"].isChecked()
        merge_pdf = self.checkbox_map["merge_pdf"].isChecked()
        merge_png = self.checkbox_map["merge_png"].isChecked()
        replace_existing = self.checkbox_map["replace_existing"].isChecked()

        max_width_values = self.max_width_input.get_values()
        max_width = int(max_width_values.get("max_width", 3500))

        paths = self.folder_selector.get_paths()
        output_folder = (
            paths[0]
            if paths
            else os.path.join(QgsProject.instance().homePath(), "exports")
        )

        if not export_pdf and not export_png:
            QgisMessageUtil.modal_error(
                self.iface, STR.SELECT_AT_LEAST_ONE_EXPORT_FORMAT
            )
            return

        os.makedirs(output_folder, exist_ok=True)
        self.logger.info(f"Pasta de saída: {output_folder}")

        if merge_pdf and not DependenciesManager.check_dependency(
            "PyPDF2", self.TOOL_KEY
        ):
            self.logger.warning(
                "Merge de PDF solicitado sem PyPDF2 disponível; merge será ignorado"
            )
            merge_pdf = False
            self.checkbox_map.get("merge_pdf").setChecked(False)

        if merge_png and not DependenciesManager.check_dependency(
            "Pillow", self.TOOL_KEY
        ):
            self.logger.warning(
                "Merge de PNG solicitado sem Pillow disponível; merge será ignorado"
            )
            merge_png = False
            self.checkbox_map.get("merge_png").setChecked(False)

        project = QgsProject.instance()
        layouts = project.layoutManager().layouts()

        pdf_list = []
        png_list = []
        total = len(layouts)
        self.logger.info(f"Iniciando exportação de {total} layout(s)")

        progress = ProgressDialog(STR.EXPORTING_LAYOUTS, STR.CANCEL, 0, total, self)
        progress.show()

        erros = []
        sucesso = 0

        for i, layout in enumerate(layouts):
            progress.set_value(i)
            QCoreApplication.processEvents()

            if progress.is_canceled():
                self.logger.warning(
                    f"Exportação cancelada pelo usuário em layout {i + 1}/{total}"
                )
                break

            nome = re.sub(r'[<>:"/\\|?*]', "", layout.name().strip())
            pdf_path = os.path.join(output_folder, f"{nome}.pdf")
            png_path = os.path.join(output_folder, f"{nome}.png")

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
                    result = exporter.exportToPdf(
                        pdf_path, QgsLayoutExporter.PdfExportSettings()
                    )
                    ok_pdf = result == QgsLayoutExporter.Success
                    if ok_pdf:
                        pdf_list.append(pdf_path)
                        self.logger.debug(f"PDF exportado: {pdf_path}")
                    else:
                        erros.append(f"{STR.FAILED_EXPORT_PDF} {nome}")

                if export_png:
                    result = exporter.exportToImage(
                        png_path, QgsLayoutExporter.ImageExportSettings()
                    )
                    ok_png = result == QgsLayoutExporter.Success
                    if ok_png:
                        png_list.append(png_path)
                        self.logger.debug(f"PNG exportado: {png_path}")
                    else:
                        erros.append(f"{STR.FAILED_EXPORT_PNG} {nome}")

                if ok_pdf or ok_png:
                    sucesso += 1

            except Exception as e:
                erro_msg = f"{STR.ERROR_EXPORTING} {nome}: {str(e)}"
                self.logger.error(erro_msg)
                erros.append(erro_msg)

        self.logger.info(
            f"Loop de exportação concluído: {sucesso}/{total} layouts processados com sucesso"
        )

        progress.set_value(total)
        progress.close()

        merge_pdf_success = False
        if merge_pdf and pdf_list:
            self.logger.debug(f"Unindo {len(pdf_list)} PDFs")
            ok, msg_text = PDFUtils.merge_pdfs(
                pdf_list, os.path.join(output_folder, "_PDF_UNICO_FINAL.pdf")
            )
            if ok:
                self.logger.info(f"PDFs unidos com sucesso: {msg_text}")
                merge_pdf_success = True
            else:
                self.logger.warning(f"Falha ao unir PDFs: {msg_text}")
                erros.append(f"{STR.FAILED_MERGE_PDFS} {msg_text}")

        merge_png_success = False
        if merge_png and png_list:
            self.logger.info(
                f"Iniciando merge de {len(png_list)} PNGs em PDF (max_width={max_width}px)"
            )
            ok, msg_text = PDFUtils.merge_pngs_to_pdf(
                png_list,
                os.path.join(output_folder, "_PNG_MERGED_FINAL.pdf"),
                max_width,
            )
            if ok:
                self.logger.info(f"PNGs unidos com sucesso: {msg_text}")
                merge_png_success = True
            else:
                self.logger.warning(f"Falha ao unir PNGs: {msg_text}")
                erros.append(f"{STR.FAILED_MERGE_PNGS} {msg_text}")

        texto = ""
        if erros:
            texto += f"<b>{STR.ERRORS_FOUND}</b><br>" + "<br>".join(erros) + "<br><br>"

        sucesso_text = f"<b>{sucesso}</b> {STR.LAYOUTS_EXPORTED_SUCCESS}"
        if merge_pdf_success:
            sucesso_text += f"<br><b>{STR.PDFS_MERGED}</b> em _PDF_UNICO_FINAL.pdf"
        if merge_png_success:
            sucesso_text += f"<br><b>{STR.PNGS_MERGED}</b> em _PNG_MERGED_FINAL.pdf"

        texto += sucesso_text

        try:
            QgisMessageUtil.modal_result_with_folder(
                self.iface,
                STR.EXPORT_LAYOUTS_COMPLETED,
                texto,
                output_folder,
                parent=self,
            )
        except Exception as modal_error:
            self.logger.error(
                f"Erro ao exibir diálogo de resultado: {str(modal_error)}"
            )
            raise


def run(iface):
    """Função de entrada do plugin."""
    dlg = ExportAllLayoutsDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
