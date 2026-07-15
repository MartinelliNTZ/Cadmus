# -*- coding: utf-8 -*-
from ...core.config.LogUtils import LogUtils
from qgis.core import QgsRasterLayer
from pathlib import Path
import os

from ..ProjectUtils import ProjectUtils


class RasterLayerSource:
    """
    ResponsÃ¡vel pelo carregamento, salvamento e criaÃ§Ã£o de camadas raster.

    Escopo:
    - Carregar rasters de diferentes fontes
    - Criar rasters novos em memÃ³ria
    - Salvar rasters em diferentes formatos
    - Validar arquivos raster
    - Gerenciar bandas e nodata

    Responsabilidade Principal:
    - Orquestrar operaÃ§Ãµes de I/O de rasters
    - Garantir integridade de dados raster
    - Validar bandas e valores nodata

    NÃƒO Ã© Responsabilidade:
    - Reprojetar rasters (use RasterLayerProjection)
    - Processar pixels (use RasterLayerProcessing)
    - Calcular estatÃ­sticas (use RasterLayerMetrics)
    - Alterar visualizaÃ§Ã£o (use RasterLayerRendering)
    """

    GOOGLE_BASEMAP_VARIANTS = {
        "hybrid": {"lyrs": "y", "label": "Google Hybrid"},
        "satellite": {"lyrs": "s", "label": "Google Satellite"},
        "road": {"lyrs": "m", "label": "Google Road"},
    }

    def load_raster_from_file(self, file_path, external_tool_key="untraceable"):
        """Carrega um raster de um arquivo GeoTIFF, IMG, ou outro formato suportado."""

        logger = LogUtils(tool=external_tool_key, class_name="RasterLayerSource")
        try:
            if not file_path or not os.path.exists(file_path):
                logger.error(f"Raster nÃ£o encontrado: {file_path}")
                return None

            name = Path(file_path).stem
            layer = QgsRasterLayer(file_path, name)
            if not layer or not layer.isValid():
                logger.error(f"Falha ao carregar raster: {file_path}")
                return None
            logger.info(f"Raster carregado: {file_path}")
            return layer
        except Exception as e:
            logger.error(f"Erro carregando raster {file_path}: {e}")
            return None

    def load_raster_from_url(
        self,
        url,
        cache_directory=None,
        external_tool_key="untraceable",
        layer_name=None,
        provider_key="wms",
    ):
        """Carrega raster remoto (ex.: XYZ/WMS) a partir de URL/URI."""
        logger = LogUtils(tool=external_tool_key, class_name="RasterLayerSource")
        try:
            if not url:
                logger.error("URL/URI raster vazia")
                return None

            resolved_name = layer_name or "Remote Raster"
            layer = QgsRasterLayer(url, resolved_name, provider_key)
            if not layer or not layer.isValid():
                logger.error(f"Falha ao carregar raster remoto: {resolved_name}")
                return None

            logger.info(f"Raster remoto carregado: {resolved_name}")
            return layer
        except Exception as e:
            logger.error(f"Erro ao carregar raster remoto: {e}")
            return None

    def _build_google_xyz_uri(self, basemap_style: str) -> str:
        style_key = (basemap_style or "hybrid").strip().lower()
        variant = self.GOOGLE_BASEMAP_VARIANTS.get(
            style_key, self.GOOGLE_BASEMAP_VARIANTS["hybrid"]
        )
        return (
            "type=xyz&zmin=0&zmax=21&"
            f"url=https://mt1.google.com/vt/lyrs={variant['lyrs']}"
            "%26x=%7Bx%7D%26y=%7By%7D%26z=%7Bz%7D"
        )

    def add_google_basemap(
        self,
        project,
        basemap_style: str = "hybrid",
        external_tool_key="untraceable",
        layer_name: str = None,
    ):
        """Adiciona camada base Google (hybrid/satellite/road) evitando duplicidade."""
        logger = LogUtils(tool=external_tool_key, class_name="RasterLayerSource")
        try:
            style_key = (basemap_style or "hybrid").strip().lower()
            variant = self.GOOGLE_BASEMAP_VARIANTS.get(
                style_key, self.GOOGLE_BASEMAP_VARIANTS["hybrid"]
            )
            resolved_name = layer_name or variant["label"]

            existing_names = ProjectUtils.project_layer_names(project)
            if resolved_name in existing_names:
                logger.debug(
                    f"Camada base Google ja existe no projeto: {resolved_name}"
                )
                return None

            layer = self.load_raster_from_url(
                self._build_google_xyz_uri(style_key),
                external_tool_key=external_tool_key,
                layer_name=resolved_name,
                provider_key="wms",
            )
            if not layer or not layer.isValid():
                logger.warning(
                    f"Falha ao criar camada base Google ({style_key}) via XYZ"
                )
                return None

            ProjectUtils.add_layer(layer, add_to_root=True, project=project)
            logger.info(f"Camada base Google adicionada ao projeto: {resolved_name}")
            return layer
        except Exception as e:
            logger.error(f"Erro ao adicionar basemap Google: {e}")
            return None

    def create_empty_raster(
        self, width, height, crs, extent, pixel_size, external_tool_key="untraceable"
    ):
        """Cria um raster vazio em memÃ³ria com dimensÃµes e CRS especificados."""
        pass

    def save_raster_to_file(
        self, raster, output_path, format, compression, external_tool_key="untraceable"
    ):
        """Salva um raster em arquivo com formato e compressÃ£o especificados."""
        pass

    def get_raster_bands_info(self, raster, external_tool_key="untraceable"):
        """Retorna informaÃ§Ãµes sobre as bandas do raster (quantidade, tipo)."""
        pass

    def validate_raster_file(self, file_path, external_tool_key="untraceable"):
        """Valida se um arquivo raster estÃ¡ corrompido ou inacessÃ­vel."""
        pass

    def get_raster_nodata_value(
        self, raster, band_index, external_tool_key="untraceable"
    ):
        """ObtÃ©m o valor de nodata de uma banda raster especÃ­fica."""
        pass

    def set_raster_nodata_value(
        self, raster, band_index, nodata_value, external_tool_key="untraceable"
    ):
        """Define o valor de nodata para uma banda raster."""
        pass

    def copy_raster_structure(
        self, source_raster, output_path, external_tool_key="untraceable"
    ):
        """Cria um novo raster com a mesma estrutura mas sem dados."""
        pass

    def clone_raster(self, source_raster, external_tool_key="untraceable"):
        """Cria uma cÃ³pia completa de um raster em memÃ³ria."""
        pass

    def get_raster_file_size(self, file_path, external_tool_key="untraceable"):
        """ObtÃ©m o tamanho do arquivo raster em bytes."""
        pass

    def export_raster_metadata(
        self, raster, output_path, external_tool_key="untraceable"
    ):
        """Exporta metadados do raster para arquivo de documentaÃ§Ã£o."""
        pass
