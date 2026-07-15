# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

from ..core.ui.dialogs.DefaultProjectsFolderDialog import DefaultProjectsFolderDialog
from ..core.ui.dialogs.ProjectNameDialog import ProjectNameDialog
from ..i18n.TranslationManager import STR
from ..plugins.BasePlugin import BasePluginMTL
from ..resources.OtherFilesManager import OtherFilesManager
from ..utils.ExplorerUtils import ExplorerUtils
from ..utils.Preferences import Preferences
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.raster.RasterLayerSource import RasterLayerSource
from ..utils.ToolKeys import ToolKey
from ..utils.vector.VectorLayerSource import VectorLayerSource


class CreateProjectPlugin(BasePluginMTL):
    DEFAULT_PROJECTS_FOLDER = "C:/QgisProjects"
    PROJECTS_FOLDER_PREF_KEY = "projects_folder"
    TOOL_KEY = ToolKey.CREATE_PROJECT
    GENERIC_PROJECT_PATTERN = re.compile(r"^NovoProjeto_(\d+)$")
    DEFAULT_CRS_AUTHID = "EPSG:4326"
    DEFAULT_CRS_PREF_KEY = "default_crs_authid"
    DEFAULT_GOOGLE_BASEMAP_STYLE = "hybrid"
    SCENARIO_UNSAVED_WITH_CONTENT = 1
    SCENARIO_SAVED_CURRENT_PROJECT = 2
    SCENARIO_UNSAVED_EMPTY_PROJECT = 3

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(
            tool_key=self.TOOL_KEY,
            class_name="CreateProjectPlugin",
            load_system_prefs=False,
            build_ui=False,
        )

    def execute(self):
        """Mantem compatibilidade com chamadas legadas."""
        return self.execute_tool()

    def execute_tool(self):
        """Executa o fluxo completo de criacao de projeto."""
        self.on_finish_plugin()
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.info("Iniciando fluxo de criacao de novo projeto")
        system_prefs = Preferences.load_tool_prefs(ToolKey.SYSTEM)
        base_folder = self._resolve_base_folder(system_prefs)
        if not base_folder:
            return

        project_name = self._resolve_project_name(base_folder)
        if not project_name:
            return

        default_crs_authid = (
            system_prefs.get(self.DEFAULT_CRS_PREF_KEY) or self.DEFAULT_CRS_AUTHID
        )
        self._create_project_structure(base_folder, project_name, default_crs_authid)

    def _resolve_base_folder(self, system_prefs: dict) -> str:
        base_folder = (system_prefs.get(self.PROJECTS_FOLDER_PREF_KEY) or "").strip()
        if base_folder:
            if self._prepare_existing_base_folder(base_folder):
                return base_folder
            return ""

        base_folder = self._prompt_and_persist_base_folder(system_prefs)
        if not base_folder:
            return ""
        if self._prepare_new_base_folder(base_folder):
            return base_folder
        return ""

    def _prompt_and_persist_base_folder(self, system_prefs: dict) -> str:
        should_define = QgisMessageUtil.confirm(
            self.iface,
            STR.PROJECTS_DEFAULT_FOLDER_MISSING,
            title=STR.PROJECTS_DEFAULT_FOLDER_MISSING_TITLE,
        )
        if not should_define:
            self.logger.info("Usuario cancelou definicao da pasta padrao")
            return ""

        folder_dialog = DefaultProjectsFolderDialog(parent=self.iface.mainWindow())
        if not folder_dialog.exec():
            self.logger.info("Usuario cancelou o dialogo da pasta padrao")
            return ""

        base_folder = folder_dialog.get_folder_path().strip()
        system_prefs[self.PROJECTS_FOLDER_PREF_KEY] = base_folder
        Preferences.save_tool_prefs(ToolKey.SYSTEM, system_prefs)
        self.logger.info(f"Pasta padrao salva nas system prefs: {base_folder}")
        return base_folder

    def _prepare_new_base_folder(self, base_folder: str) -> bool:
        if ExplorerUtils.ensure_folder_exists(base_folder, self.TOOL_KEY):
            return True

        QgisMessageUtil.modal_error(
            self.iface,
            f"{STR.PROJECT_DEFAULT_FOLDER_PREPARE_ERROR}\n{base_folder}",
        )
        return False

    def _prepare_existing_base_folder(self, base_folder: str) -> bool:
        if ExplorerUtils.ensure_folder_exists(base_folder, self.TOOL_KEY):
            return True

        QgisMessageUtil.modal_error(
            self.iface,
            f"{STR.PROJECT_DEFAULT_FOLDER_ACCESS_ERROR}\n{base_folder}",
        )
        return False

    def _resolve_project_name(self, base_folder: str) -> str:
        suggested_name = ExplorerUtils.next_indexed_folder_name(
            base_folder=base_folder,
            prefix="NovoProjeto_",
            pattern=self.GENERIC_PROJECT_PATTERN,
        )
        name_dialog = ProjectNameDialog(
            suggested_name=suggested_name, parent=self.iface.mainWindow()
        )
        if not name_dialog.exec():
            self.logger.info("Usuario cancelou o dialogo de nome do projeto")
            return ""

        project_name = ExplorerUtils.sanitize_path_component(
            name_dialog.get_project_name()
        )
        return project_name or suggested_name

    def _detect_creation_scenario(self, current_project) -> int:
        if ProjectUtils.is_project_saved(current_project):
            return self.SCENARIO_SAVED_CURRENT_PROJECT
        if not ProjectUtils.is_project_empty(current_project):
            return self.SCENARIO_UNSAVED_WITH_CONTENT
        return self.SCENARIO_UNSAVED_EMPTY_PROJECT

    def _should_load_line_for_scenario(self, scenario: int) -> bool:
        return scenario in (
            self.SCENARIO_SAVED_CURRENT_PROJECT,
            self.SCENARIO_UNSAVED_EMPTY_PROJECT,
        )

    def _copy_and_load_line_reference_layer(
        self, project, project_vectors_folder: Path
    ):
        line_path = OtherFilesManager.vector_path(OtherFilesManager.LINE_VECTOR)
        if not os.path.exists(line_path):
            self.logger.warning(
                f"Arquivo de referencia nao encontrado para carga automatica: {line_path}"
            )
            return None, ""

        copied_line_path = ExplorerUtils.copy_file_to_folder(
            source_file=line_path,
            destination_folder=str(project_vectors_folder),
            tool_key=self.TOOL_KEY,
            overwrite=True,
        )
        if not copied_line_path:
            self.logger.warning(
                f"Falha ao copiar line.gpkg para pasta do projeto: {project_vectors_folder}"
            )
            return None, ""

        normalized_target = ProjectUtils.normalize_layer_source(copied_line_path)
        for layer in ProjectUtils.project_layers(project).values():
            source_normalized = ProjectUtils.normalize_layer_source(layer.source())
            if source_normalized == normalized_target:
                self.logger.debug(
                    f"Camada de referencia ja carregada no projeto: {copied_line_path}"
                )
                if layer and hasattr(layer, "isValid") and layer.isValid():
                    return layer, copied_line_path
                return None, copied_line_path

        line_layer = VectorLayerSource.load_existing_vector_layer(
            copied_line_path, tool_key=self.TOOL_KEY
        )
        if not line_layer or not line_layer.isValid():
            self.logger.warning(
                f"Falha ao carregar camada de referencia line.gpkg copiada: {copied_line_path}"
            )
            return None, copied_line_path

        ProjectUtils.add_layer(line_layer, add_to_root=True, project=project)
        self.logger.info(
            f"Camada de referencia carregada a partir da copia: {copied_line_path}"
        )
        return line_layer, copied_line_path

    def _apply_project_crs(self, project, authid: str):
        crs = ProjectUtils.resolve_valid_crs(
            authid=authid,
            fallback_authid=self.DEFAULT_CRS_AUTHID,
            tool_key=self.TOOL_KEY,
        )
        ProjectUtils.set_project_crs(project, crs)
        self.logger.info(f"SRC aplicado ao projeto: {crs.authid()}")

    def _create_project_structure(
        self, base_folder: str, project_name: str, default_crs_authid: str
    ):
        project_folder = Path(base_folder) / project_name
        project_file = project_folder / f"{project_name}.qgz"
        vectors_folder = project_folder / "vectors"
        rasters_folder = project_folder / "rasters"
        current_project = ProjectUtils.get_project_instance()
        current_project_path = ProjectUtils.get_project_file_name(current_project)
        scenario = self._detect_creation_scenario(current_project)
        should_load_line = self._should_load_line_for_scenario(scenario)

        if project_folder.exists():
            self.logger.warning(f"Pasta de projeto ja existe: {project_folder}")
            should_continue = QgisMessageUtil.confirm(
                self.iface,
                f"{STR.PROJECT_FOLDER_ALREADY_EXISTS}\n{project_folder}\n\n{STR.CONTINUE_ANYWAY}",
                title=STR.PROJECT_FOLDER_ALREADY_EXISTS,
            )
            if not should_continue:
                self.logger.info("Usuario cancelou criacao do projeto existente")
                return

        try:
            if not ExplorerUtils.ensure_folder_exists(
                str(vectors_folder), self.TOOL_KEY
            ):
                raise RuntimeError("Falha ao criar pasta vectors")
            if not ExplorerUtils.ensure_folder_exists(
                str(rasters_folder), self.TOOL_KEY
            ):
                raise RuntimeError("Falha ao criar pasta rasters")
        except Exception as e:
            self.logger.error(
                f"Erro ao criar estrutura de pastas para '{project_folder}': {e}"
            )
            QgisMessageUtil.modal_error(
                self.iface,
                f"{STR.PROJECT_FOLDER_CREATE_ERROR}\n{project_folder}\n\n{e}",
            )
            return

        try:
            if not current_project_path:
                self._apply_project_crs(current_project, default_crs_authid)
                RasterLayerSource().add_google_basemap(
                    current_project,
                    basemap_style=self.DEFAULT_GOOGLE_BASEMAP_STYLE,
                    external_tool_key=self.TOOL_KEY,
                )
                line_layer = None
                line_path_in_project = ""
                if should_load_line:
                    line_layer, line_path_in_project = (
                        self._copy_and_load_line_reference_layer(
                            current_project, vectors_folder
                        )
                    )
                    if line_layer:
                        ProjectUtils.center_canvas_on_file_extent(
                            iface=self.iface,
                            file_path=line_path_in_project,
                            project=current_project,
                            layer_name=line_layer.name(),
                            tool_key=self.TOOL_KEY,
                        )
                ProjectUtils.set_project_home_path(current_project, str(project_folder))
                ProjectUtils.set_project_file_name(current_project, str(project_file))

                if not ProjectUtils.write_project(current_project, str(project_file)):
                    raise RuntimeError(
                        STR.CURRENT_PROJECT_SAVE_TO_NEW_DESTINATION_ERROR
                    )

                self.logger.info(f"Projeto atual sem arquivo salvo em: {project_file}")
            else:
                new_project = ProjectUtils.create_project_instance()
                self._apply_project_crs(new_project, default_crs_authid)
                RasterLayerSource().add_google_basemap(
                    new_project,
                    basemap_style=self.DEFAULT_GOOGLE_BASEMAP_STYLE,
                    external_tool_key=self.TOOL_KEY,
                )
                line_layer = None
                if should_load_line:
                    line_layer, _ = self._copy_and_load_line_reference_layer(
                        new_project, vectors_folder
                    )
                ProjectUtils.set_project_home_path(new_project, str(project_folder))
                ProjectUtils.set_project_file_name(new_project, str(project_file))

                if not ProjectUtils.write_project(new_project, str(project_file)):
                    raise RuntimeError(STR.NEW_PROJECT_FILE_WRITE_ERROR)

                line_extent = None
                if line_layer and line_layer.isValid():
                    layer_extent = line_layer.extent()
                    if not layer_extent.isEmpty():
                        line_extent = (
                            layer_extent.xMinimum(),
                            layer_extent.yMinimum(),
                            layer_extent.xMaximum(),
                            layer_extent.yMaximum(),
                        )

                if not ProjectUtils.open_project_in_new_window(
                    str(project_file), line_extent
                ):
                    raise RuntimeError(STR.OPEN_NEW_QGIS_WINDOW_ERROR)
        except Exception as e:
            self.logger.error(f"Erro ao criar projeto QGIS '{project_file}': {e}")
            QgisMessageUtil.modal_error(
                self.iface,
                f"{STR.PROJECT_FILE_CREATE_ERROR}\n{project_file}\n\n{e}",
            )
            return

        self.logger.info(f"Projeto criado com sucesso em: {project_folder}")
        QgisMessageUtil.modal_result_with_folder(
            self.iface,
            title=STR.PROJECT_CREATED_TITLE,
            message=(
                STR.PROJECT_CREATED_SUCCESS.format(project_name=project_name)
                if not current_project_path
                else STR.PROJECT_CREATED_OPENED_NEW_WINDOW.format(
                    project_name=project_name
                )
            ),
            folder_path=str(project_folder),
            parent=self.iface.mainWindow(),
        )


def run(iface):
    """Ponto de entrada do plugin instantaneo de criacao de projeto."""
    plugin = CreateProjectPlugin(iface)
    plugin.execute_tool()
    return plugin
