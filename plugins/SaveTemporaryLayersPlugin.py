# -*- coding: utf-8 -*-
"""
Salvar Temporárias — Salva camadas temporárias (memory) do projeto QGIS
em arquivos permanentes no disco.

UI:
  - InputFieldsWidget: prefixo + sufixo
  - DropdownSelectorWidget: extensões vetor (shp, gpkg, geojson, ...)
  - DropdownSelectorWidget: extensões raster (tif, jp2, png, ...)
  - Output folder

  Vetores salvos em <output>/vectors/
  Rasters salvos em <output>/rasters/
"""

import os
from pathlib import Path
from qgis.core import (
    QgsRasterFileWriter,
    QgsRasterLayer,
    QgsVectorLayer,
)
from ..plugins.BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..i18n.TranslationManager import STR
from ..utils.ToolKeys import ToolKey
from ..utils.Preferences import Preferences
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.vector.VectorLayerSource import VectorLayerSource
from ..utils.ExplorerUtils import ExplorerUtils


class SaveTemporaryLayersPlugin(BasePluginMTL):
    """
    Ferramenta para salvar camadas temporárias (memory) do projeto QGIS
    em arquivos permanentes no disco.
    """

    VECTOR_EXTENSIONS = {
        ".gpkg": "GeoPackage (.gpkg)",
        ".shp": "Shapefile (.shp)",
        ".geojson": "GeoJSON (.geojson)",
        ".kml": "KML (.kml)",
        ".dxf": "DXF (.dxf)",
        ".gml": "GML (.gml)",
        ".csv": "CSV (.csv)",
    }

    RASTER_EXTENSIONS = {
        ".tif": "TIFF (.tif)",
        ".jp2": "JPEG 2000 (.jp2)",
        ".png": "PNG (.png)",
        ".jpg": "JPEG (.jpg)",
    }

    VECTOR_SUBFOLDER = "vectors"
    RASTER_SUBFOLDER = "rasters"

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(ToolKey.SAVE_TEMPORARY_LAYER, "SaveTemporaryLayersPlugin")

    def _build_ui(self, **kwargs):
        self.logger.debug("Inicializando PLUGIN SaveTemporaryLayersPlugin")
        super()._build_ui(
            title=STR.SAVE_TEMPORARY_LAYER_TITLE,
            icon_path="save_temporary_layer.ico",
            enable_scroll=True,
        )
        self.logger.info("Construindo interface da ferramenta")

        # ── Prefixo e Sufixo (InputFieldsWidget) ──
        fields_dict = {
            "prefix": {
                "title": f"{STR.PREFIX}:",
                "type": "text",
                "default": "",
                "description": "Prefixo adicionado ao nome dos arquivos de saída",
            },
            "suffix": {
                "title": f"{STR.SUFFIX}:",
                "type": "text",
                "default": "",
                "description": "Sufixo adicionado ao nome dos arquivos de saída",
            },
        }
        fields_layout, self.fields_widget = (
            WidgetFactory.create_input_fields_widget(
                fields_dict=fields_dict,
                parent=self,
                separator_bottom=True,
            )
        )

        # ── Extensão Vetor (DropdownSelectorWidget) ──
        vector_ext_layout, self.vector_ext_selector = (
            WidgetFactory.create_dropdown_selector(
                title=f"{STR.VECTOR_EXTENSIONS}:",
                options_dict=self.VECTOR_EXTENSIONS,
                selected_key=".gpkg",
                parent=self,
                separator_bottom=True,
            )
        )

        # ── Extensão Raster (DropdownSelectorWidget) ──
        raster_ext_layout, self.raster_ext_selector = (
            WidgetFactory.create_dropdown_selector(
                title=f"{STR.RASTER_EXTENSIONS}:",
                options_dict=self.RASTER_EXTENSIONS,
                selected_key=".tif",
                parent=self,
                separator_bottom=True,
            )
        )

        # ── Pasta de saída com 📁 🛠️ ➡️ (GridComplexSelector via WidgetFactory) ──
        output_layout, self.output_grid = (
            WidgetFactory.create_grid_complex_selector(
                specs={
                    "output": {
                        "label_text": f"{STR.OUTPUT_FOLDER}:",
                        "placeholder": "Selecione a pasta de saída...",
                        "allow_file": False,
                        "allow_folder": True,
                        "selection_mode": "folder",
                        "show_suggest_button": True,
                        "show_explorer_button": True,
                        "show_suggest_button": True,
                        "mode_type": "output",
                    },
                },
                parent=self,
                separator_bottom=True,
            )
        )
        self.output_selector = self.output_grid["output"]
        self.output_path = self.output_selector.edit  # compatibilidade

        # ── Botões de ação ──
        buttons_layout, self.action_buttons = (
            WidgetFactory.create_bottom_action_buttons(
                parent=self,
                run_callback=self.execute_tool,
                close_callback=self.close,
                info_callback=self.show_info_dialog,
                tool_key=self.TOOL_KEY,
                run_text=STR.SAVE,
            )
        )

        self.layout.add_items(
            [
                fields_layout,
                vector_ext_layout,
                raster_ext_layout,
                output_layout,
                buttons_layout,
            ]
        )
        self.logger.info("Interface da ferramenta construída com sucesso")

    def _load_prefs(self):
        """Carrega preferências salvas."""
        self.logger.debug("Carregando preferências")
        prefix = self.preferences.get("prefix", "")
        suffix = self.preferences.get("suffix", "")
        self.fields_widget.set_values({"prefix": prefix, "suffix": suffix})

        vector_ext = self.preferences.get("vector_extension", ".gpkg")
        self.vector_ext_selector.set_selected_key(vector_ext)

        raster_ext = self.preferences.get("raster_extension", ".tif")
        self.raster_ext_selector.set_selected_key(raster_ext)

        output_path = self.preferences.get("output_path", "")
        if output_path:
            self.output_path.setText(output_path)

    def _save_prefs(self):
        """Salva preferências."""
        self.logger.debug("Salvando preferências")
        values = self.fields_widget.get_values()
        self.preferences["prefix"] = values.get("prefix", "")
        self.preferences["suffix"] = values.get("suffix", "")
        self.preferences["vector_extension"] = (
            self.vector_ext_selector.get_selected_key()
        )
        self.preferences["raster_extension"] = (
            self.raster_ext_selector.get_selected_key()
        )
        self.preferences["output_path"] = self.output_path.text()
        self.preferences["window_width"] = self.width()
        self.preferences["window_height"] = self.height()
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)

    def _get_temporary_layers(self):
        """
        Retorna as camadas temporárias do projeto QGIS atual.

        Inclui:
        1. Camadas memory (providerType == "memory")
        2. Camadas cujo arquivo fonte está em diretório temporário
           (ex: processing_...\\OUTPUT.tif)

        Returns:
            tuple: (vector_layers, raster_layers)
                vector_layers: list de (nome, QgsMapLayer)
                raster_layers: list de (nome, QgsMapLayer)
        """
        vector_layers = []
        raster_layers = []

        project = ProjectUtils.get_project_instance()
        if not project:
            self.logger.warning("Nenhum projeto QGIS aberto")
            return [], []

        # 1. Camadas memory (providerType == "memory")
        memory_layers = ProjectUtils.get_temporary_layers(
            project=project,
            provider_name="memory",
            logger=self.logger,
        )

        # 2. Camadas com arquivo em diretório temp
        temp_file_layers = ProjectUtils.get_temp_file_layers(
            project=project,
            allow_temp_dir=True,
            logger=self.logger,
        )

        # Combinar (evitando duplicatas pelo layer.id())
        seen_ids = set()
        all_temp = []
        for ldat in memory_layers + temp_file_layers:
            if ldat.id() not in seen_ids:
                seen_ids.add(ldat.id())
                all_temp.append(ldat)

        self.logger.debug(
            f"_get_temporary_layers: memory={len(memory_layers)}, "
            f"temp_file={len(temp_file_layers)}, "
            f"total_unicas={len(all_temp)}"
        )

        for layer in all_temp:
            self.logger.debug(
                f"Processando camada temporária: name='{layer.name()}', "
                f"type(QgsVectorLayer)={isinstance(layer, QgsVectorLayer)}, "
                f"type(QgsRasterLayer)={isinstance(layer, QgsRasterLayer)}, "
                f"providerType()='{layer.providerType()}', "
                f"source='{layer.source()}'"
            )

            if isinstance(layer, QgsVectorLayer):
                vector_layers.append((layer.name(), layer))
            elif isinstance(layer, QgsRasterLayer):
                raster_layers.append((layer.name(), layer))
            else:
                self.logger.warning(
                    f"Camada temporária ignorada por tipo desconhecido: "
                    f"name='{layer.name()}', type={type(layer).__name__}"
                )

        self.logger.info(
            f"Camadas temporárias encontradas: {len(vector_layers)} vetor(es), "
            f"{len(raster_layers)} raster(s)"
        )
        return vector_layers, raster_layers

    def execute_tool(self):
        """Salva camadas temporárias em arquivos permanentes."""
        self.logger.info("Iniciando salvamento de camadas temporárias")

        # Resolver pasta de saída
        output_root = self.output_path.text().strip()

        if not output_root:
            # Tentar usar pasta do projeto
            project = ProjectUtils.get_project_instance()
            project_path = ProjectUtils.get_project_dir(project)
            if project_path:
                output_root = project_path
                if ExplorerUtils.is_file(project_path):
                    output_root = ExplorerUtils.resolve_initial_dir(project_path)
                self.logger.info(f"Usando pasta do projeto: {output_root}")
            else:
                self.logger.warning(
                    "Nenhuma pasta de saída selecionada e nenhum projeto salvo")
                QgisMessageUtil.bar_warning(
                    self.iface,
                    "Selecione uma pasta de saída ou salve o projeto primeiro.",
                )
                return

        # Garantir pastas via ExplorerUtils
        if not ExplorerUtils.ensure_folder_exists(output_root, tool_key=self.TOOL_KEY):
            self.logger.error(f"Erro ao criar pasta de saída: {output_root}")
            return

        vectors_dir = Path(output_root) / self.VECTOR_SUBFOLDER
        rasters_dir = Path(output_root) / self.RASTER_SUBFOLDER

        if not ExplorerUtils.ensure_folder_exists(str(vectors_dir), tool_key=self.TOOL_KEY):
            self.logger.error(f"Erro ao criar subpasta vectors: {vectors_dir}")
            return

        if not ExplorerUtils.ensure_folder_exists(str(rasters_dir), tool_key=self.TOOL_KEY):
            self.logger.error(f"Erro ao criar subpasta rasters: {rasters_dir}")
            return

        vectors_dir_str = str(vectors_dir)
        rasters_dir_str = str(rasters_dir)

        # Obter valores
        values = self.fields_widget.get_values()
        prefix = values.get("prefix", "")
        suffix = values.get("suffix", "")
        vector_ext = self.vector_ext_selector.get_selected_key() or ".gpkg"
        raster_ext = self.raster_ext_selector.get_selected_key() or ".tif"

        if not vector_ext.startswith("."):
            vector_ext = f".{vector_ext}"
        if not raster_ext.startswith("."):
            raster_ext = f".{raster_ext}"

        self.logger.info(
            f"Parâmetros: prefix='{prefix}', suffix='{suffix}', "
            f"vector_ext='{vector_ext}', raster_ext='{raster_ext}', "
            f"output='{output_root}'"
        )

        vector_layers, raster_layers = self._get_temporary_layers()

        if not vector_layers and not raster_layers:
            self.logger.info(
                "Nenhuma camada temporária encontrada para salvar")
            QgisMessageUtil.bar_info(
                self.iface,
                "Nenhuma camada temporária encontrada no projeto.",
            )
            return

        saved_count = 0
        errors = []

        self.logger.info(
            "Iniciando substituição de camadas temporárias por permanentes")

        for layer_name, layer in vector_layers:
            filename = f"{prefix}{layer_name}{suffix}{vector_ext}"
            filepath = ExplorerUtils.get_unique_filepath(
                str(Path(vectors_dir_str) / filename),
                tool_key=self.TOOL_KEY,
            )
            try:
                # ── Sair do modo edição se necessário ──
                if layer.isEditable():
                    if layer.isModified():
                        msg = f"A camada '{layer_name}' tem alterações não salvas. Salvar antes de continuar?"
                        if QgisMessageUtil.confirm(self.iface, msg, "Alterações encontradas"):
                            layer.commitChanges()
                            self.logger.info(
                                f"Alterações salvas para camada '{layer_name}'")
                        else:
                            layer.rollBack()
                            self.logger.info(
                                f"Alterações descartadas para camada '{layer_name}'")
                    else:
                        layer.commitChanges()
                        self.logger.debug(
                            f"Camada '{layer_name}' saiu do modo edição sem alterações")

                # ── Salvar arquivo no disco via VectorLayerSource ──
                saved_layer = VectorLayerSource.save_and_load_layer(
                    layer,
                    output_path=filepath,
                    tool_key=self.TOOL_KEY,
                    decision="overwrite",
                )

                if saved_layer is None:
                    error_msg_text = f"Erro ao salvar vetor '{layer_name}'"
                    self.logger.error(error_msg_text)
                    errors.append(error_msg_text)
                    continue

                self.logger.info(f"Vetor salvo: {filepath}")

                # ── Substituir camada temporária pela permanente ──
                self._replace_memory_layer(layer, filepath, layer_name)
                saved_count += 1

            except Exception as e:
                err_msg = f"Exceção ao salvar vetor '{layer_name}': {e}"
                self.logger.error(err_msg)
                errors.append(err_msg)

        for layer_name, layer in raster_layers:
            filename = f"{prefix}{layer_name}{suffix}{raster_ext}"
            filepath = ExplorerUtils.get_unique_filepath(
                str(Path(rasters_dir_str) / filename),
                tool_key=self.TOOL_KEY,
            )
            try:
                # ── Sair do modo edição se necessário ──
                if layer.isEditable():
                    if layer.isModified():
                        msg = f"A camada raster '{layer_name}' tem alterações não salvas. Salvar antes de continuar?"
                        if QgisMessageUtil.confirm(self.iface, msg, "Alterações encontradas"):
                            layer.commitChanges()
                            self.logger.info(
                                f"Alterações salvas para camada raster '{layer_name}'")
                        else:
                            layer.rollBack()
                            self.logger.info(
                                f"Alterações descartadas para camada raster '{layer_name}'")
                    else:
                        layer.commitChanges()

                # ── Verificar se é camada com arquivo real (temp file) ──
                # Se a camada tem um source com arquivo existente em disco, copiamos direto
                layer_source = layer.source() or ""
                source_file = layer_source.split("|")[0]
                source_path = Path(source_file)

                if source_path.exists() and source_path.is_file():
                    # Camada com arquivo real → copiar para o destino via ExplorerUtils
                    if not ExplorerUtils.copy_file(
                        str(source_path),
                        filepath,
                        tool_key=self.TOOL_KEY,
                    ):
                        err_msg = f"Erro ao copiar raster '{layer_name}'"
                        self.logger.error(err_msg)
                        errors.append(err_msg)
                        continue

                    self.logger.info(f"Raster copiado: {filepath}")
                else:
                    # Camada sem arquivo real (memory raster) → usar writeRasterFile
                    file_writer = QgsRasterFileWriter(filepath)
                    write_result = file_writer.writeRasterLayer(
                        layer,
                        layer.extent(),
                        layer.crs(),
                        ProjectUtils.get_project_instance().transformContext(),
                    )

                    if write_result != 0:
                        err_msg = f"Erro ao salvar raster '{layer_name}': código {write_result}"
                        self.logger.error(err_msg)
                        errors.append(err_msg)
                        continue

                    self.logger.info(f"Raster salvo: {filepath}")

                # ── Substituir camada temporária pela permanente ──
                self._replace_raster_layer(layer, filepath, layer_name)
                saved_count += 1

            except AttributeError as e:
                # Fallback: writeRasterLayer não existe → copiar arquivo se existir
                err_msg = f"Erro de API ao salvar raster '{layer_name}': {e}"
                self.logger.error(err_msg)
                errors.append(err_msg)
            except Exception as e:
                err_msg = f"Exceção ao salvar raster '{layer_name}': {e}"
                self.logger.error(err_msg)
                errors.append(err_msg)

        if errors:
            msg = (
                f"Salvas: {saved_count} camada(s). "
                f"Erros: {len(errors)}. "
                f"Vetores em: {vectors_dir_str}, Rasters em: {rasters_dir_str}"
            )
            self.logger.warning(msg)
            QgisMessageUtil.bar_warning(self.iface, msg)
        else:
            msg = (
                f"{saved_count} camada(s) temporária(s) salva(s) com sucesso! "
                f"Vetores em: {vectors_dir_str}, Rasters em: {rasters_dir_str}"
            )
            self.logger.info(msg)
            QgisMessageUtil.bar_info(self.iface, msg)

    def _replace_memory_layer(self, old_layer, filepath, layer_name):
        """Remove a camada memory e carrega a salva no mesmo lugar, com mesmo estilo."""
        try:
            project = ProjectUtils.get_project_instance()
            root = project.layerTreeRoot()

            # Capturar grupo pai, índice e estilo antes de remover
            old_node = root.findLayer(old_layer.id())
            parent_group = None
            insert_index = -1
            renderer = None
            if old_node:
                parent_group = old_node.parent()
                if parent_group:
                    insert_index = parent_group.children().index(old_node)
                renderer = old_layer.renderer() if old_layer.renderer() else None

            self.logger.debug(
                f"_replace_memory_layer: name='{layer_name}', "
                f"parent='{parent_group.name() if parent_group else 'root'}', "
                f"index={insert_index}, has_renderer={renderer is not None}"
            )

            # Criar nova camada a partir do arquivo salvo
            uri = filepath.replace("\\", "/")
            new_layer = QgsVectorLayer(uri, layer_name, "ogr")

            if not new_layer or not new_layer.isValid():
                self.logger.error(
                    f"Não foi possível carregar a camada salva: {filepath}"
                )
                return False

            # Aplicar estilo original (renderer) se existir
            if renderer:
                new_layer.setRenderer(renderer.clone())

            # Remover camada memory do projeto
            ProjectUtils.remove_layer_from_project(old_layer)

            # Adicionar nova camada sem inserir na root
            ProjectUtils.add_layer(new_layer, add_to_root=False, project=project)

            # Inserir no mesmo grupo/posição
            if parent_group:
                if insert_index >= 0:
                    parent_group.insertLayer(insert_index, new_layer)
                else:
                    parent_group.addLayer(new_layer)
            else:
                root.insertLayer(0, new_layer)

            self.logger.info(
                f"Camada '{layer_name}' substituída com sucesso: {filepath}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao substituir camada '{layer_name}': {e}"
            )
            return False

    def _replace_raster_layer(self, old_layer, filepath, layer_name):
        """Remove a camada raster temporária e carrega a salva no mesmo lugar,
        preservando o estilo (renderer) original."""
        try:
            project = ProjectUtils.get_project_instance()
            root = project.layerTreeRoot()

            # Capturar grupo pai e índice
            old_node = root.findLayer(old_layer.id())
            parent_group = None
            insert_index = -1
            if old_node:
                parent_group = old_node.parent()
                if parent_group:
                    insert_index = parent_group.children().index(old_node)

            # ── Salvar estilo original como QML temporário via ExplorerUtils ──
            qml_temp = None
            try:
                fd, qml_temp = ExplorerUtils.create_temp_file(
                    suffix=".qml", prefix="raster_style_", tool_key=self.TOOL_KEY
                )
                if fd is not None:
                    os.close(fd)
                    style_saved = old_layer.saveNamedStyle(qml_temp)
                    if style_saved[0]:
                        self.logger.debug(
                            f"Estilo raster salvo em QML temporário: {qml_temp}"
                        )
                    else:
                        self.logger.debug(
                            f"Não foi possível salvar estilo do raster: {style_saved[1]}"
                        )
                        ExplorerUtils.delete_file(qml_temp, ignore_errors=True)
                        qml_temp = None
                else:
                    qml_temp = None
            except Exception as e:
                self.logger.debug(f"Erro ao salvar estilo QML temporário: {e}")
                if qml_temp:
                    ExplorerUtils.delete_file(qml_temp, ignore_errors=True)
                qml_temp = None

            self.logger.debug(
                f"_replace_raster_layer: name='{layer_name}', "
                f"parent='{parent_group.name() if parent_group else 'root'}', "
                f"index={insert_index}, has_style={qml_temp is not None}"
            )

            # Criar nova camada raster a partir do arquivo salvo
            uri = filepath.replace("\\", "/")
            new_layer = QgsRasterLayer(uri, layer_name)

            if not new_layer or not new_layer.isValid():
                self.logger.error(
                    f"Não foi possível carregar o raster salvo: {filepath}"
                )
                # Limpar QML temporário
                if qml_temp:
                    ExplorerUtils.delete_file(qml_temp, ignore_errors=True)
                return False

            # ── Aplicar estilo original se existir ──
            if qml_temp:
                try:
                    style_ok = new_layer.loadNamedStyle(qml_temp)
                    if style_ok:
                        new_layer.triggerRepaint()
                        self.logger.debug(
                            f"Estilo aplicado ao novo raster: {qml_temp}"
                        )
                    else:
                        self.logger.debug(
                            "loadNamedStyle retornou False para o raster"
                        )
                except Exception as e:
                    self.logger.debug(f"Erro ao aplicar estilo: {e}")
                finally:
                    ExplorerUtils.delete_file(qml_temp, ignore_errors=True)

            # Remover camada temporária do projeto
            ProjectUtils.remove_layer_from_project(old_layer)

            # Adicionar nova camada sem inserir na root
            ProjectUtils.add_layer(new_layer, add_to_root=False, project=project)

            # Inserir no mesmo grupo/posição
            if parent_group:
                if insert_index >= 0:
                    parent_group.insertLayer(insert_index, new_layer)
                else:
                    parent_group.addLayer(new_layer)
            else:
                root.insertLayer(0, new_layer)

            self.logger.info(
                f"Camada raster '{layer_name}' substituída com sucesso: {filepath}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Erro ao substituir raster '{layer_name}': {e}"
            )
            return False


def run(iface):
    dlg = SaveTemporaryLayersPlugin(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
