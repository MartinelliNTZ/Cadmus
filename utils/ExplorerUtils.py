# -*- coding: utf-8 -*-
import os
import shutil
import re
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices

from ..core.config.LogUtils import LogUtils
from .vector.VectorLayerSource import VectorLayerSource
from .raster.RasterLayerSource import RasterLayerSource
from .StringManager import StringManager
from .BaseUtil import BaseUtil


class ExplorerUtils(BaseUtil):
    """Utilitário para varredura de diretórios e carregamento de layers.

    Métodos estáticos, log com LogUtils, tool_key em todos os métodos que logam.
    """

    CADMUS_TEMP_FOLDER = "cadmus"
    REPORTS_TEMP_FOLDER = "reports"
    REPORTS_JSON_FOLDER = "json"
    REPORTS_HTML_FOLDER = "html"

    # ── Diálogos de seleção ─────────────────────────────────────────

    @staticmethod
    def resolve_initial_dir(path_or_dir: str) -> str:
        """Resolve diretório inicial para diálogos."""
        if not path_or_dir:
            return ""
        if os.path.isfile(path_or_dir):
            return os.path.dirname(path_or_dir)
        if os.path.isdir(path_or_dir):
            return path_or_dir
        # Pode ser um path que ainda não existe (output)
        parent = os.path.dirname(path_or_dir)
        if parent and os.path.isdir(parent):
            return parent
        return path_or_dir

    @staticmethod
    def open_file_dialog(
        title: str,
        initial_dir: str = "",
        file_filter: str = "Todos (*.*)",
        parent=None,
    ) -> str:
        """Abre diálogo para selecionar UM arquivo existente."""
        from qgis.PyQt.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            parent, title, initial_dir, file_filter)
        return path or ""

    @staticmethod
    def open_files_dialog(
        title: str,
        initial_dir: str = "",
        file_filter: str = "Todos (*.*)",
        parent=None,
    ) -> list:
        """Abre diálogo para selecionar MÚLTIPLOS arquivos existentes."""
        from qgis.PyQt.QtWidgets import QFileDialog
        paths, _ = QFileDialog.getOpenFileNames(
            parent, title, initial_dir, file_filter)
        return list(paths)

    @staticmethod
    def save_file_dialog(
        title: str,
        initial_dir: str = "",
        file_filter: str = "Todos (*.*)",
        parent=None,
    ) -> str:
        """Abre diálogo para selecionar UM arquivo de saída (salvar)."""
        from qgis.PyQt.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            parent, title, initial_dir, file_filter)
        return path or ""

    @staticmethod
    def select_directory_dialog(
        title: str,
        initial_dir: str = "",
        parent=None,
    ) -> str:
        """Abre diálogo para selecionar UMA pasta."""
        from qgis.PyQt.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(parent, title, initial_dir)
        return path or ""

    @staticmethod
    def _get_logger(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="ExplorerUtils")

    @staticmethod
    def has_extension(path: str, extensions: List[str]) -> bool:
        """Verifica se `path` possui uma das extensoes informadas."""
        if not path:
            return False

        ext = Path(path).suffix.lower()
        normalized = {e.lower() for e in extensions}
        return ext in normalized

    @staticmethod
    def build_suffixed_output_path(
        file_path: str, suffix: str, extension: str = ".gpkg"
    ) -> str:
        """Gera caminho ao lado do arquivo original com sufixo e nova extensao."""
        p = Path(file_path)
        return str(p.with_name(f"{p.stem}_{suffix}{extension}"))

    @staticmethod
    def sanitize_path_component(raw_name: str) -> str:
        """Sanitiza nome para uso como pasta/arquivo."""
        cleaned = re.sub(r'[<>:"/\\\\|?*]+', " ", raw_name or "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".")
        return cleaned

    @staticmethod
    def next_indexed_folder_name(
        base_folder: str,
        prefix: str,
        pattern: re.Pattern,
    ) -> str:
        """Retorna próximo nome incremental de pasta usando pattern informado."""
        folder = Path(base_folder)
        highest = 0

        if folder.exists():
            for child in folder.iterdir():
                if not child.is_dir():
                    continue
                match = pattern.match(child.name)
                if match:
                    highest = max(highest, int(match.group(1)))

        return f"{prefix}{highest + 1}"

    @staticmethod
    def ensure_folder_exists(
        folder_path: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> bool:
        """Garante que a pasta existe; retorna False em erro."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if not folder_path:
                logger.error("ensure_folder_exists: caminho vazio")
                return False
            os.makedirs(folder_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"ensure_folder_exists: erro ao preparar pasta: {e}")
            return False

    @staticmethod
    def is_file(path: str) -> bool:
        """Verifica se o caminho existe e aponta para um arquivo."""
        return bool(path) and Path(path).is_file()

    @staticmethod
    def open_folder(folder: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> bool:
        """Abre uma pasta no explorador do sistema."""
        logger = ExplorerUtils._get_logger(tool_key)

        if not folder or not os.path.isdir(folder):
            logger.error(f"open_folder: pasta invalida: {folder}")
            return False

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
        logger.info(f"open_folder: pasta aberta: {folder}")
        return True

    @staticmethod
    def open_file(
        file_path: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> bool:
        """Abre um arquivo com o aplicativo padrao do sistema (ex.: HTML no navegador)."""
        logger = ExplorerUtils._get_logger(tool_key)
        if not file_path or not os.path.isfile(file_path):
            logger.error(f"open_file: arquivo invalido: {file_path}")
            return False

        ok = QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        if ok:
            logger.info(f"open_file: arquivo aberto: {file_path}")
            return True

        logger.error(f"open_file: falha ao abrir arquivo: {file_path}")
        return False

    @staticmethod
    def copy_file_to_folder(
        source_file: str,
        destination_folder: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        overwrite: bool = True,
    ) -> str:
        """Copia arquivo para uma pasta destino e retorna o caminho final."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if not source_file or not os.path.isfile(source_file):
                logger.error(
                    f"copy_file_to_folder: arquivo origem invalido: {source_file}"
                )
                return ""

            if not destination_folder:
                logger.error("copy_file_to_folder: pasta destino vazia")
                return ""

            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(
                destination_folder, os.path.basename(source_file)
            )

            if os.path.exists(destination_path) and not overwrite:
                logger.info(
                    f"copy_file_to_folder: arquivo ja existe (sem overwrite): {destination_path}"
                )
                return destination_path

            shutil.copy2(source_file, destination_path)
            logger.info(
                f"copy_file_to_folder: arquivo copiado de '{source_file}' para '{destination_path}'"
            )
            return destination_path
        except Exception as e:
            logger.error(f"copy_file_to_folder: erro ao copiar arquivo: {e}")
            return ""

    @staticmethod
    def create_temp_json(
        payload,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        prefix: str = "cadmus_drone_metadata",
        subfolder: str = None,
        file_stem_hint: str = None,
    ) -> str:
        """Cria arquivo JSON temporario e retorna caminho absoluto."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if subfolder:
                temp_dir = ExplorerUtils.ensure_temp_subfolder(
                    subfolder, tool_key=tool_key
                )
            else:
                temp_dir = tempfile.gettempdir()
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hint = ExplorerUtils.sanitize_path_component(file_stem_hint or "")
            if hint:
                file_name = f"{prefix}_{hint}_{stamp}.json"
            else:
                file_name = f"{prefix}_{stamp}.json"
            output_path = os.path.join(temp_dir, file_name)
            with open(output_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False,
                          indent=2, default=str)
            logger.info(f"create_temp_json: arquivo gerado em {output_path}")
            return output_path
        except Exception as e:
            logger.error(
                f"create_temp_json: erro ao criar json temporario: {e}")
            return ""

    @staticmethod
    def get_cadmus_temp_root(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> str:
        """Retorna pasta base temporaria do Cadmus em %TEMP%."""
        logger = ExplorerUtils._get_logger(tool_key)
        temp_root = os.path.join(
            tempfile.gettempdir(),
            ExplorerUtils.CADMUS_TEMP_FOLDER,
        )
        try:
            os.makedirs(temp_root, exist_ok=True)
            return temp_root
        except Exception as e:
            logger.error(
                f"get_cadmus_temp_root: erro ao criar pasta base: {e}")
            return tempfile.gettempdir()

    @staticmethod
    def ensure_temp_subfolder(
        subfolder: str, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE
    ) -> str:
        """Cria e retorna subpasta dentro da raiz temporaria do Cadmus."""
        logger = ExplorerUtils._get_logger(tool_key)
        root = ExplorerUtils.get_cadmus_temp_root(tool_key)
        subfolder_text = str(subfolder or "").strip()
        if not subfolder_text:
            logger.warning(
                "ensure_temp_subfolder: subfolder vazio/invalido, usando raiz cadmus temp"
            )
            return root

        parts = re.split(r"[\\/]+", subfolder_text)
        safe_parts = [
            ExplorerUtils.sanitize_path_component(part)
            for part in parts
            if ExplorerUtils.sanitize_path_component(part)
        ]
        if not safe_parts:
            logger.warning(
                "ensure_temp_subfolder: subfolder sem partes validas, usando raiz cadmus temp"
            )
            return root

        full_path = os.path.join(root, *safe_parts)
        try:
            os.makedirs(full_path, exist_ok=True)
            return full_path
        except Exception as e:
            logger.error(f"ensure_temp_subfolder: erro ao criar subpasta: {e}")
            return root

    @staticmethod
    def get_temp_folder(
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE, *subfolders: str
    ) -> str:
        """Retorna pasta temporaria do Cadmus opcionalmente navegando por subpastas."""
        if not subfolders:
            return ExplorerUtils.get_cadmus_temp_root(tool_key)
        joined = os.path.join(*[str(part)
                              for part in subfolders if str(part).strip()])
        return ExplorerUtils.ensure_temp_subfolder(joined, tool_key=tool_key)

    @staticmethod
    def build_report_json_stem(base_folder: str = "", points_total: int = None) -> str:
        """
        Monta sufixo amigavel para nome de JSON de report.
        Exemplo: `M3E_DJI_202604011322_001_m2_167pts`.
        """
        base_name = os.path.basename(str(base_folder or "").rstrip("\\/"))
        base_name = ExplorerUtils.sanitize_path_component(base_name)
        if points_total is None:
            return base_name or "dataset"
        return f"{base_name or 'dataset'}_{int(points_total)}pts"

    @staticmethod
    def build_report_html_stem(
        source_json_path: str = "", default_stem: str = "report_metadata"
    ) -> str:
        """Monta sufixo amigavel para nome de HTML de report."""
        json_stem = Path(
            source_json_path).stem if source_json_path else default_stem
        return ExplorerUtils.sanitize_path_component(json_stem) or default_stem

    @staticmethod
    def build_temp_file_path(
        tool_key=BaseUtil.TOOL_KEY_UNTRACEABLE,
        *subfolders: str,
        prefix: str = "cadmus",
        extension: str = ".tmp",
        file_stem_hint: str = "",
    ) -> str:
        """Monta caminho de arquivo temporario com nome padronizado em subpasta do Cadmus temp."""
        temp_dir = ExplorerUtils.get_temp_folder(tool_key, *subfolders)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = extension if str(extension).startswith(".") else f".{extension}"
        hint = ExplorerUtils.sanitize_path_component(file_stem_hint or "")
        if hint:
            file_name = f"{prefix}_{hint}_{stamp}{ext}"
        else:
            file_name = f"{prefix}_{stamp}{ext}"
        return os.path.join(temp_dir, file_name)

    @staticmethod
    def rename_file(
        src: str,
        dst: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        overwrite: bool = False,
    ) -> bool:
        """Renomeia/move um arquivo no disco."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if not src or not os.path.isfile(src):
                logger.error(f"rename_file: arquivo origem inválido: '{src}'")
                return False

            if not dst:
                logger.error("rename_file: caminho destino vazio")
                return False

            if os.path.isfile(dst) and not overwrite:
                logger.warning(
                    f"rename_file: destino já existe (sem overwrite): '{dst}'"
                )
                return False

            parent = os.path.dirname(dst)
            if parent:
                os.makedirs(parent, exist_ok=True)

            os.rename(src, dst)
            logger.info(
                f"rename_file: '{os.path.basename(src)}' → '{os.path.basename(dst)}'"
            )
            return True
        except PermissionError as e:
            logger.error(
                f"rename_file: permissão negada ao renomear '{src}': {e}")
            return False
        except Exception as e:
            logger.error(f"rename_file: erro ao renomear '{src}': {e}")
            return False

    @staticmethod
    def remove_extension_dot(
        file_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> Optional[str]:
        """Remove o ponto da extensão do arquivo: foto.jpg → fotojpg."""
        logger = ExplorerUtils._get_logger(tool_key)
        if not file_path or not os.path.isfile(file_path):
            logger.warning(
                f"remove_extension_dot: arquivo não encontrado: '{file_path}'"
            )
            return None

        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        stem, ext = os.path.splitext(basename)
        ext_sem_ponto = ext.replace(".", "")
        novo_basename = stem + ext_sem_ponto
        novo_path = os.path.join(dirname, novo_basename)

        ok = ExplorerUtils.rename_file(file_path, novo_path, tool_key)
        if ok:
            return novo_path
        return None

    @staticmethod
    def restore_extension_dot(
        file_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> Optional[str]:
        """Restaura o ponto na extensão: fotojpg → foto.jpg."""
        logger = ExplorerUtils._get_logger(tool_key)

        if os.path.isfile(file_path):
            logger.info(
                f"restore_extension_dot: '{os.path.basename(file_path)}' já existe no disco, mantendo"
            )
            return file_path

        dirname = os.path.dirname(file_path)
        basename = os.path.basename(file_path)
        stem, ext = os.path.splitext(basename)
        ext_sem_ponto = ext.replace(".", "")
        flat_name = stem + ext_sem_ponto

        target_dir = dirname if dirname else os.getcwd()
        if not os.path.isdir(target_dir):
            logger.warning(
                f"restore_extension_dot: diretório inválido: '{target_dir}'")
            return None

        try:
            for f_name in os.listdir(target_dir):
                f_path = os.path.join(target_dir, f_name)
                if not os.path.isfile(f_path):
                    continue
                if f_name == flat_name:
                    ok = ExplorerUtils.rename_file(f_path, file_path, tool_key)
                    if ok:
                        return file_path
                    return None
        except Exception as e:
            logger.error(
                f"restore_extension_dot: erro ao listar diretório: {e}")
            return None

        logger.warning(
            f"restore_extension_dot: nenhum arquivo '{flat_name}' encontrado em '{target_dir}'"
        )
        return None

    @staticmethod
    def copy_file(
        source: str,
        destination: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        overwrite: bool = True,
    ) -> bool:
        """Copia um arquivo diretamente para o destino especificado (path completo)."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if not source or not os.path.isfile(source):
                logger.error(f"copy_file: arquivo origem invalido: {source}")
                return False

            if not destination:
                logger.error("copy_file: caminho destino vazio")
                return False

            if os.path.exists(destination) and not overwrite:
                logger.info(
                    f"copy_file: destino ja existe (sem overwrite): {destination}"
                )
                return True

            dst_dir = os.path.dirname(destination)
            if dst_dir:
                os.makedirs(dst_dir, exist_ok=True)

            shutil.copy2(source, destination)
            logger.info(
                f"copy_file: '{os.path.basename(source)}' -> '{destination}'"
            )
            return True
        except Exception as e:
            logger.error(
                f"copy_file: erro ao copiar '{source}' -> '{destination}': {e}")
            return False

    @staticmethod
    def get_unique_filepath(
        filepath: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> str:
        """
        Gera caminho unico adicionando sufixo _1, _2, _3... se o arquivo ja existir.

        Exemplo:
            arquivo.gpkg -> arquivo.gpkg (se nao existir)
            arquivo.gpkg -> arquivo_1.gpkg (se existir)
            arquivo_1.gpkg -> arquivo_2.gpkg (se existir)
        """
        logger = ExplorerUtils._get_logger(tool_key)
        if not filepath:
            logger.warning("get_unique_filepath: caminho vazio")
            return ""
        if not os.path.exists(filepath):
            return filepath

        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        result = f"{base}_{counter}{ext}"
        logger.debug(f"get_unique_filepath: '{filepath}' -> '{result}'")
        return result

    @staticmethod
    def create_temp_file(
        suffix: str = ".tmp",
        prefix: str = "cadmus_tmp_",
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> Tuple[Optional[int], Optional[str]]:
        """Cria arquivo temporario no disco e retorna (fd, path)."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            logger.debug(f"create_temp_file: criado '{path}' (fd={fd})")
            return fd, path
        except Exception as e:
            logger.error(f"create_temp_file: erro ao criar temp file: {e}")
            return None, None

    @staticmethod
    def delete_file(
        file_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        ignore_errors: bool = True,
    ) -> bool:
        """Remove um arquivo do disco."""
        logger = ExplorerUtils._get_logger(tool_key)
        try:
            if not file_path:
                logger.warning("delete_file: caminho vazio")
                return False
            if not os.path.isfile(file_path):
                logger.warning(
                    f"delete_file: arquivo nao encontrado: '{file_path}'")
                return False
            os.remove(file_path)
            logger.debug(f"delete_file: removido '{file_path}'")
            return True
        except Exception as e:
            if not ignore_errors:
                logger.error(
                    f"delete_file: erro ao remover '{file_path}': {e}")
            return False

    @staticmethod
    def scan_folder(
        folder: str,
        extensions: List[str],
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> List[Dict]:
        """Varre `folder` e retorna lista de registros de arquivos que batem nas `extensions`."""
        logger = ExplorerUtils._get_logger(tool_key)
        results = []
        if not folder or not os.path.isdir(folder):
            logger.error(f"scan_folder: pasta inválida: {folder}")
            return results

        exts_set = set(e.lower() for e in extensions)

        for root, dirs, files in os.walk(folder):
            for f in files:
                p = Path(root) / f
                ext = p.suffix.lower()
                if exts_set and ext not in exts_set:
                    continue
                rec = {"path": str(p), "ext": ext}
                if ext in StringManager.RASTER_EXTS:
                    rec["type"] = "raster"
                else:
                    rec["type"] = "vector"
                results.append(rec)
        logger.info(
            f"scan_folder: encontrados {len(results)} arquivos em {folder}")
        return results

    @staticmethod
    def create_layer(record: Dict, tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE):
        """Carrega e retorna uma camada QGIS baseada no registro (usa Vector/RasterSource)."""
        logger = ExplorerUtils._get_logger(tool_key)
        path = record.get("path")
        rtype = record.get("type")

        if rtype == "raster":
            layer = RasterLayerSource().load_raster_from_file(
                path, external_tool_key=tool_key
            )
            if layer:
                logger.info(f"Raster criado: {path}")
            return layer
        else:
            layer = VectorLayerSource().load_vector_layer_from_file(
                path, external_tool_key=tool_key
            )
            if layer:
                logger.info(f"Vector criado: {path}")
            return layer
