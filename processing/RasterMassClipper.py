# -*- coding: utf-8 -*-
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import processing
from qgis.core import (
    QgsCoordinateTransform,
    QgsGeometry,
    QgsProcessing,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterMultipleLayers,
    QgsProject,
    QgsVectorLayer,
)

from ..core.config.LogUtils import LogUtils
from ..i18n.TranslationManager import STR
from ..resources.IconManager import IconManager as im
from ..utils.ToolKeys import ToolKey
from .BaseProcessingAlgorithm import BaseProcessingAlgorithm


class RasterMassClipper(BaseProcessingAlgorithm):

    TOOL_KEY = ToolKey.RASTER_MASS_CLIPPER
    ALGORITHM_NAME = "raster_mass_clipper"
    ALGORITHM_DISPLAY_NAME = STR.RASTER_MASS_CLIPPER_TITLE
    ALGORITHM_GROUP = BaseProcessingAlgorithm.GROUP_RASTER
    INSTRUCTIONS_FILE = "raster_mass_clipper.html"
    logger = LogUtils(tool=TOOL_KEY, class_name="RasterMassClipper", level="DEBUG")
    ICON = im.RASTER_MASS_CLIPPER
    INPUT_MASK = "INPUT_MASK"
    INPUT_RASTERS = "INPUT_RASTERS"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"
    PER_FEATURE = "PER_FEATURE"
    BUFFER_FIX = "BUFFER_FIX"
    DISPLAY_HELP = "DISPLAY_HELP"
    OPEN_OUTPUT_FOLDER = "OPEN_OUTPUT_FOLDER"

    def initAlgorithm(self, config=None):
        self.logger.debug("Inicializando algoritmo RasterMassClipperâ€¦")

        self.load_preferences()

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_MASK,
                STR.INPUT_MASK_POLYGON_LAYER,
                [QgsProcessing.TypeVectorPolygon],
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
            QgsProcessingParameterBoolean(
                self.PER_FEATURE,
                STR.CLIP_PER_EACH_POLYGON,
                defaultValue=self.prefs.get("per_feature", False),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.BUFFER_FIX,
                STR.APPLY_CORRECTION_BUFFER_PIXEL_1_1,
                defaultValue=self.prefs.get("buffer_fix", True),
            )
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

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                STR.OUTPUT_FOLDER,
                defaultValue=self.prefs.get("last_output_folder", ""),
            )
        )

    def processAlgorithm(self, params, context, feedback):
        mask_layer = self.parameterAsVectorLayer(params, self.INPUT_MASK, context)
        rasters = self.parameterAsLayerList(params, self.INPUT_RASTERS, context)
        out_folder = self.parameterAsString(params, self.OUTPUT_FOLDER, context)

        per_feature = self.parameterAsBool(params, self.PER_FEATURE, context)
        buffer_fix = self.parameterAsBool(params, self.BUFFER_FIX, context)
        open_output_folder = self.parameterAsBool(params, self.OPEN_OUTPUT_FOLDER, context)
        display_help = (
            bool(self.parameterAsBool(params, self.DISPLAY_HELP, context))
            if self.DISPLAY_HELP in params
            else False
        )
        self.logger.debug(
            f"ParÃ¢metros: {per_feature}, Buffer fix: {buffer_fix}, Output folder: {out_folder}, Rasters: {[r.name() for r in rasters]}"
        )

        os.makedirs(out_folder, exist_ok=True)

        tasks = []

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            if per_feature:
                for feat in mask_layer.getFeatures():
                    for ras in rasters:
                        tasks.append(
                            executor.submit(
                                self.clip_raster_feature,
                                ras,
                                feat.geometry(),
                                feat.id(),
                                mask_layer,
                                out_folder,
                                buffer_fix,
                                context,
                            )
                        )
            else:
                for ras in rasters:
                    tasks.append(
                        executor.submit(
                            self.clip_raster_layer,
                            ras,
                            mask_layer,
                            out_folder,
                            buffer_fix,
                            context,
                        )
                    )

            for future in as_completed(tasks):
                if feedback.isCanceled():
                    break

                try:
                    future.result()
                except Exception as e:
                    feedback.pushInfo(str(e))
                    self.logger.error(f"Erro ao processar tarefa: {e}")

        self.prefs.update(
            {
                "last_output_folder": out_folder,
                "per_feature": bool(per_feature),
                "buffer_fix": bool(buffer_fix),
                "display_help": display_help,
                "open_output_folder": bool(open_output_folder),
            }
        )
        self.save_preferences()

        if open_output_folder:
            self.open_folder_in_explorer(out_folder)

        return {self.OUTPUT_FOLDER: out_folder}

    def clip_raster_layer(self, raster, mask_layer, out_folder, buffer_fix, context):
        raster_path = raster.source()
        base = os.path.splitext(os.path.basename(raster_path))[0]

        mask = self.prepare_mask(mask_layer, raster)

        if buffer_fix:
            pixel = abs(raster.rasterUnitsPerPixelX())
            buffer_dist = pixel * 1.1

            self.logger.debug(f"Aplicando buffer {buffer_dist} na layer inteira")

            buffered = QgsVectorLayer(
                f"Polygon?crs={raster.crs().authid()}",
                "mask_buffer",
                "memory",
            )

            prov = buffered.dataProvider()
            feats = []

            for f in mask.getFeatures():
                g = f.geometry().buffer(buffer_dist, 5)
                nf = f
                nf.setGeometry(g)
                feats.append(nf)

            prov.addFeatures(feats)
            buffered.updateExtents()
            mask = buffered

        out_path = os.path.join(out_folder, f"{base}_clip.tif")

        processing.run(
            "gdal:cliprasterbymasklayer",
            {
                "INPUT": raster_path,
                "MASK": mask,
                "CROP_TO_CUTLINE": True,
                "KEEP_RESOLUTION": True,
                "OUTPUT": out_path,
            },
            context=context,
        )

    def clip_raster_feature(
        self, raster, geom, feat_id, mask_layer, out_folder, buffer_fix, context
    ):
        raster_path = raster.source()
        base = os.path.splitext(os.path.basename(raster_path))[0]

        geom = self.reproject_geom(geom, mask_layer.crs(), raster.crs())

        if buffer_fix:
            pixel = abs(raster.rasterUnitsPerPixelX())
            buffer_dist = pixel * 1.1
            geom = geom.buffer(buffer_dist, 5)
            self.logger.debug(f"Buffer feature {feat_id}: {buffer_dist}")

        mem_layer = QgsVectorLayer(
            f"Polygon?crs={raster.crs().authid()}",
            "mask",
            "memory",
        )

        prov = mem_layer.dataProvider()
        feat = self.geom_to_feature(geom)
        prov.addFeature(feat)
        mem_layer.updateExtents()

        out_path = os.path.join(out_folder, f"{base}_feat_{feat_id}.tif")

        processing.run(
            "gdal:cliprasterbymasklayer",
            {
                "INPUT": raster_path,
                "MASK": mem_layer,
                "CROP_TO_CUTLINE": True,
                "KEEP_RESOLUTION": True,
                "OUTPUT": out_path,
            },
            context=context,
        )

    def reproject_geom(self, geom, src_crs, dst_crs):
        if geom is None:
            return None

        if src_crs == dst_crs:
            return geom

        transform = QgsCoordinateTransform(
            src_crs,
            dst_crs,
            QgsProject.instance(),
        )

        if hasattr(geom, "clone"):
            g = geom.clone()
        else:
            g = QgsGeometry.fromWkt(geom.asWkt())

        try:
            g.transform(transform)
        except Exception as e:
            self.logger.error(f"Falha ao reprojetar geometria: {e}")
            return geom

        return g

    def geom_to_feature(self, geom):
        from qgis.core import QgsFeature

        f = QgsFeature()
        f.setGeometry(geom)
        return f

    def prepare_mask(self, layer, raster):
        crs = raster.crs()

        if layer.crs() == crs:
            return layer

        self.logger.debug(
            f"Reprojetando mÃ¡scara {layer.crs().authid()} -> {crs.authid()}"
        )

        params = {
            "INPUT": layer,
            "TARGET_CRS": crs,
            "OUTPUT": "memory:",
        }

        result = processing.run("native:reprojectlayer", params)

        return result["OUTPUT"]
