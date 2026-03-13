# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path
from datetime import datetime
import shutil

from qgis.core import (
    QgsProject,
)

from ..plugins.BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..utils.Preferences import (
    load_tool_prefs,
    save_tool_prefs,
)
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ExplorerUtils import ExplorerUtils
from ..utils.ProjectUtils import ProjectUtils
from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.LoadFilesStep import LoadFilesStep
from ..core.engine_tasks.ExecutionContext import ExecutionContext



# ============================================================
#  ** Janela Principal da Ferramenta **
# ============================================================

class LoadFolderLayersDialog(BasePluginMTL):

    TOOL_KEY = "load_folder_layers"
    ASYNC_THRESHOLD = 19

    FILE_TYPES = {
        "GeoPackage (*.gpkg)": (".gpkg",),
        "Shapefile (*.shp)": (".shp",),
        "GeoJSON (*.geojson *.json)": (".geojson", ".json"),
        "KML (*.kml)": (".kml",),
        "KMZ (*.kmz)": (".kmz",),
        "TIFF/GeoTIFF (*.tif *.tiff)": (".tif", ".tiff"),
        "ECW (*.ecw)": (".ecw",),
        "JPEG2000 (*.jp2)": (".jp2",),
        "ASCII GRID (*.asc)": (".asc",),
        "GPX (*.gpx)": (".gpx",),
        "CSV (*.csv)": (".csv",),
        "MapInfo TAB (*.tab)": (".tab",),
        "LAS/LAZ (*.las *.laz)": (".las", ".laz"),
    }

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface

        # Inicializar via BasePluginMTL
        self.init(
            self.TOOL_KEY,
            "LoadFolderLayersDialog",
            load_settings_prefs=False,
            build_ui=True
        )

    def _build_ui(self, **kwargs):
        # Constrói a UI padronizada usando WidgetFactory e BasePluginMTL
        super()._build_ui(
            title="Carregar Pasta de Arquivos",
            icon_path="load_folder.ico",
            instructions_file="load_folder_layers.md",
            enable_scroll=False
        )

        # --- Tipos de arquivo dentro de seção colapsável ---
        coll_layout, self.coll_widget = WidgetFactory.create_collapsible_parameters(
            parent=self,
            title="Tipos de Arquivo",
            expanded_by_default=False,
            separator_top=False,
            separator_bottom=True,
        )

        file_options = {label: label for label in self.FILE_TYPES.keys()}
        types_layout, self.chk_types = WidgetFactory.create_checkbox_grid(
            file_options,
            items_per_row=2,
            checked_by_default=False,
            title=None,
            separator_top=False,
            separator_bottom=False,
        )

        self.coll_widget.add_content_layout(types_layout)

        # --- Seletor de pasta ---
        folder_layout, self.folder_selector = WidgetFactory.create_path_selector(
            parent=self,
            title="Pasta raiz:",
            mode="folder",
            separator_top=False,
            separator_bottom=True,
        )

        # --- Opções adicionais (1 coluna) ---
        opts = {
            "missing_only": "Carregar apenas arquivos ainda NÃO carregados no projeto",
            "preserve": "Criar grupos conforme estrutura de pastas/subpastas",
            "lastfolder": "Não agrupar a última pasta",
            "backup": "Criar backup do projeto antes de carregar (somente se salvo)",            
        }
        #cmo funciona F:\TTG\FEV_2026\FAZ_UNIAO\OLD\file.shp)
        #crie os grupo TTG  - FEV_2026 - FAZ_UNIAO - MAS NAO CARREGUE O OLD, POIS É A ULTIMA PASTA
        # MODO PRESERVE COM LASTFOLDER DESABILITADO: F:\TTG\FEV_2026\FAZ_UNIAO\OLD\file.shp -> GRUPOS: TTG  - FEV_2026 - FAZ_UNIAO - OLD
        #VEJA QUE O MODO LASTFOLDER SO FAZ SENTIDO SE O MODO PRESERVE ESTIVER HABILITADO. SE O MODO PRESERVE ESTIVER DESABILITADO, 
        # O LASTFOLDER NAO TEM EFEITO, POIS NAO SERA CRIADA NENHUMA ESTRUTURA DE GRUPOS, INDEPENDENTE DO VALOR DE LASTFOLDER
        # POR ISSO ANALISE O GRID DE CHECKBOX E TENTE IMPLEMENTAR UM SISTEMA ONDE DETERMINADO CHECK PODE INATIVAR OUTRO CHECK, 
        # COMO É O CASO DO LASTFOLDER QUE SÓ FAZ SENTIDO SE O PRESERVE ESTIVER HABILITADO. LAST FOLDER SO FICA POSSIVEL CHECKAR SE LAST FOLDER ESTIVER HABILITADO

        opts_layout, opts_map = WidgetFactory.create_checkbox_grid(
            opts,
            items_per_row=1,
            checked_by_default=False,
            title=None,
            separator_top=False,
            separator_bottom=True,
        )

        self.chk_load_missing_only = opts_map["missing_only"]
        self.chk_preserve_structure = opts_map["preserve"]
        self.chk_last_folder = opts_map["lastfolder"]
        self.chk_backup = opts_map["backup"]

        # last_folder faz sentido apenas se preserve estiver ativado
        # usa mecanismo de dependência via CheckboxGridWidget/DependentCheckBox
        try:
            self.chk_preserve_structure.set_dependents([self.chk_last_folder])
        except Exception:
            pass

        # --- Botões padrão ---
        buttons_layout, self.action_buttons = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=self.execute_tool,
            close_callback=self.close,
            info_callback=self.show_info_dialog,
            tool_key=self.TOOL_KEY,
            run_text="Carregar Arquivos",
        )

        # Adicionar tudo ao layout principal
        self.layout.add_items([
            folder_layout,
            coll_layout,
            opts_layout,
            buttons_layout,
        ])

        # Carregar preferências
        self.logger.debug("Construindo interface de usuário", code="UI_BUILD")
        self._load_prefs()


    # ------------------------------------------------------------------
    # Nota: `show_info` deste plugin foi removido. Use `show_info_dialog()` da classe-base.

    # ------------------------------------------------------------------
    # seleção de pasta é feita via WidgetFactory.create_path_selector

    # ------------------------------------------------------------------
    def _load_prefs(self):
        # Carregar preferências e repopular widgets (assume widgets criados em _build_ui)
        prefs = load_tool_prefs(self.TOOL_KEY)
        try:
            # Pasta
            folder = prefs.get("folder", "")
            if folder:
                self.folder_selector.set_paths([folder])

            # Tipos
            saved_types = prefs.get("types", [])
            for label, chk in self.chk_types.items():
                chk.setChecked(label in saved_types)
            self.coll_widget.set_expanded(prefs.get("types_expanded", False))
            # Opções
            self.chk_load_missing_only.setChecked(prefs.get("missing_only", False))
            self.chk_preserve_structure.setChecked(prefs.get("preserve", True))
            self.chk_last_folder.setChecked(prefs.get("lastfolder", False))
            self.chk_backup.setChecked(prefs.get("backup", True))

            # backup só se projeto salvo
            if not QgsProject.instance().fileName():
                self.chk_backup.setChecked(False)
                self.chk_backup.setEnabled(False)

            # Layout / janela
            w = prefs.get("window_width")
            h = prefs.get("window_height")
            if w and h:
                try:
                    self.resize(int(w), int(h))
                except Exception:
                    pass
        except Exception:
            # Mantém comportamento tolerante: não falhar ao carregar prefs
            pass

    # ------------------------------------------------------------------
    def _save_prefs(self):
        # Salva preferências de forma simples (assume widgets existem)
        try:
            selected_types = [label for label, chk in self.chk_types.items() if chk.isChecked()]
            paths = self.folder_selector.get_paths()
            folder = paths[0] if paths else ""

            data = {
                "folder": folder,
                "types": selected_types,
                "missing_only": self.chk_load_missing_only.isChecked(),
                "preserve": self.chk_preserve_structure.isChecked(),
                "lastfolder": self.chk_last_folder.isChecked(),
                "backup": self.chk_backup.isChecked(),
                "window_width": self.width(),
                "window_height": self.height(),
                "types_expanded": self.coll_widget.is_expanded(),
            }

            save_tool_prefs(self.TOOL_KEY, data)
        except Exception:
            # não falhar ao salvar preferências
            pass

    # -----------------------------------------------------------------
    # ------------------------------------------------------------------
    def execute_tool(self):

        # Pasta (usa API do path selector)
    
        paths = self.folder_selector.get_paths()
        folder = paths[0].strip() if paths else ""
        self.start_stats(folder)

        self.logger.info(f"Iniciando execução: pasta={folder}", code="EXEC_START")

        if not folder or not os.path.isdir(folder):
            QgisMessageUtil.bar_warning(self.iface, "Selecione uma pasta válida.")
            return

        backup_file = None
        if self.chk_backup.isChecked():
            try:
                backup_file = ProjectUtils.create_project_backup(QgsProject.instance())
            except Exception:
                backup_file = None

        # coletar extensões selecionadas
        extensions = []
        for label, chk in self.chk_types.items():
            if chk.isChecked():
                extensions.extend(self.FILE_TYPES.get(label, []))

        if not extensions:
            QgisMessageUtil.bar_warning(self.iface, "Selecione pelo menos um tipo de arquivo.")
            return

        # scan via ExplorerUtils
        records = ExplorerUtils.scan_folder(folder, extensions, self.TOOL_KEY)
        self.logger.info(f"scan_folder retornou {len(records)} registros", code="SCAN_COMPLETE")

        # decidir entre execução síncrona ou assíncrona baseado no número de arquivos
        total_files = len(records)
        if total_files > self.ASYNC_THRESHOLD:
            self.logger.info(f"Arquivos ({total_files}) acima do limiar ({self.ASYNC_THRESHOLD}), usando execução assíncrona", code="EXEC_STRATEGY")
            return self._run_async_pipeline(folder=folder, records=records, backup_file=backup_file)
        else:
            self.logger.info(f"Arquivos ({total_files}) dentro do limiar ({self.ASYNC_THRESHOLD}), usando execução síncrona", code="EXEC_STRATEGY")
            return self._run_sync_pipeline(folder=folder, records=records, backup_file=backup_file)


    def _run_sync_pipeline(self, folder: str, records: list, backup_file: str = None):
        """Executa o carregamento de forma síncrona (comportamento atual)."""
        project = QgsProject.instance()
        already_loaded = set()
        if self.chk_load_missing_only.isChecked():
            for layer in project.mapLayers().values():
                src = ProjectUtils.normalize_layer_source(layer.source())
                already_loaded.add(src)

        loaded_count = 0

        for rec in records:
            path = rec.get("path")
            norm = ProjectUtils.normalize_layer_source(path)
            if self.chk_load_missing_only.isChecked() and norm in already_loaded:
                continue

            layer = ExplorerUtils.create_layer(rec, self.TOOL_KEY)
            if not layer or not layer.isValid():
                continue

            if self.chk_preserve_structure.isChecked():
                rel = os.path.relpath(os.path.dirname(path), folder)

                # Se lastfolder estiver ativo, nem sempre queremos o último nível
                if self.chk_last_folder.isChecked() and rel not in (".", ""):
                    parts = rel.split(os.sep)
                    if len(parts) > 1:
                        rel = os.path.join(*parts[:-1])
                    else:
                        rel = "."

                if rel == ".":
                    ProjectUtils.add_layer(layer, add_to_root=True)
                else:
                    group = ProjectUtils.ensure_group(rel)
                    ProjectUtils.add_layer_to_group(layer, group)
            else:
                ProjectUtils.add_layer(layer, add_to_root=True)

            loaded_count += 1
            self.logger.debug(f"Layer carregada e adicionada: {path}", code="LAYER_ADDED")
        self.finish_stats()
        QgisMessageUtil.modal_info(
            self.iface,
            f"Foram carregados {loaded_count} arquivos.\n" + (f"Backup criado: {backup_file}" if backup_file else "")
        )

    def _run_async_pipeline(self, folder: str, records: list, backup_file: str = None):
        """Inicia pipeline assíncrona para carregar arquivos em background.

        A Task apenas valida/filtra registros. O Step adiciona as camadas
        no thread principal em lote (bloqueando signals do layer tree)
        para reduzir impacto na UI.
        """
        self.logger.info("_run_async_pipeline: iniciando pipeline assíncrona", code="ASYNC_START")

        ctx = ExecutionContext({
            "folder": folder,
            "records": records,
            "tool_key": self.TOOL_KEY,
            "preserve": self.chk_preserve_structure.isChecked(),
            "last_folder": self.chk_last_folder.isChecked(),
            "missing_only": self.chk_load_missing_only.isChecked(),
            "backup_file": backup_file,
            # parent widget used by Steps to show modal progress
            "parent": self,
        })

        engine = AsyncPipelineEngine(
            steps=[LoadFilesStep()],
            context=ctx,
            on_finished=self._on_async_finished,
            on_error=self._on_async_error,
        )

        try:
            engine.start()
            QgisMessageUtil.bar_info(self.iface, "Execução em background iniciada. Verifique o log para progresso.")
        except Exception as e:
            self.logger.error(f"Falha iniciando pipeline assíncrona: {e}", code="ASYNC_ERROR")
            QgisMessageUtil.bar_critical(self.iface, f"Erro iniciando execução assíncrona: {e}")
        return None

    def _on_async_finished(self, context: ExecutionContext):
        loaded = context.get("loaded_count", 0)
        backup = context.get("backup_file") or context.get("backup_file", None)
        self.finish_stats()
        self.logger.info(f"_on_async_finished: loaded={loaded}", code="ASYNC_FINISH")
        QgisMessageUtil.bar_info(self.iface, f"Execução assíncrona concluída. Foram carregados {loaded} arquivos.\n" + (f"Backup: {backup}" if backup else ""))

    def _on_async_error(self, errors):
        self.logger.error(f"_on_async_error: {errors}", code="ASYNC_ERROR")
        QgisMessageUtil.modal_error(self.iface, f"Erro na execução assíncrona: {errors}")

# Função pública
def run_load_folder_layers(iface):
    dlg = LoadFolderLayersDialog(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
