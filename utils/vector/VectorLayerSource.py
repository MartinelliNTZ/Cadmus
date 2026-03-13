from pathlib import Path
from qgis.core import (
            QgsVectorFileWriter,
            QgsProject,
            QgsVectorLayer,
            QgsWkbTypes,
            QgsFeatureRequest,
            QgsVectorLayer,
        QgsVectorFileWriter,
        QgsProject,
        )
from typing import Optional, Tuple 
import os
import tempfile 
import time
from ...utils.StringUtils import StringUtils
from ...utils.ProjectUtils import ProjectUtils
from ...core.config.LogUtils import LogUtils
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
    - Helper method: _get_logger(tool_key) centraliza criação de instâncias LogUtilsNew
    - Benefícios: Thread-safe, flexível (tool_key customizável), sem estado global
    """

    @staticmethod
    def _get_logger(tool_key: str = "untraceable") -> LogUtils:
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
            external_tool_key: str = "untraceable"
    ) -> Optional[QgsVectorLayer]:

        logger = VectorLayerSource._get_logger(external_tool_key)

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
                "memory"
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
        driver = StringUtils.VECTOR_DRIVERS.get(ext)

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

        transform_context = QgsProject.instance().transformContext()

        result, error_message = QgsVectorFileWriter.writeAsVectorFormatV2(
            layer,
            final_path,
            transform_context,
            options
        )

        if result != QgsVectorFileWriter.NoError:
            logger.critical(f"Erro ao salvar camada | Código={result} | Msg={error_message}")
            return None

        saved_layer = QgsVectorLayer(
            final_path,
            Path(final_path).stem,  # nome vem do arquivo escolhido pelo usuário
            "ogr"
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
        tool_key: str = "untraceable",
        decision: str = "rename",
    ) -> Optional[str]:
        """Salva layer em arquivo e retorna o caminho efetivo salvo."""
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
        tool_key: str = "untraceable",
        decision: str = "rename",
    ) -> Optional[QgsVectorLayer]:
        """Salva layer e retorna a camada carregada do arquivo salvo."""
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
    def get_layer_file_size( layer: QgsVectorLayer) -> int:
        """Retorna tamanho em bytes do datasource se for arquivo"""
        try:
            src = layer.source()
            if not src:
                return 0

            # remover parâmetros tipo "|layername="
            path = src.split("|")[0]

            if os.path.exists(path):
                return os.path.getsize(path)
        except Exception:
            pass
        return 0

    @staticmethod
    def export_temp_layer(
        layer: QgsVectorLayer,
        prefix: str = "tmp_layer",
        external_tool_key: str = "untraceable"
    ) -> Optional[str]:

        if not layer or not layer.isValid():
            return None

        tmp_dir = tempfile.mkdtemp(prefix=prefix)
        output_path = os.path.join(tmp_dir, f"{prefix}.gpkg")

        return VectorLayerSource.save_vector_layer(
            layer=layer,
            output_path=output_path,
            decision="overwrite",
            external_tool_key=external_tool_key
        )

    @staticmethod
    def delete_shapefile_set(base_path, retries=5, delay=0.3):
        """
        base_path = caminho do .shp
        """
        folder = os.path.dirname(base_path)
        base = os.path.splitext(os.path.basename(base_path))[0]

        for attempt in range(retries):
            errors = []
            for ext in StringUtils.SHP_EXTENSIONS:
                f = os.path.join(folder, base + ext)
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        errors.append((f, str(e)))

            if not errors:
                return True

            time.sleep(delay)

        return False

    @staticmethod
    def generate_incremental_path(path):
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
        require_editable: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida camada vetorial com regras padronizadas.

        Retorna:
            (True, None) se OK
            (False, "mensagem erro") se inválida
        """

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




    def load_vector_layer_from_file(self, file_path, external_tool_key="untraceable"):
        """Carrega uma camada vetorial de um arquivo no disco."""
        logger = VectorLayerSource._get_logger(external_tool_key)
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

    def load_vector_layer_from_database(self, connection_string, layer_name, external_tool_key="untraceable"):
        """Carrega uma camada vetorial de um banco de dados."""
        pass

    def create_memory_layer(self, layer_name, geometry_type, crs, external_tool_key="untraceable"):
        """Cria uma camada vetorial em memória com geometria e CRS especificados."""
        pass


    def save_vector_layer_to_database(self, layer, connection_string, table_name, external_tool_key="untraceable"):
        """Salva uma camada vetorial em um banco de dados."""
        pass

    def clone_vector_layer(self, source_layer, include_features, external_tool_key="untraceable"):
        """Cria uma cópia exata de uma camada vetorial com ou sem feições."""
        pass

    def validate_layer_integrity(self, layer, external_tool_key="untraceable"):
        """Verifica se a camada está válida e íntegra para operações."""
        pass

    def get_layer_source_uri(self, layer, external_tool_key="untraceable"):
        """Obtém a URI ou caminho completo da origem da camada."""
        pass

    def check_file_format_compatibility(self, file_path, target_format, external_tool_key="untraceable"):
        """Verifica se o arquivo pode ser convertido para o formato desejado."""
        pass

    def reload_layer_from_source(self, layer, external_tool_key="untraceable"):
        """Recarrega a camada a partir de sua fonte original."""
        pass

    def export_layer_statistics(self, layer, output_path, external_tool_key="untraceable"):
        """Exporta estatísticas básicas da camada para arquivo de relatório."""
        pass

    def validate_geometry_before_save(self, layer, external_tool_key="untraceable"):
        """Valida geometrias da camada antes de salvar para evitar corrupção."""
        pass
