# -*- coding: utf-8 -*-
import os
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsMapLayerProxyModel
from typing import Optional, Tuple
from ..plugins.BasePlugin import BasePluginMTL
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.StringManager import StringManager
from ..utils.vector.VectorLayerGeometry import VectorLayerGeometry
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from ..utils.vector.VectorLayerSource import VectorLayerSource
from ..utils.Preferences import Preferences
from ..utils.ToolKeys import ToolKey
from ..core.ui.WidgetFactory import WidgetFactory
from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.BufferStep import BufferStep
from ..core.engine_tasks.ExecutionContext import ExecutionContext
from ..core.engine_tasks.ExplodeStep import ExplodeStep
from ..core.engine_tasks.SaveVectorStep import SaveVectorStep
from ..i18n.TranslationManager import STR


class GenerateTrailPlugin(BasePluginMTL):
    # Essa é uma ferramenta de janela com geração de produtos: do tipo vetoriais.
    # O valor inicial ainda existe como fallback caso as preferências globais
    # não sejam carregadas. O padrão atualizado é 20 MB.

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        # precisamos das preferências globais (Settings) para ler o limiar
        # assíncrono definido pelo usuário
        self.init(
            ToolKey.GENERATE_TRAIL,
            "GenerateTrailPlugin",
            load_system_prefs=True,
        )

    def _build_ui(self, **kwargs):
        self.logger.debug("Inicializando PLUGIN Gerar Rastro Implemento")
        super()._build_ui(
            title=STR.GENERATE_TRAIL_TITLE,
            icon_path="gerar_rastro.ico",
            enable_scroll=True,
        )
        self.logger.info("Construindo interface da ferramenta")

        layer_layout, self.layer_input = WidgetFactory.create_layer_input(
            label_text=STR.INPUT_LINE_LAYER,
            filters=[QgsMapLayerProxyModel.Filter.LineLayer],
            parent=self,
            allow_empty=False,
        )
        self.logger.debug("Componente de camada de entrada adicionado")

        tam_layout, self.spin_tam = WidgetFactory.create_double_spin_input(
            STR.IMPLEMENT_SIZE,
            separator_bottom=True,
        )
        self.logger.debug("Componente de tamanho de implemento adicionado")

        save_layout, self.save_selector = WidgetFactory.create_save_file_selector(
            parent=self,
            file_filter=StringManager.FILTER_VECTOR,
            path_button=os.path.join("vetores", "Rastro_implemento.gpkg"),
            separator_top=False,
        )
        self.logger.debug("Componente de salvamento de arquivo adicionado")

        adv_layout, self.adv_params = WidgetFactory.create_collapsible_parameters(
            parent=self,
            title=STR.ADVANCED_PARAMETERS,
            expanded_by_default=False,
            separator_top=False,
            separator_bottom=True,
        )
        self.logger.debug("Widget de parâmetros avançados criado")

        qml_layout, self.qml_selector = WidgetFactory.create_qml_selector(
            parent=self, separator_top=False, separator_bottom=False
        )
        self.adv_params.add_content_layout(qml_layout)
        self.logger.debug(
            "Componente de estilo QML adicionado dentro de parâmetros avançados"
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

        self.layout.add_items(
            [layer_layout, tam_layout, save_layout, adv_layout, buttons_layout]
        )
        self.logger.info("Interface da ferramenta construída com sucesso")

    def _load_prefs(self):
        self.logger.debug(f"Carregando preferências salvas da ferramenta. Self={self}")
        last_tam = self.preferences.get("last_implement_length")
        save_to_folder = self.preferences.get("save_to_folder", False)
        last_file = self.preferences.get("last_output_file", "")
        apply_style = self.preferences.get("apply_style", False)
        last_qml = self.preferences.get("last_qml_path", "")
        self.qml_selector.set_file_path(last_qml)
        self.qml_selector.set_enabled(bool(apply_style))

        if last_tam is not None:
            try:
                self.spin_tam.setValue(float(last_tam))
            except Exception as e:
                self.logger.warning(
                    f"Valor de tamanho do implemento inválido nas preferências: {last_tam}. Erro: {str(e)}"
                )

        try:
            self.save_selector.set_enabled(bool(save_to_folder))
            self.save_selector.set_file_path(last_file)
            self.logger.debug("Preferências carregadas e aplicadas com sucesso")
        except Exception as e:
            self.logger.warning(f"Erro ao restaurar algumas preferências: {str(e)}")

    def _save_prefs(self):
        self.logger.debug("Salvando preferências da ferramenta")
        self.preferences["last_implement_length"] = float(self.spin_tam.value())
        self.preferences["save_to_folder"] = bool(self.save_selector.is_enabled())
        self.preferences["last_output_file"] = self.save_selector.get_file_path()
        self.preferences["apply_style"] = bool(self.qml_selector.is_enabled())
        self.preferences["last_qml_path"] = self.qml_selector.get_file_path()
        self.preferences["window_width"] = self.width()
        self.preferences["window_height"] = self.height()

        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.debug(
            f"Preferências salvas: tamanho={self.preferences['last_implement_length']}m, salvar_arquivo={self.preferences['save_to_folder']}"
        )

    def execute_tool(self):
        self.logger.info("Iniciando processamento: Gerar Rastro Implemento")

        input_layer = self.layer_input.current_layer()
        self.start_stats(
            input_layer,
        )

        if not isinstance(input_layer, QgsVectorLayer):
            self.logger.warning("Nenhuma camada de linhas válida selecionada")
            QgisMessageUtil.bar_warning(
                self.iface, STR.SELECT_VALID_LINE_LAYER
            )
            return

        implement_lenght = float(self.spin_tam.value())
        save_to_folder = self.save_selector.is_enabled()
        out_file = self.save_selector.get_file_path().strip() if save_to_folder else ""

        if save_to_folder and out_file and not out_file.startswith("memory"):
            output_path = out_file
        else:
            save_to_folder = False
            output_path = None

        only_selected = self.layer_input.only_selected_enabled()
        output_name = "Rastro_implemento"
        self.logger.info(
            f"Parâmetros: camada='{input_layer.name()}', tamanho={implement_lenght}m, selecionadas={only_selected}, salvar_arquivo={save_to_folder}"
        )

        self.logger.info(
            f"execute_tool: implement_lenght={implement_lenght}, only_selected={only_selected}, save_to_folder={save_to_folder}, output_path={output_path}"
        )

        layer, implement_lenght = self._resolve_input_layer(
            input_layer, implement_lenght
        )
        if layer is None:
            self.logger.warning("_resolve_input_layer returned None, aborting")
            return

        ok, error = VectorLayerSource.validate_layer(
            layer, expected_geometry=QgsWkbTypes.LineGeometry
        )

        if not ok:
            self.logger.error(f"Layer validation failed: {error}")
            QgisMessageUtil.modal_error(self.iface, error)
            return
        else:
            self.logger.debug("Layer validation passed")

        layer = self._process_selection(layer, only_selected)
        if layer is None:
            self.logger.warning("_process_selection returned None, aborting")
            return
        self.logger.debug("Selection processing complete, layer ready")

        if implement_lenght == 0:
            self.logger.error("implement_lenght is zero, aborting")
            QgisMessageUtil.modal_error(self.iface, STR.BUFFER_CANNOT_BE_ZERO)
            return

        buffer_distance = float(implement_lenght) / 2.0

        context = ExecutionContext()
        context.set("layer", layer)
        context.set("save_to_folder", save_to_folder)
        context.set("output_path", output_path)
        context.set("output_name", output_name)
        context.set("tool_key", self.TOOL_KEY)
        context.set("buffer_distance", buffer_distance)
        context.set("buffer_dissolve", False)

        self.logger.debug(
            f"Context prepared: {{'buffer_distance':{buffer_distance}, 'output_name':{output_name}}}"
        )

        feature_count = layer.featureCount() if layer else 0
        threshold = int(self.system_preferences.get("async_threshold_features", 1000))
        self.logger.debug(
            f"Comparando feições: {feature_count} versus {threshold} (limiar)"
        )

        if feature_count > threshold:
            self.logger.info("Processamento iniciado em background (assíncrono)")
            self._run_async_pipeline(context)
        else:
            self.logger.info("Executando processamento de forma síncrona")
            self._run_sync_pipeline(context)

    def _resolve_input_layer(
        self, input_layer, implement_lenght: float
    ) -> Tuple[Optional[QgsVectorLayer], float]:
        """Etapa 1: Resolver camada de entrada e converter tamanho se necessário"""
        layer = (
            input_layer
            if isinstance(input_layer, QgsVectorLayer)
            else QgsProject.instance().mapLayer(input_layer)
        )
        self.logger.debug(f"Camada resolvida: {layer.name() if layer else 'None'}")

        if not isinstance(layer, QgsVectorLayer):
            self.logger.error("Camada de entrada inválida - não é QgsVectorLayer")
            QgisMessageUtil.modal_error(self.iface, STR.INVALID_INPUT_LAYER)
            return None, implement_lenght
        implement_lenght = VectorLayerProjection.convert_distance_to_layer_units(
            layer, implement_lenght
        )

        return layer, implement_lenght

    def _process_selection(
        self, layer: QgsVectorLayer, only_selected: bool
    ) -> Optional[QgsVectorLayer]:
        """Etapa 3: Processar seleção de feições"""
        self.logger.info("3/6] Processando seleção de feições")
        if only_selected:
            self.logger.debug(
                f"Filtrando apenas feições selecionadas. Total selecionadas: {layer.selectedFeatureCount()}"
            )
            layer_sel, err = VectorLayerGeometry.get_selected_features(layer)
            if err:
                self.logger.error(f"Erro ao obter feições selecionadas: {err}")
                QgisMessageUtil.modal_error(self.iface, err)
                return None
            layer = layer_sel
            self.logger.debug(f"Usando camada com feições selecionadas: {layer.name()}")
        else:
            self.logger.debug(
                f"Processando todas as feições da camada. Total: {layer.featureCount()}"
            )

        return layer

    def _run_sync_pipeline(self, context: ExecutionContext) -> Optional[QgsVectorLayer]:
        """
        Executa a pipeline de forma síncrona:
        Explode -> Buffer -> Save
        Retorna camada final.
        """

        try:
            layer: QgsVectorLayer = context.get("layer")
            if not layer or not layer.isValid():
                raise RuntimeError(STR.INVALID_INPUT_LAYER)

            save_to_folder: bool = context.get("save_to_folder")
            output_path: Optional[str] = context.get("output_path")
            output_name: str = context.get("output_name")
            buffer_distance: float = context.get("buffer_distance")
            dissolve: bool = context.get("buffer_dissolve")

            self.logger.debug("SYNC: ExplodeStep")

            exploded = VectorLayerGeometry.explode_multipart_features(
                layer=layer, external_tool_key=self.TOOL_KEY
            )

            if not exploded or not exploded.isValid():
                raise RuntimeError("Falha no explode")

            self.logger.debug("SYNC: BufferStep")

            buffered = VectorLayerGeometry.create_buffer_geometry(
                layer=exploded,
                distance=buffer_distance,
                dissolve=dissolve,
                external_tool_key=self.TOOL_KEY,
            )

            if not buffered or not buffered.isValid():
                raise RuntimeError("Falha no buffer")

            self.logger.debug("SYNC: SaveVectorStep")

            final_layer = VectorLayerSource.save_vector_layer(
                layer=buffered,
                output_path=output_path,
                save_to_folder=save_to_folder,
                output_name=output_name,
                external_tool_key=self.TOOL_KEY,
            )

            if not final_layer or not final_layer.isValid():
                raise RuntimeError("Falha ao salvar camada")

            context.set("layer", final_layer)
            self._on_pipeline_finished(context)
        except Exception as e:
            self.logger.error(f"Erro pipeline SYNC: {e}. Contexto: {context}.")
            QgisMessageUtil.modal_error(self.iface, str(e))
            return None

    def _run_async_pipeline(self, context: ExecutionContext):
        engine = AsyncPipelineEngine(
            steps=[ExplodeStep(), BufferStep(), SaveVectorStep()],
            context=context,
            on_finished=self._on_pipeline_finished,
            on_error=self._on_pipeline_error,
        )

        self.logger.info("Starting AsyncPipelineEngine")
        engine.start()
        return None

    def _on_pipeline_finished(self, context):

        final_layer = context.get("layer")

        self.logger.warning(f"Layer: {final_layer}")

        self.logger.warning(
            f"Is valid: {final_layer.isValid() if final_layer else None}"
        )

        self.logger.warning(
            f"Provider: {final_layer.providerType() if final_layer else None}"
        )
        if not final_layer:
            QgisMessageUtil.modal_error(
                self.iface, STR.FINAL_LAYER_NOT_FOUND
            )
            return

        if not QgsProject.instance().mapLayer(final_layer.id()):
            self.logger.debug("Final layer not in project, adding")
            QgsProject.instance().addMapLayer(final_layer)
        else:
            self.logger.debug("Final layer already in project")

        if self.qml_selector.is_enabled():
            qml = self.qml_selector.get_file_path()
            self.logger.debug(f"QML style enabled, path={qml}")
            if qml:
                self.apply_qml_style(final_layer, qml)
                self.logger.info("QML style applied to final layer")
        else:
            self.logger.debug("QML style not enabled")

        QgisMessageUtil.bar_success(self.iface, STR.SUCCESS_MESSAGE)

        self.finish_stats()


def run(iface):
    dlg = GenerateTrailPlugin(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
