# -*- coding: utf-8 -*-
from qgis.core import QgsVectorLayer, QgsWkbTypes
from ..utils.Preferences import Preferences

from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.ExecutionContext import ExecutionContext
from ..core.engine_tasks.LineFieldsStep import LineFieldsStep
from ..core.engine_tasks.PointFieldsStep import PointFieldsStep
from ..core.engine_tasks.PolygonFieldsStep import PolygonFieldsStep
from ..i18n.TranslationManager import STR
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ToolKeys import ToolKey
from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
from ..utils.vector.VectorLayerMetrics import VectorLayerMetrics
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from .BasePlugin import BasePluginMTL


class VectorFieldsCalculationPlugin(BasePluginMTL):

    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.init(
            tool_key=ToolKey.VECTOR_FIELDS,
            class_name="VectorFieldsCalculationPlugin",
            build_ui=False,
            load_system_prefs=True,
        )

    def initGui(self):
        self.create_action(
            "../resources/icons/vector_field.png",
            STR.VECTOR_FIELDS_TITLE,
            self.run_vector_field,
        )

    def unload(self):
        for a in self.actions:
            self.iface.removePluginMenu("Cadmus", a)

    # ==================== ENTRY POINT ====================

    def run_vector_field(self):
        """Entry point: valida, obtém parâmetros e decide entre sync/async."""
        self.logger.info("Iniciando Calcular Campos Vetoriais")

        from ..utils.ProjectUtils import ProjectUtils

        layer = self.iface.activeLayer()
        if not layer or not isinstance(layer, QgsVectorLayer):
            QgisMessageUtil.bar_critical(self.iface, STR.SELECT_VECTOR_LAYER)
            self.logger.warning("Nenhuma camada vetorial ativa")
            return

        # --- 1. VERIFICAR SE CAMADA É EDITÁVEL (com pergunta) ---
        if not ProjectUtils.ask_and_make_editable(self.iface, layer, self.logger):
            QgisMessageUtil.bar_critical(self.iface, STR.SELECT_EDITABLE_VECTOR_LAYER)
            self.logger.warning("Usuário recusou tornar camada editável")
            return

        self.logger.info(f"Camada editável confirmada: {layer.name()}")

        try:
            self.start_stats(layer)
        except Exception as e:
            self.logger.debug(f"Falha ao iniciar estatísticas: {e}")

        source = layer.source().lower()
        if source.endswith(".kml") or (
            "|layername=" in source
            and source.startswith("file://")
            and ".kml" in source
        ):
            self.logger.warning("Camada KML não pode ser editada")
            QgisMessageUtil.bar_critical(
                self.iface,
                f"❌ {STR.KML_FILES_ARE_NOT_EDITABLE}\n\n"
                f"{STR.CONVERT_LAYER_TO_GPKG_OR_SHP_BEFORE_USING}",
            )
            return

        geom_type = layer.geometryType()
        self.logger.debug(f"Camada: {layer.name()}, Geometria: {geom_type}")

        step_map = {
            QgsWkbTypes.PointGeometry: (PointFieldsStep, self._prepare_point_fields),
            QgsWkbTypes.LineGeometry: (LineFieldsStep, self._prepare_line_fields),
            QgsWkbTypes.PolygonGeometry: (
                PolygonFieldsStep,
                self._prepare_polygon_fields,
            ),
        }

        if geom_type not in step_map:
            self.logger.error(f"Geometria não suportada: {geom_type}")
            QgisMessageUtil.bar_warning(self.iface, STR.GEOMETRY_TYPE_NOT_SUPPORTED)
            return

        step_class, prepare_func = step_map[geom_type]

        try:
            field_map, mode_altered = prepare_func(layer)
            if field_map is None:
                return
        except Exception as e:
            self.logger.error(f"Erro ao preparar campos: {str(e)}")
            QgisMessageUtil.bar_critical(
                self.iface, f"{STR.ERROR_IN_PREPARATION} {str(e)}"
            )
            return

        precision = int(self.system_preferences.get("vector_field_precision", 2))
        feature_count = layer.featureCount()
        threshold_features = int(
            self.system_preferences.get("async_threshold_features", 1000)
        )

        self.logger.debug(
            f"Feature count: {feature_count}, Threshold: {threshold_features} features"
        )

        try:
            if feature_count >= threshold_features or layer.source().startswith(
                "memory:"
            ):
                self.logger.info(
                    f"Usando processamento assíncrono (features={feature_count})"
                )
                self._start_async_calculation(
                    layer, step_class, field_map, mode_altered, precision
                )
            else:
                self.logger.info(
                    "Usando processamento síncrono (features={})".format(feature_count)
                )
                self._execute_sync_calculation(
                    layer, field_map, mode_altered, precision
                )
                try:
                    self.finish_stats()
                    # Salvar prefs e incrementar uso APÓS execução bem-sucedida
                    Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
                    self.on_finish_plugin()
                except Exception as e:
                    self.logger.debug(f"Falha ao finalizar estatísticas: {e}")
        except Exception as e:
            self.logger.error(f"Erro: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"{STR.ERROR}: {str(e)}")

    # ==================== PREPARATION METHODS ====================

    def _prepare_point_fields(self, layer):
        """Prepara field_map e parâmetros para cálculo de coordenadas X e Y."""
        field_map = {}
        for base in ["x", "y"]:
            name = self._resolve_field_name(layer, base)
            if not name:
                self.logger.warning(f"Campo {base} cancelado")
                return None, False
            field_map[base] = name

        return field_map, False

    def _prepare_line_fields(self, layer):
        """Prepara field_map para cálculo de comprimento."""
        requested_mode = self.system_preferences.get(
            "calculation_method", STR.ELLIPSOIDAL
        )
        calc_mode, mode_altered = self._resolve_calculation_mode(layer, requested_mode)
        cartesian_suffix, ellipsoidal_suffix = self._get_metric_suffixes()

        field_map = VectorLayerAttributes.resolve_field_names_for_calculation(
            layer,
            "length",
            calc_mode,
            cartesian_suffix=cartesian_suffix,
            ellipsoidal_suffix=ellipsoidal_suffix,
        )

        resolved_fields = {}
        for mode, base_field in field_map.items():
            resolved = self._resolve_field_name(layer, base_field)
            if not resolved:
                self.logger.warning(f"Campo para {mode} cancelado")
                return None, False
            resolved_fields[mode] = resolved

        return resolved_fields, mode_altered

    def _prepare_polygon_fields(self, layer):
        """Prepara field_map para cálculo de área."""
        requested_mode = self.system_preferences.get(
            "calculation_method", STR.ELLIPSOIDAL
        )
        calc_mode, mode_altered = self._resolve_calculation_mode(layer, requested_mode)
        cartesian_suffix, ellipsoidal_suffix = self._get_metric_suffixes()

        field_map = VectorLayerAttributes.resolve_field_names_for_calculation(
            layer,
            "area",
            calc_mode,
            cartesian_suffix=cartesian_suffix,
            ellipsoidal_suffix=ellipsoidal_suffix,
        )

        resolved_fields = {}
        for mode, base_field in field_map.items():
            resolved = self._resolve_field_name(layer, base_field)
            if not resolved:
                self.logger.warning(f"Campo para {mode} cancelado")
                return None, False
            resolved_fields[mode] = resolved

        return resolved_fields, mode_altered

    # ==================== HELPERS ====================

    def _resolve_calculation_mode(self, layer, requested_mode):
        """Valida e ajusta modo de cálculo.

        Fluxo correto:
        - Se modo solicitado é Cartesiano E CRS é geográfico → força Ambos
        - Caso contrário (Elipsoidal, Ambos, ou Cartesiano em CRS projetado) → segue solicitado
        """
        if requested_mode == STR.CARTESIAN and VectorLayerProjection.is_geographic_crs(
            layer
        ):
            self.logger.warning(
                "Modo Cartesiano em CRS geográfico -> calculando ambos os modos"
            )
            msg = (
                f"⚠️ {STR.LAYER_USES_GEOGRAPHIC_CRS} ({layer.crs().authid()})\n\n"
                f"{STR.CARTESIAN_MODE_RESULTS_IN_DEGREES2}\n"
                f"{STR.CALCULATING_BOTH_MODES_AUTOMATICALLY}"
            )
            QgisMessageUtil.bar_warning(self.iface, msg)
            self.logger.info(msg)
            return STR.BOTH, True

        return requested_mode, False

    def _resolve_field_name(self, layer, base_name):
        """Resolve conflito de nomes de campo."""
        if layer.fields().lookupField(base_name) == -1:
            return base_name

        action = QgisMessageUtil.ask_field_conflict(self.iface, base_name)
        if action == "cancel":
            return None
        if action == "replace":
            return base_name

        i = 1
        while layer.fields().lookupField(f"{base_name}_{i}") != -1:
            i += 1
        return f"{base_name}_{i}"

    def _get_metric_suffixes(self):
        """Lê sufixos configurados para campos de comprimento e área."""
        cartesian_suffix = self.preferences.get("cartesian_suffix", "")
        ellipsoidal_suffix = self.preferences.get("ellipsoidal_suffix", "_eli")

        if cartesian_suffix is None:
            cartesian_suffix = ""
        if ellipsoidal_suffix is None:
            ellipsoidal_suffix = "_eli"

        return str(cartesian_suffix), str(ellipsoidal_suffix)

    # ==================== EXECUTION ====================

    def _execute_sync_calculation(self, layer, field_map, mode_altered, precision):
        """Executa o cálculo de forma síncrona (bloqueador)."""
        try:
            geom_type = layer.geometryType()
            self.logger.debug(
                f"Iniciando cálculo síncrono para geometria tipo {geom_type}"
            )

            if geom_type == QgsWkbTypes.PointGeometry:
                const_prec = 8
                self.logger.debug(
                    f"Criando campos de coordenadas com precisão {const_prec}"
                )
                VectorLayerAttributes.create_point_coordinate_fields(
                    layer, field_map, precision=const_prec, tool_key=self.TOOL_KEY
                )
                self.logger.debug("Atualizando coordenadas X/Y")
                VectorLayerAttributes.update_point_xy_coordinates(
                    layer, field_map, precision=const_prec
                )
                msg = STR.XY_FIELDS_CALCULATED_SUCCESS

            elif geom_type == QgsWkbTypes.LineGeometry:
                self.logger.debug("Criando campos de comprimento")
                VectorLayerAttributes.create_point_coordinate_fields(
                    layer, field_map, precision=precision, tool_key=self.TOOL_KEY
                )
                if STR.ELLIPSOIDAL in field_map:
                    self.logger.debug("Calculando comprimento elipsoidal")
                    VectorLayerMetrics.calculate_line_length(
                        layer,
                        field_map[STR.ELLIPSOIDAL],
                        use_ellipsoidal=True,
                        precision=precision,
                        tool_key=self.TOOL_KEY,
                    )
                if STR.CARTESIAN in field_map:
                    self.logger.debug("Calculando comprimento cartesiano")
                    VectorLayerMetrics.calculate_line_length(
                        layer,
                        field_map[STR.CARTESIAN],
                        use_ellipsoidal=False,
                        precision=precision,
                        tool_key=self.TOOL_KEY,
                    )
                msg = STR.LINE_LENGTH_CALCULATED_SUCCESS

            elif geom_type == QgsWkbTypes.PolygonGeometry:
                self.logger.debug("Criando campos de área")
                VectorLayerAttributes.create_point_coordinate_fields(
                    layer, field_map, precision=precision, tool_key=self.TOOL_KEY
                )
                if STR.ELLIPSOIDAL in field_map:
                    self.logger.debug("Calculando área elipsoidal")
                    VectorLayerMetrics.calculate_polygon_area(
                        layer,
                        field_map[STR.ELLIPSOIDAL],
                        use_ellipsoidal=True,
                        precision=precision,
                        tool_key=self.TOOL_KEY,
                    )
                if STR.CARTESIAN in field_map:
                    self.logger.debug("Calculando área cartesiana")
                    VectorLayerMetrics.calculate_polygon_area(
                        layer,
                        field_map[STR.CARTESIAN],
                        use_ellipsoidal=False,
                        precision=precision,
                        tool_key=self.TOOL_KEY,
                    )
                msg = STR.POLYGON_AREA_CALCULATED_SUCCESS

            if not mode_altered:
                QgisMessageUtil.bar_success(self.iface, msg)
                self.logger.info(msg)
            self.logger.info("Cálculo síncrono concluído")

        except Exception as e:
            self.logger.error(f"Erro no cálculo síncrono: {str(e)}")
            raise

    def _start_async_calculation(
        self, layer, step_class, field_map, mode_altered, precision
    ):
        """Inicia pipeline assíncrona com AsyncPipelineEngine."""
        try:
            context = ExecutionContext()
            context.set("layer", layer)
            context.set("field_map", field_map)
            context.set("precision", precision)
            context.set("tool_key", self.TOOL_KEY)
            context.set("mode_altered", mode_altered)

            self.logger.info(
                f"Iniciando pipeline assíncrona: step={step_class.__name__}, "
                f"layer={layer.name()}, features={layer.featureCount()}"
            )
            self.logger.debug(
                f"Parâmetros: field_map={field_map}, precision={precision}"
            )

            calc_step = step_class()

            engine = AsyncPipelineEngine(
                steps=[calc_step],
                context=context,
                on_finished=self._on_async_finished,
                on_error=self._on_async_error,
                on_cancelled=self._on_async_cancelled,
            )

            engine.start()
            self.logger.info("Pipeline assíncrona iniciada com 1 step")

        except Exception as e:
            self.logger.error(f"Erro ao iniciar pipeline: {str(e)}")
            QgisMessageUtil.bar_critical(
                self.iface, f"{STR.ERROR_STARTING_CALCULATION} {str(e)}"
            )
            raise

    def _on_async_finished(self, context):
        """Callback de sucesso da pipeline assíncrona."""
        self.logger.info("Cálculo assíncrono finalizado com sucesso!")

        layer = context.get("layer")
        mode_altered = context.get("mode_altered", False)

        if layer:
            geom_type = layer.geometryType()
            if geom_type == QgsWkbTypes.PointGeometry:
                msg = STR.XY_FIELDS_CALCULATED_SUCCESS
            elif geom_type == QgsWkbTypes.LineGeometry:
                msg = STR.LINE_LENGTH_CALCULATED_SUCCESS
            else:
                msg = STR.POLYGON_AREA_CALCULATED_SUCCESS

            if not mode_altered:
                QgisMessageUtil.bar_success(self.iface, msg)
                self.logger.info(msg)

        try:
            self.finish_stats()
            Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
            self.on_finish_plugin()
            self.logger.debug("Estatísticas finalizadas após sucesso")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")

    def _on_async_error(self, errors):
        """Callback de erro da pipeline assíncrona."""
        error_msg = "\n".join(str(e) for e in errors) if errors else STR.UNKNOWN_ERROR
        self.logger.error(f"ERRO na pipeline: {error_msg}")
        QgisMessageUtil.bar_critical(
            self.iface, f"{STR.CALCULATION_FAILED}\n{error_msg}"
        )
        try:
            self.finish_stats()
            self.logger.debug("Estatísticas finalizadas após erro")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")

    def _on_async_cancelled(self, context):
        """Callback de cancelamento da pipeline assíncrona."""
        self.logger.warning("Pipeline assíncrona CANCELADA pelo usuário")
        QgisMessageUtil.bar_warning(self.iface, STR.OPERATION_CANCELLED_BY_USER)
        try:
            self.finish_stats()
            self.logger.debug("Estatísticas finalizadas após cancelamento")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")


def run(iface):
    plugin = VectorFieldsCalculationPlugin(iface)
    plugin.run_vector_field()
