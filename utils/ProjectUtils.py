# -*- coding: utf-8 -*-
import os
import shutil
from datetime import datetime
from pathlib import Path
from qgis.core import QgsProject, QgsMapLayer, QgsVectorLayer
from qgis.PyQt.QtWidgets import QApplication
from ..core.config.LogUtils import LogUtils
from pathlib import Path
import gc
from pathlib import Path
from typing import Union, Optional
from qgis.core import QgsMapLayer




class ProjectUtils:
    @staticmethod
    def get_active_vector_layer(layer, logger=None, require_editable=False):
        """Valida camada vetorial ativa.
        Recebe: layer, logger, require_editable (bool).
        Retorna: QgsVectorLayer ou None.
        Não acessa iface nem exibe mensagens.
        """
        from qgis.core import QgsVectorLayer
        if logger:
            logger.debug(f"Validando camada vetorial ativa. Require editable: {require_editable}")
        if not layer or not isinstance(layer, QgsVectorLayer):
            if logger:
                logger.debug("Camada ativa inválida ou não é vetorial")
            return None
        if require_editable and not ProjectUtils.ensure_editable(layer, logger):
            return None
        return layer

    @staticmethod
    def ensure_editable(layer, logger=None):
        """Verifica se a camada está em modo edição.
        Recebe: layer (QgsVectorLayer), logger.
        Retorna: bool.
        Não acessa iface nem exibe mensagens.
        """
        if logger:
            logger.debug(f"Verificando se camada está em edição: {layer.name()}. Editável: {layer.isEditable()}")
        return layer.isEditable()
    """
    Utilitários relacionados ao projeto QGIS (.qgz).
    Não possui dependência de UI.
    """
    @staticmethod
    def get_project_instance() -> QgsProject:
        """Retorna a instância do projeto QGIS aberto."""
        return QgsProject.instance()
    @staticmethod
    def is_project_saved(project: QgsProject) -> bool:
        return bool(project.fileName())

    @staticmethod
    def get_project_dir(project: QgsProject) -> str:
        """
        Retorna diretório do projeto salvo ou homePath como fallback.
        """
        if project.fileName():
            return str(Path(project.fileName()).parent)
        return project.homePath() or os.path.expanduser("~")

    @staticmethod
    def set_clipboard_text(text: str) -> bool:
        """Define o texto do clipboard via Qt. Retorna True se bem-sucedido."""
        try:
            from qgis.PyQt.QtGui import QGuiApplication
            QGuiApplication.clipboard().setText("" if text is None else str(text))
            return True
        except Exception as e:
            logger = LogUtils(tool="project_utils", class_name="ProjectUtils")
            logger.error(f"Erro ao copiar para clipboard: {e}")
            return False

    @staticmethod
    def create_project_backup(project: QgsProject) -> str:
        """
        Cria backup do .qgz em subpasta 'backup'.
        Retorna caminho do arquivo criado.
        Lança exceção se projeto não estiver salvo.
        """
        project_file = project.fileName()
        if not project_file:
            raise RuntimeError("Projeto não está salvo. Backup impossível.")

        project_path = Path(project_file)
        project_dir = project_path.parent

        backup_folder = project_dir / "backup"
        backup_folder.mkdir(exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        base_name = project_path.stem[:100]
        backup_name = f"{base_name}_{ts}{project_path.suffix}"

        backup_path = backup_folder / backup_name
        shutil.copy2(project_file, backup_path)

        return str(backup_path)

    @staticmethod
    def compute_size(obj: Optional[Union[str, Path, QgsMapLayer]]) -> int:
        if obj is None:
            return 0

        # QgsMapLayer
        if isinstance(obj, QgsMapLayer):
            src = obj.source() or ""

            # memory layer → estimar
            if src.startswith("memory:"):
                try:
                    feat_count = obj.featureCount()
                    geom_type = obj.wkbType()
                    # estimativa simples: 200 bytes por feature + geometria
                    return feat_count * 200
                except Exception:
                    return 0

            # arquivo real
            if "|" in src:
                src = src.split("|", 1)[0]

            obj = src

        p = Path(str(obj))
        if not p.exists():
            return 0

        if p.is_dir():
            total = 0
            for f in p.rglob("*"):
                if f.is_file():
                    try:
                        total += f.stat().st_size
                    except Exception:
                        pass
            return total

        if p.suffix.lower() == ".shp":
            total = 0
            for ext in (".shp", ".dbf", ".shx", ".prj", ".cpg", ".qix", ".sbn", ".sbx"):
                f = p.with_suffix(ext)
                if f.exists():
                    total += f.stat().st_size
            return total

        return p.stat().st_size
    
    @staticmethod
    def is_layer_in_project(layer: QgsMapLayer) -> bool:
        """
        Verifica se a camada informada está presente no projeto QGIS aberto.

        :param layer: QgsMapLayer selecionada (ex: cmb_layers.currentLayer())
        :return: True se estiver no projeto, False caso contrário
        """
        try:
            if layer is None:
                return False

            project = QgsProject.instance()
            return layer.id() in project.mapLayers()

        except Exception as e:
            logger = LogUtils(tool="project_utils", class_name="ProjectUtils")
            logger.error(f"Erro ao verificar camada no projeto: {e}")
            return False

    @staticmethod
    
    def remove_layer_from_project(layer: QgsMapLayer) -> bool:
        """
        Remove a camada informada do projeto QGIS aberto.

        :param layer: QgsMapLayer a ser removida
        :return: True se removida com sucesso, False em erro
        """
        try:
            if layer is None:
                return False

            project = QgsProject.instance()

            if layer.id() not in project.mapLayers():
                return False

            project.removeMapLayer(layer.id())
            return True

        except Exception as e:
            logger = LogUtils(tool="project_utils", class_name="ProjectUtils")
            logger.error(f"Erro ao remover camada do projeto: {e}")
            return False
        
    
    @staticmethod
    def is_file_in_project(file_path: str) -> bool:
        """
        Verifica se existe uma camada no projeto cujo source corresponde ao arquivo informado.
        """
        try:
            if not file_path:
                return False

            target = Path(file_path).resolve()

            for layer in QgsProject.instance().mapLayers().values():
                source = layer.source()

                if not source:
                    continue

                # Normaliza o path da layer (remove |layername= etc)
                layer_path = source.split("|")[0]

                if Path(layer_path).resolve() == target:
                    return True

            return False

        except Exception as e:
            logger = LogUtils(tool="project_utils", class_name="ProjectUtils")
            logger.error(f"Erro ao verificar arquivo no projeto: {e}")
            return False
    @staticmethod
    def remove_file_from_project(file_path: str) -> bool:
        """
        Remove do projeto a camada cujo source corresponde ao arquivo informado.
        """
        try:
            if not file_path:
                return False

            target = Path(file_path).resolve()
            project = QgsProject.instance()

            for layer_id, layer in project.mapLayers().items():
                source = layer.source()
                if not source:
                    continue

                layer_path = source.split("|")[0]

                if Path(layer_path).resolve() == target:
                    project.removeMapLayer(layer_id)
                    return True

            return False

        except Exception as e:
            logger = LogUtils(tool="project_utils", class_name="ProjectUtils")
            logger.error(f"Erro ao remover arquivo do projeto: {e}")
            return False

    # ------------------------------------------------------------------
    # Helpers adicionais para LoadFolderLayers refactor
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_layer_source(src: str) -> str:
        """Normaliza a source de uma layer (remove parâmetros e resolve path)."""
        if not src:
            return ""
        if "|" in src:
            src = src.split("|", 1)[0]
        try:
            return str(Path(src).resolve())
        except Exception:
            return os.path.normpath(src)

    @staticmethod
    def ensure_group(rel_path: str):
        """Garante a existência de um grupo aninhado a partir de um caminho relativo.

        Retorna o QgsLayerTreeGroup criado/encontrado.
        """
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        parts = rel_path.split(os.sep)
        current = root

        for part in parts:
            found = current.findGroup(part)
            if not found:
                found = current.addGroup(part)
            current = found

        return current

    @staticmethod
    def add_layer(layer, add_to_root: bool = True):
        """Adiciona uma layer ao projeto; retorna a layer adicionada ou None."""
        try:
            project = QgsProject.instance()
            if add_to_root:
                project.addMapLayer(layer, True)
            else:
                project.addMapLayer(layer, False)
            return layer
        except Exception:
            return None

    @staticmethod
    def add_layer_to_group(layer, group):
        """Adiciona uma camada já registrada no projeto dentro de um grupo (QgsLayerTreeGroup)."""
        try:
            project = QgsProject.instance()
            # garante que layer está no projeto sem inserir na root
            project.addMapLayer(layer, False)
            group.insertLayer(0, layer)
            return layer
        except Exception:
            return None





