# -*- coding: utf-8 -*-
from pathlib import Path
from qgis.core import (
    QgsVectorFileWriter,
    QgsWkbTypes,
    QgsVectorLayer,
)
from typing import Optional, Tuple
import os
import tempfile
import time
from ..StringManager import StringManager
from ...core.config.LogUtils import LogUtils
from ..ToolKeys import ToolKey
from ..ProjectUtils import ProjectUtils


class VectorLayerSource:
    """
    Responsável pela entrada, saída e origem de camadas vetoriais.

    Escopo:
    - Carregar camadas vetoriais de diferentes fontes
    - Salvar camadas em diferentes formatos
    - Validar integridade de camadas
    - Clonar camadas existentes
    - Gerenciar origem de dados (arquivo, banco, memória)

    Responsabilidade Principal:
    - Orquestrar operações de I/O de camadas vetoriais
    - Garantir que camadas sejam carregadas e salvas corretamente
    - Validar antes de operações críticas

    Logging Strategy (Métodos Estáticos):
    - Helper method: _get_logger(tool_key) centraliza criação de instâncias LogUtils
    - Benefícios: Thread-safe, flexível (tool_key customizável), sem estado global
    """

    @staticmethod
    def _get_logger(tool_key: str = ToolKey.UNTRACEABLE) -> LogUtils:
        """Helper para obter logger com tool_key específico.

        Parameters
        ----------
        tool_key : str
            Identificador da ferramenta (padrão: 'untraceable')

        Returns
        -------
        LogUtils
            Instância de logger configurada para a classe
        """
        return LogUtils(tool=tool_key, class_name="VectorLayerSource")

    # ------------------------------------------------------------------
    # SAVE VECTOR LAYER (UNIFICADO E BIG-DATA SAFE)
    # ------------------------------------------------------------------
    @staticmethod
    def save_vector_layer(
        layer: QgsVectorLayer,
        *,
        save_to_folder: bool = False,
        output_path: Optional[str] = None,
        output_name: Optional[str] = None,
        decision: str = "rename",
        external_tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Optional[QgsVectorLayer]:

        logger = VectorLayerSource._get_logger(external_tool_key)
        logger.debug(
            f"save_vector_layer(layer={layer}, save_to_folder={save_to_folder}, output_path={output_path}, output_name={output_name}, decision={decision})"
        )

        if not layer or not layer.isValid():
            logger.critical("Camada inválida para salvamento.")
            return None

        # ==========================================================
        # CASO 1 — MEMÓRIA
        # ==========================================================
        if not save_to_folder:
            layer_name = output_name or layer.name()

            logger.info(f"Criando camada em memória: {layer_name}")

            memory_layer = QgsVectorLayer(
                f"{QgsWkbTypes.displayString(layer.wkbType())}?crs={layer.crs().authid()}",
                layer_name,
                "memory",
            )

            provider = memory_layer.dataProvider()
            provider.addAttributes(layer.fields())
            memory_layer.updateFields()
            provider.addFeatures(layer.getFeatures())
            memory_layer.updateExtents()

            return memory_layer

        # ==========================================================
        # CASO 2 — DISCO (NOME VEM DO USUÁRIO VIA output_path)
        # ==========================================================
        if not output_path:
            logger.critical("output_path é obrigatório quando save_to_folder=True.")
            return None

        ext = os.path.splitext(output_path)[1].lower()
        driver = StringManager.VECTOR_DRIVERS.get(ext)

        if not driver:
            logger.critical(f"Formato não suportado: {ext}")
            return None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_path = output_path

        # ----------------------------
        # Rename
        # ----------------------------
        if decision == "rename" and os.path.exists(final_path):
            final_path = VectorLayerSource.generate_incremental_path(final_path)

        # ----------------------------
        # Overwrite
        # ----------------------------
        elif decision == "overwrite" and os.path.exists(final_path):
            try:
                os.remove(final_path)
            except Exception as e:
                logger.critical(f"Erro ao remover arquivo existente: {e}")
                return None

        # ----------------------------
        # Escrita (Compatível 3.16)
        # ----------------------------
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = driver
        options.fileEncoding = "UTF-8"

        # IMPORTANTE:
        # Nome da camada dentro do arquivo vem do nome original
        # (não sobrescrevemos com output_name)
        options.layerName = layer.name()

        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

        transform_context = ProjectUtils.get_project_instance().transformContext()

        result, error_message = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer, final_path, transform_context, options
        )

        if result != QgsVectorFileWriter.NoError:
            logger.critical(
                f"Erro ao salvar camada | Código={result} | Msg={error_message}"
            )
            return None

        saved_layer = QgsVectorLayer(
            final_path,
            Path(final_path).stem,  # nome vem do arquivo escolhido pelo usuário
            "ogr",
        )

        if not saved_layer.isValid():
            logger.critical("Camada salva mas não carregou corretamente.")
            return None

        logger.info("Camada salva com sucesso.")

        return saved_layer

    @staticmethod
    def save_layer_to_path(
        layer: QgsVectorLayer,
        output_path: str,
        tool_key: str = ToolKey.UNTRACEABLE,
        decision: str = "rename",
    ) -> Optional[str]:
        """Salva layer em arquivo e retorna o caminho efetivo salvo."""
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(
            f"save_layer_to_path(layer={layer}, output_path={output_path}, decision={decision})"
        )
        if not layer or not layer.isValid() or not output_path:
            return None

        path = output_path
        if os.path.exists(path) and decision == "rename":
            path = VectorLayerSource.generate_incremental_path(path)

        saved = VectorLayerSource.save_vector_layer(
            layer,
            save_to_folder=True,
            output_path=path,
            decision="overwrite",
            external_tool_key=tool_key,
        )

        if saved:
            return path
        return None

    @staticmethod
    def save_and_load_layer(
        layer: QgsVectorLayer,
        output_path: str,
        tool_key: str = ToolKey.UNTRACEABLE,
        decision: str = "rename",
    ) -> Optional[QgsVectorLayer]:
        """Salva layer e retorna a camada carregada do arquivo salvo."""
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(
            f"save_and_load_layer(layer={layer}, output_path={output_path}, decision={decision})"
        )
        if not layer or not layer.isValid() or not output_path:
            return None

        path = output_path
        if os.path.exists(path) and decision == "rename":
            path = VectorLayerSource.generate_incremental_path(path)

        return VectorLayerSource.save_vector_layer(
            layer,
            save_to_folder=True,
            output_path=path,
            decision="overwrite",
            external_tool_key=tool_key,
        )

    @staticmethod
    def load_existing_vector_layer(
        file_path: str, tool_key: str = ToolKey.UNTRACEABLE
    ) -> Optional[QgsVectorLayer]:
        """Carrega camada vetorial existente a partir de um caminho no disco."""
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(f"load_existing_vector_layer(file_path={file_path})")
        return VectorLayerSource().load_vector_layer_from_file(
            file_path, external_tool_key=tool_key
        )

    @staticmethod
    def get_layer_file_size(
        layer: QgsVectorLayer, tool_key: str = ToolKey.UNTRACEABLE
    ) -> int:
        """Retorna tamanho em bytes do datasource se for arquivo"""
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(f"get_layer_file_size(layer={layer})")
        try:
            src = layer.source()
            if not src:
                return 0

            # remover parâmetros tipo "|layername="
            path = src.split("|")[0]

            if os.path.exists(path):
                return os.path.getsize(path)
        except Exception as e:
            logger.error(f"Erro ao obter tamanho do arquivo da camada: {e}")
            return 0
        return 0

    @staticmethod
    def get_extension(path: str, tool_key: str = ToolKey.UNTRACEABLE) -> str:
        """Retorna a extensao do caminho normalizado."""
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(f"get_extension(path={path})")

        if not path:
            logger.debug("Caminho vazio ao obter extensao")
            return ""

        normalized_path = str(path).split("|", 1)[0].strip().lower()
        extension = os.path.splitext(normalized_path)[1]
        logger.debug(f"Extensao resolvida para '{path}': {extension}")
        return extension

    @staticmethod
    def export_temp_layer(
        layer: QgsVectorLayer,
        prefix: str = "tmp_layer",
        external_tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Optional[str]:
        logger = VectorLayerSource._get_logger(external_tool_key)
        logger.debug(f"export_temp_layer(layer={layer}, prefix={prefix})")

        if not layer or not layer.isValid():
            return None

        tmp_dir = tempfile.mkdtemp(prefix=prefix)
        output_path = os.path.join(tmp_dir, f"{prefix}.gpkg")

        return VectorLayerSource.save_vector_layer(
            layer=layer,
            output_path=output_path,
            decision="overwrite",
            external_tool_key=external_tool_key,
        )

    @staticmethod
    def delete_shapefile_set(
        base_path, retries=5, delay=0.3, tool_key: str = ToolKey.UNTRACEABLE
    ):
        """
        base_path = caminho do .shp
        """
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(
            f"delete_shapefile_set(base_path={base_path}, retries={retries}, delay={delay})"
        )
        folder = os.path.dirname(base_path)
        base = os.path.splitext(os.path.basename(base_path))[0]

        for attempt in range(retries):
            errors = []
            for ext in StringManager.SHP_EXTENSIONS:
                f = os.path.join(folder, base + ext)
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        logger.error(
                            f"Erro removendo arquivo do shapefile set: {f} | {e}"
                        )
                        errors.append((f, str(e)))

            if not errors:
                return True

            time.sleep(delay)

        return False

    @staticmethod
    def generate_incremental_path(path, tool_key: str = ToolKey.UNTRACEABLE):
        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(f"generate_incremental_path(path={path})")
        folder = os.path.dirname(path)
        name, ext = os.path.splitext(os.path.basename(path))

        counter = 1
        new_path = path
        while os.path.exists(new_path):
            new_path = os.path.join(folder, f"{name}_{counter}{ext}")
            counter += 1

        return new_path

    # ------------------------------------------------------------------
    # VALIDAÇÃO CENTRALIZADA
    # ------------------------------------------------------------------
    @staticmethod
    def validate_layer(
        layer: QgsVectorLayer,
        *,
        expected_geometry: Optional[int] = None,
        require_editable: bool = False,
        tool_key: str = ToolKey.UNTRACEABLE,
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida camada vetorial com regras padronizadas.

        Retorna:
            (True, None) se OK
            (False, "mensagem erro") se inválida
        """

        logger = VectorLayerSource._get_logger(tool_key)
        logger.debug(
            f"validate_layer(layer={layer}, expected_geometry={expected_geometry}, require_editable={require_editable})"
        )

        if not layer:
            return False, "Nenhuma camada foi informada."

        if not isinstance(layer, QgsVectorLayer):
            return False, "Objeto informado não é uma camada vetorial."

        if not layer.isValid():
            return False, "Camada inválida."

        if expected_geometry is not None:
            if layer.geometryType() != expected_geometry:
                expected_name = QgsWkbTypes.displayString(expected_geometry)
                current_name = QgsWkbTypes.displayString(layer.geometryType())
                return False, (
                    f"Tipo de geometria inválido.\n"
                    f"Esperado: {expected_name}\n"
                    f"Atual: {current_name}"
                )

        if require_editable and not layer.isEditable():
            return False, "A camada precisa estar em modo de edição."

        return True, None

    def load_vector_layer_from_file(
        self, file_path, external_tool_key=ToolKey.UNTRACEABLE
    ):
        """Carrega uma camada vetorial de um arquivo no disco."""
        logger = VectorLayerSource._get_logger(external_tool_key)
        logger.debug(f"load_vector_layer_from_file(file_path={file_path})")
        try:
            if not file_path or not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                return None

            name = Path(file_path).stem
            layer = QgsVectorLayer(file_path, name, "ogr")
            if not layer or not layer.isValid():
                logger.error(f"Falha ao carregar camada: {file_path}")
                return None
            logger.info(f"Camada vetorial carregada: {file_path}")
            return layer
        except Exception as e:
            logger.error(f"Erro carregando layer {file_path}: {e}")
            return None

    @staticmethod
    def load_vector_layer_from_source_path(
        source_path: str,
        layer_name: str = "",
        external_tool_key=ToolKey.UNTRACEABLE,
    ):
        """Carrega camada vetorial a partir da source completa do QGIS."""
        logger = VectorLayerSource._get_logger(external_tool_key)
        logger.debug(
            f"load_vector_layer_from_source_path(source_path={source_path}, layer_name={layer_name})"
        )

        try:
            if not source_path:
                logger.error("Source path vazio")
                return None

            normalized_name = layer_name or Path(source_path.split("|", 1)[0]).stem
            layer = QgsVectorLayer(source_path, normalized_name, "ogr")
            if not layer or not layer.isValid():
                logger.error(
                    f"Falha ao carregar camada a partir de source path: {source_path}"
                )
                return None

            logger.info(f"Camada vetorial carregada por source path: {source_path}")
            return layer
        except Exception as e:
            logger.error(f"Erro carregando camada por source path {source_path}: {e}")
            return None
