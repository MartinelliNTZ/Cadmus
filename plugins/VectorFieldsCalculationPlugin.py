# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsVectorLayer, QgsWkbTypes, QgsApplication
import os

from ..utils.vector.VectorLayerAttributes import VectorLayerAttributes
from ..utils.vector.VectorLayerMetrics import VectorLayerMetrics
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.ToolKeys import ToolKey
from ..utils.ProjectUtils import ProjectUtils
from ..core.engine_tasks.AsyncPipelineEngine import AsyncPipelineEngine
from ..core.engine_tasks.ExecutionContext import ExecutionContext
from ..core.engine_tasks.PointFieldsStep import PointFieldsStep
from ..core.engine_tasks.LineFieldsStep import LineFieldsStep
from ..core.engine_tasks.PolygonFieldsStep import PolygonFieldsStep
from .BasePlugin import BasePluginMTL


class VectorFieldsCalculationPlugin(BasePluginMTL):
    
    def __init__(self, iface):
        self.iface = iface
        self.actions = []
        self.init(
            tool_key=ToolKey.VECTOR_FIELDS,
            class_name="VectorFieldsCalculationPlugin",
            build_ui=False,
            load_settings_prefs=True
        )

    def initGui(self):
        self.create_action(
            "../resources/icons/vector_field.png",
            "Calcular Campos Vetoriais",
            self.run_vector_field
        )

    def unload(self):
        for a in self.actions:
            self.iface.removePluginMenu("Cadmus", a)

    # ==================== ENTRY POINT ====================

    def run_vector_field(self):
        """Entry point: valida, obtém parâmetros e decide entre sync/async."""
        self.logger.info("Iniciando Calcular Campos Vetoriais")

        from ..utils.ProjectUtils import ProjectUtils
        layer = ProjectUtils.get_active_vector_layer(self.iface.activeLayer(), self.logger, require_editable=True)
        if not layer:
            QgisMessageUtil.bar_critical(self.iface, "Selecione uma camada vetorial editável")
            self.logger.warning("Nenhuma camada vetorial editável disponível")
            return

        # estatísticas iniciais (agrega contagem de feições em relatórios)
        try:
            self.start_stats(layer)
        except Exception:
            # se houver problema, apenas continue, não deve quebrar a ferramenta
            self.logger.debug("Falha ao iniciar estatísticas")

        # Verificar se a camada é KML (não editável)
        source = layer.source().lower()
        if source.endswith('.kml') or '|layername=' in source and source.startswith('file://') and '.kml' in source:
            self.logger.warning("Camada KML não pode ser editada")
            QgisMessageUtil.bar_critical(
                self.iface, 
                "❌ Arquivos KML não são editáveis.\n\n"
                "Converta a camada para GeoPackage (.gpkg) ou Shapefile (.shp) antes de usar esta ferramenta."
            )
            return

        geom_type = layer.geometryType()
        self.logger.debug(f"Camada: {layer.name()}, Geometria: {geom_type}")

        # Mapear tipo de geometria para step class
        step_map = {
            QgsWkbTypes.PointGeometry: (PointFieldsStep, self._prepare_point_fields),
            QgsWkbTypes.LineGeometry: (LineFieldsStep, self._prepare_line_fields),
            QgsWkbTypes.PolygonGeometry: (PolygonFieldsStep, self._prepare_polygon_fields),
        }

        if geom_type not in step_map:
            self.logger.error(f"Geometria não suportada: {geom_type}")
            QgisMessageUtil.bar_warning(self.iface, "Tipo de geometria não suportado")
            return

        step_class, prepare_func = step_map[geom_type]

        # Preparar contexto e field_map
        try:
            field_map, mode_altered = prepare_func(layer)
            if field_map is None:
                return
        except Exception as e:
            self.logger.error(f"Erro ao preparar campos: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro na preparação: {str(e)}")
            return

        # Decidir entre sync/async baseado em feature count (mais confiável que tamanho de arquivo)
        precision = int(self.settings_preferences.get('vector_field_precision', 2))
        
        # Feature count é muito mais confiável que compute_size() para decidir
        # Threshold: 1000 features = sempre assíncrono (evita UI travada)
        feature_count = layer.featureCount()
        # valor padrão de segurança
        threshold_features = int(self.settings_preferences.get('async_threshold_features', 1000))
        
        self.logger.debug(f"Feature count: {feature_count}, Threshold: {threshold_features} features")

        try:
            # SEMPRE usar assíncrono para evitar travamento da UI
            # Feature count > 1000 ou qualquer memória layer = assíncrono obrigatório
            if feature_count >= threshold_features or layer.source().startswith("memory:"):
                self.logger.info(f"Usando processamento assíncrono (features={feature_count})")
                self._start_async_calculation(
                    layer, step_class, field_map, mode_altered, precision
                )
            else:
                # Mesmo com < 1000 features, considerar usar async para consistência
                # Descomentar a linha abaixo para forçar SEMPRE assíncrono
                # self.logger.info("Forçando processamento assíncrono para consistência")
                # self._start_async_calculation(layer, step_class, field_map, mode_altered, precision)
                
                self.logger.info("Usando processamento síncrono (features={})".format(feature_count))
                self._execute_sync_calculation(
                    layer, field_map, mode_altered, precision
                )
                # estatísticas finais após término síncrono
                try:
                    self.finish_stats()
                except Exception:
                    self.logger.debug("Falha ao finalizar estatísticas")
        except Exception as e:
            self.logger.error(f"Erro: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro: {str(e)}")

    # ==================== PREPARATION METHODS ====================

    def _prepare_point_fields(self, layer):
        """Prepara field_map e parâmetros para cálculo de coordenadas X e Y.

        A funcionalidade de Z foi removida por decisão de design, portanto não
        há mais prompt ao usuário nem criação de campo Z.
        """
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
        requested_mode = self.settings_preferences.get('calculation_method', 'Elipsoidal')
        calc_mode, mode_altered = self._resolve_calculation_mode(layer, requested_mode)

        field_map = VectorLayerAttributes.resolve_field_names_for_calculation(
            layer, "length", calc_mode
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
        requested_mode = self.settings_preferences.get('calculation_method', 'Elipsoidal')
        calc_mode, mode_altered = self._resolve_calculation_mode(layer, requested_mode)

        field_map = VectorLayerAttributes.resolve_field_names_for_calculation(
            layer, "area", calc_mode
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
        """Valida e ajusta modo de cálculo (CRS geográfico com Cartesiana -> Ambos)."""
        if requested_mode != "Cartesiana" or VectorLayerProjection.is_geographic_crs(layer):
            return requested_mode, False

        self.logger.warning("CRS geográfico com modo Cartesiana -> mudando para Ambos")
        msg = (
            f"⚠️ Camada usa CRS Geográfico ({layer.crs().authid()})\n\n"
            f"Modo 'Cartesiano' resultaria em valores em graus².\n\n"
            f"Calculando AMBOS os modos automaticamente."
        )
        QgisMessageUtil.bar_warning(self.iface, msg)
        return "Ambos", True

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

    # ==================== EXECUTION ====================

    def _execute_sync_calculation(self, layer, field_map, mode_altered, precision):
        """Executa o cálculo de forma síncrona (bloqueador)."""
        try:
            geom_type = layer.geometryType()
            self.logger.debug(f"Iniciando cálculo síncrono para geometria tipo {geom_type}")

            if geom_type == QgsWkbTypes.PointGeometry:
                # XY sempre em 8 casas, ignorar preferência
                const_prec = 8
                self.logger.debug(f"Criando campos de coordenadas com precisão {const_prec}")
                VectorLayerAttributes.create_point_coordinate_fields(
                    layer, field_map, precision=const_prec
                )
                self.logger.debug("Atualizando coordenadas X/Y")
                VectorLayerAttributes.update_point_xy_coordinates(
                    layer, field_map, precision=const_prec
                )
                msg = "Campos X/Y calculados com sucesso"

            elif geom_type == QgsWkbTypes.LineGeometry:
                self.logger.debug("Criando campos de comprimento")
                VectorLayerAttributes.create_point_coordinate_fields(layer, field_map, precision=precision)
                if "Elipsoidal" in field_map:
                    self.logger.debug("Calculando comprimento elispoidal")
                    VectorLayerMetrics.calculate_line_length(
                        layer, field_map["Elipsoidal"], use_ellipsoidal=True, precision=precision
                    )
                if "Cartesiana" in field_map:
                    self.logger.debug("Calculando comprimento cartesiano")
                    VectorLayerMetrics.calculate_line_length(
                        layer, field_map["Cartesiana"], use_ellipsoidal=False, precision=precision
                    )
                msg = "Comprimento de linhas calculado com sucesso"

            elif geom_type == QgsWkbTypes.PolygonGeometry:
                self.logger.debug("Criando campos de área")
                VectorLayerAttributes.create_point_coordinate_fields(layer, field_map, precision=precision)
                if "Elipsoidal" in field_map:
                    self.logger.debug("Calculando área elispoidal")
                    VectorLayerMetrics.calculate_polygon_area(
                        layer, field_map["Elipsoidal"], use_ellipsoidal=True, precision=precision
                    )
                if "Cartesiana" in field_map:
                    self.logger.debug("Calculando área cartesiana")
                    VectorLayerMetrics.calculate_polygon_area(
                        layer, field_map["Cartesiana"], use_ellipsoidal=False, precision=precision
                    )
                msg = "Área de polígonos calculada com sucesso"

            if not mode_altered:
                QgisMessageUtil.bar_success(self.iface, msg)
                self.logger.info(msg)
            self.logger.info("Cálculo síncrono concluído")

        except Exception as e:
            self.logger.error(f"Erro no cálculo síncrono: {str(e)}")
            raise

    def _start_async_calculation(self, layer, step_class, field_map, mode_altered, precision):
        """Inicia pipeline assíncrona com AsyncPipelineEngine.
        
        Contexto:
        - A task executa em thread de trabalho; ela **não** toca na camada,
          apenas calcula os valores e devolve um mapeamento de atualizações.
        - O step correspondente roda no thread principal e aplica os atributos
          à camada existente em lotes (via provider.changeAttributeValues).
        
        Resultado: UI não trava, arquivo original recebe os novos campos e
        valores sem criar vetores temporários.
        """
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

            # Pipeline com 1 step: calcula campos NO arquivo original
            calc_step = step_class()

            engine = AsyncPipelineEngine(
                steps=[calc_step],
                context=context,
                on_finished=self._on_async_finished,
                on_error=self._on_async_error,
                on_cancelled=self._on_async_cancelled
            )

            engine.start()
            self.logger.info("Pipeline assíncrona iniciada com 1 step")

        except Exception as e:
            self.logger.error(f"Erro ao iniciar pipeline: {str(e)}")
            QgisMessageUtil.bar_critical(self.iface, f"Erro ao iniciar cálculo: {str(e)}")
            raise

    def _on_async_finished(self, context):
        """Callback de sucesso da pipeline assíncrona."""
        self.logger.info("Cálculo assíncrono finalizado com sucesso!")
        
        layer = context.get("layer")
        mode_altered = context.get("mode_altered", False)
        
        if layer:
            geom_type = layer.geometryType()
            if geom_type == QgsWkbTypes.PointGeometry:
                msg = "Campos X/Y calculados com sucesso"
            elif geom_type == QgsWkbTypes.LineGeometry:
                msg = "Comprimento de linhas calculado com sucesso"
            else:
                msg = "Área de polígonos calculada com sucesso"
            
            if not mode_altered:
                QgisMessageUtil.bar_success(self.iface, msg)
                self.logger.info(msg)
        
        # terminar estatísticas
        try:
            self.finish_stats()
            self.logger.debug("Estatísticas finalizadas")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")

    def _on_async_error(self, errors):
        """Callback de erro da pipeline assíncrona."""
        error_msg = "\n".join(str(e) for e in errors) if errors else "Erro desconhecido"
        self.logger.error(f"ERRO na pipeline: {error_msg}")
        QgisMessageUtil.bar_critical(self.iface, f"Falha no cálculo:\n{error_msg}")
        try:
            self.finish_stats()
            self.logger.debug("Estatísticas finalizadas após erro")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")

    def _on_async_cancelled(self, context):
        """Callback de cancelamento da pipeline assíncrona."""
        self.logger.warning("Pipeline assíncrona CANCELADA pelo usuário")
        QgisMessageUtil.bar_warning(self.iface, "Operação cancelada pelo usuário.")
        try:
            self.finish_stats()
            self.logger.debug("Estatísticas finalizadas após cancelamento")
        except Exception as e:
            self.logger.debug(f"Falha ao finalizar estatísticas: {e}")


def run_vector_field(iface):
    """Função de entrada do plugin."""
    plugin = VectorFieldsCalculationPlugin(iface)
    plugin.initGui()
    return plugin
