# -*- coding: utf-8 -*-
import os
import re

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterMultipleLayers,
)

from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from ..utils.vector.VectorLayerProjection import VectorLayerProjection
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RasterMassSampler(BaseProcessingAlgorithm):
    """
    QgsProcessingAlgorithm: Amostragem massiva de rasters para pontos.
    """

    TOOL_KEY = ToolKey.RASTER_MASS_SAMPLER
    ALGORITHM_NAME = "raster_mass_sampler"
    ALGORITHM_DISPLAY_NAME = STR.RASTER_MASS_SAMPLER_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    ICON = im.RASTER_MASS_SAMPLER
    INSTRUCTIONS_FILE = "raster_mass_sampler.html"

    INPUT_POINTS = "INPUT_POINTS"
    INPUT_RASTERS = "INPUT_RASTERS"
    OUTPUT_CRS = "OUTPUT_CRS"
    OUTPUT = "OUTPUT"
    DISPLAY_HELP = "DISPLAY_HELP"
    OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"

    def __init__(self):
        super().__init__()
        self.logger = None

    def initAlgorithm(self, config=None):
        self.load_preferences()

        # Inicializa logger apos carregar prefs (para ter tool_key disponivel)
        from ..core.config.LogUtils import LogUtils
        self.logger = LogUtils(
            tool=self.TOOL_KEY,
            class_name=self.__class__.__name__,
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                STR.INPUT_POINTS,
                [QgsProcessing.TypeVectorPoint],
            )
        )

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_RASTERS,
                STR.RASTERS,
                QgsProcessing.TypeRaster,
            )
        )

        self.addParameter(
            QgsProcessingParameterCrs(
                self.OUTPUT_CRS,
                STR.REPROJECT_OUTPUT_LAYER_OPTIONAL,
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, STR.SAMPLED_VALUES)
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.OPEN_OUTPUT_FOLDER,
                STR.OPEN_OUTPUT_FOLDER,
                defaultValue=self.prefs.get("open_output_folder", True),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.DISPLAY_HELP,
                STR.DISPLAY_HELP_FIELD,
                defaultValue=self.prefs.get("display_help", True),
            )
        )

    def processAlgorithm(self, params, context, feedback):
        self.logger.info("Iniciando amostragem massiva de rasters")

        pts = self.parameterAsSource(params, self.INPUT_POINTS, context)
        rasters = self.parameterAsLayerList(
            params, self.INPUT_RASTERS, context)
        open_output_folder = self.parameterAsBool(
            params, self.OPEN_OUTPUT_FOLDER, context)
        display_help = self.parameterAsBool(params, self.DISPLAY_HELP, context)

        if not pts:
            self.logger.error("Camada de pontos nao informada",
                              code="NO_INPUT_POINTS")
            raise ValueError("Camada de pontos de entrada nao encontrada.")
        if not rasters:
            self.logger.error("Nenhum raster informado",
                              code="NO_INPUT_RASTERS")
            raise ValueError("Nenhum raster de entrada informado.")

        output_crs = self.parameterAsCrs(params, self.OUTPUT_CRS, context)
        if not output_crs.isValid():
            output_crs = None

        feedback.pushInfo(
            f"{STR.OUTPUT_CRS_LABEL} {output_crs.authid() if output_crs else STR.NONE}"
        )

        # Prepara estruturas
        out_fields, raster_fields = self.build_output_fields(pts, rasters)
        transforms = self.build_transforms(pts, rasters, context)

        # CRS final
        source_crs = pts.sourceCrs()
        final_crs = output_crs if output_crs else source_crs

        # Determina se precisa reprojetar saida via VectorLayerProjection
        needs_reproject = (
            output_crs is not None
            and source_crs.isValid()
            and output_crs.isValid()
            and source_crs != output_crs
        )

        # Cria sink no CRS de origem (se for reprojetar, fazemos depois)
        sink_crs = source_crs if needs_reproject else final_crs
        sink, dest = self.parameterAsSink(
            params, self.OUTPUT, context, out_fields, pts.wkbType(), sink_crs
        )
        if not sink:
            self.logger.error("Falha ao criar sink de saida",
                              code="SINK_CREATE_FAILED")
            raise RuntimeError("Nao foi possivel criar o sink de saida.")

        # Amostragem incremental com progresso e cancelamento
        total = pts.featureCount() if hasattr(pts, "featureCount") else 0
        processed = 0
        sampled_count = 0
        error_count = 0
        features_buffer = [] if needs_reproject else None

        for feat in pts.getFeatures():
            # Verifica cancelamento
            if feedback.isCanceled():
                self.logger.warning(
                    f"Processamento cancelado pelo usuario apos {processed} pontos")
                break

            geom = feat.geometry()
            if geom is None or geom.isEmpty():
                self.logger.debug(
                    f"Ponto {feat.id()} ignorado: geometria vazia")
                continue

            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(geom)
            attrs = feat.attributes()

            for i, ras in enumerate(rasters):
                try:
                    # Valida CRS do raster antes de transformar
                    ras_crs = ras.crs()
                    if not ras_crs.isValid():
                        self.logger.warning(
                            f"Raster {ras.name()} sem CRS valido, pulando amostragem"
                        )
                        attrs.append(None)
                        continue

                    # Transforma ponto para o CRS do raster
                    ct = transforms[i]
                    if ct is not None:
                        pt = ct.transform(geom.asPoint())
                    else:
                        pt = geom.asPoint()

                    # Amostra o raster
                    dp = ras.dataProvider()
                    if dp is None:
                        self.logger.warning(
                            f"Raster {ras.name()} sem dataProvider, pulando amostragem"
                        )
                        attrs.append(None)
                        continue

                    val, result_ok = dp.sample(pt, 1)
                    if not result_ok:
                        attrs.append(None)
                        self.logger.debug(
                            f"Ponto {feat.id()}, Raster {ras.name()} = sem dados (fora da extensao)"
                        )
                    else:
                        attrs.append(float(val))
                        sampled_count += 1

                except Exception as e:
                    error_count += 1
                    self.logger.error(
                        f"Erro ao amostrar ponto {feat.id()} no raster {ras.name()}: {e}",
                        code="SAMPLE_ERROR",
                    )
                    attrs.append(None)

            out_feat.setAttributes(attrs)

            if needs_reproject:
                features_buffer.append(out_feat)
            else:
                sink.addFeature(out_feat, QgsFeatureSink.FastInsert)

            processed += 1

            # Atualiza progresso
            if total > 0:
                progress = int(100.0 * processed / total)
                feedback.setProgress(progress)
                if processed % 100 == 0:
                    feedback.pushInfo(
                        f"Progresso: {processed}/{total} pontos processados "
                        f"({sampled_count} amostras, {error_count} erros)"
                    )

        # Reprojeta saida se necessario (via VectorLayerProjection)
        if needs_reproject and features_buffer:
            feedback.pushInfo(
                f"Reprojetando {len(features_buffer)} pontos de "
                f"{source_crs.authid()} para {output_crs.authid()}..."
            )
            self.logger.info(
                f"Reprojetando {len(features_buffer)} features via VectorLayerProjection"
            )
            reprojected = VectorLayerProjection.reproject_features(
                features_buffer, source_crs, output_crs, context
            )
            for f in reprojected:
                sink.addFeature(f, QgsFeatureSink.FastInsert)

        feedback.pushInfo(
            f"Resumo: {processed} pontos processados, "
            f"{sampled_count} amostras coletadas, "
            f"{error_count} erros de amostragem"
        )
        self.logger.info(
            f"Amostragem concluida: {processed} pontos, "
            f"{sampled_count} amostras, {error_count} erros"
        )

        # Preferencias
        self.prefs.update(
            {
                "display_help": bool(display_help),
                "open_output_folder": bool(open_output_folder),
                "last_rasters_count": len(rasters),
                "last_points_count": total,
            }
        )

        if dest and isinstance(dest, str) and not dest.startswith("memory:"):
            out_folder = os.path.dirname(dest)
            feedback.pushInfo(f"{STR.FILE_SAVED_IN} {out_folder}")
            self.prefs.update(
                {"last_output_folder": out_folder, "last_output_file": dest}
            )
            if open_output_folder:
                self.open_folder_in_explorer(out_folder)

        self.save_preferences()
        return {self.OUTPUT: dest}

    def build_output_fields(self, pts, rasters, max_len: int = 10):
        out_fields = QgsFields()
        try:
            for f in pts.fields():
                out_fields.append(f)
        except Exception as e:
            self.logger.error(
                f"Erro ao construir campos de saida a partir dos pontos: {e}")
            if isinstance(pts, QgsFields):
                for f in pts:
                    out_fields.append(f)

        raster_fields = []
        for ras in rasters:
            layer_name = ras.name() if hasattr(ras, "name") else str(ras)
            candidate = self._sanitize_field_name(
                layer_name, raster_fields, max_len=max_len
            )
            raster_fields.append(candidate)
            out_fields.append(QgsField(candidate, QVariant.Double))

        self.logger.debug(
            f"Campos de saida: {len(out_fields)} totais "
            f"({len(raster_fields)} rasters, {len(out_fields) - len(raster_fields)} originais)"
        )
        return out_fields, raster_fields

    def _sanitize_field_name(
        self, layer_name: str, existing: list, max_len: int = 10
    ) -> str:
        field_base = re.sub(r"[^0-9A-Za-z_]", "_", layer_name)
        candidate = field_base[:max_len]
        if candidate in existing:
            i = 1
            while True:
                suffix = f"_{i}"
                avail_len = max_len - len(suffix)
                new_candidate = (
                    (field_base[:avail_len] + suffix)
                    if avail_len > 0
                    else (field_base[:max_len])
                )
                if new_candidate not in existing:
                    candidate = new_candidate
                    break
                i += 1
        return candidate

    def build_transforms(self, pts, rasters, context):
        effective_pts_crs = None
        try:
            effective_pts_crs = pts.sourceCrs()
            if not effective_pts_crs.isValid():
                self.logger.warning(
                    "CRS da camada de pontos nao e valido, transformacoes serao identity")
                effective_pts_crs = None
        except Exception as e:
            self.logger.error(f"Erro ao obter CRS da camada de pontos: {e}")
            effective_pts_crs = None

        transforms = []
        for ras in rasters:
            ras_crs = ras.crs()
            if not ras_crs.isValid():
                self.logger.warning(
                    f"Raster {ras.name()} sem CRS valido, transformacao sera identity"
                )
                transforms.append(None)
                continue

            if effective_pts_crs and effective_pts_crs.isValid():
                try:
                    ct = QgsCoordinateTransform(
                        effective_pts_crs, ras_crs, context.transformContext()
                    )
                    transforms.append(ct)
                except Exception as e:
                    self.logger.error(
                        f"Erro ao criar transformacao para raster {ras.name()}: {e}",
                        code="TRANSFORM_CREATE_ERROR",
                    )
                    transforms.append(None)
            else:
                transforms.append(None)

        self.logger.debug(
            f"Transformacoes criadas: {len(transforms)} "
            f"({sum(1 for t in transforms if t is not None)} validas)"
        )
        return transforms

    def write_sink(self, params, context, out_fields, features, pts, feedback):
        sink, dest = self.parameterAsSink(
            params, self.OUTPUT, context, out_fields, pts.wkbType(), pts.sourceCrs()
        )

        for f in features:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        if dest and isinstance(dest, str) and not dest.startswith("memory:"):
            out_folder = os.path.dirname(dest)
            feedback.pushInfo(f"{STR.FILE_SAVED_IN} {out_folder}")

            display_help = (
                bool(self.parameterAsBool(params, self.DISPLAY_HELP, context))
                if self.DISPLAY_HELP in params
                else False
            )
            open_output_folder = (
                bool(self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context))
                if self.OPEN_OUTPUT_FOLDER in params
                else True
            )
            self.prefs.update(
                {
                    "last_output_folder": out_folder,
                    "last_output_file": dest,
                    "display_help": display_help,
                    "open_output_folder": open_output_folder,
                }
            )
            self.save_preferences()

            if open_output_folder:
                self.open_folder_in_explorer(out_folder)

        return {self.OUTPUT: dest}
