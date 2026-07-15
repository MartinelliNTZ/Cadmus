# -*- coding: utf-8 -*-
import os
import zipfile
from typing import List, Tuple, Optional

from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil


class FileCompressUtils(BaseUtil):
    """
    Utilitário para compressão e extração de arquivos.

    Métodos estáticos, sem dependência de QGIS.
    """

    @staticmethod
    def _get_logger(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> LogUtils:
        return LogUtils(tool=tool_key, class_name="FileCompressUtils")

    @staticmethod
    def is_valid_zip(zip_path: str) -> bool:
        """Verifica se o arquivo é um zip válido e não está corrompido."""
        if not zip_path or not os.path.isfile(zip_path):
            return False
        try:
            with zipfile.ZipFile(zip_path, mode="r") as zf:
                bad = zf.testzip()
                return bad is None
        except (zipfile.BadZipFile, Exception):
            return False

    @staticmethod
    def zip_files(
        file_paths: List[str],
        zip_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        remove_originals: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        logger = FileCompressUtils._get_logger(tool_key)

        if os.path.isfile(zip_path):
            logger.warning(f"ZIP: zip já existe: '{zip_path}'")
            return False, "Arquivo zip já existe"

        valid_paths = []
        for fp in file_paths:
            if os.path.isfile(fp):
                valid_paths.append(fp)
            else:
                logger.warning(f"ZIP: arquivo não encontrado, ignorado: '{fp}'")

        if not valid_paths:
            logger.warning("ZIP: nenhum arquivo válido para zipar")
            return False, "Nenhum arquivo válido encontrado"

        parent = os.path.dirname(zip_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        try:
            with zipfile.ZipFile(
                zip_path, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as zf:
                for file_path in valid_paths:
                    basename = os.path.basename(file_path)
                    zf.write(file_path, arcname=basename)

            if remove_originals:
                for file_path in valid_paths:
                    os.remove(file_path)

            logger.info(
                f"ZIP: criado '{os.path.basename(zip_path)}' com {len(valid_paths)} arquivo(s)"
            )
            return True, zip_path

        except zipfile.BadZipFile as e:
            logger.error(f"ZIP: erro ao criar zip: {e}")
            if os.path.isfile(zip_path):
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
            return False, f"Erro ao criar zip: {e}"
        except Exception as e:
            logger.error(f"ZIP: erro inesperado: {e}")
            return False, f"Erro inesperado: {e}"

    @staticmethod
    def zip_directory(
        dir_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        remove_originals: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        logger = FileCompressUtils._get_logger(tool_key)

        if not os.path.isdir(dir_path):
            logger.warning(f"ZIP_DIR: diretório inválido: '{dir_path}'")
            return False, "Diretório inválido"

        folder_name = os.path.basename(dir_path) or "pasta"
        zip_path = os.path.join(dir_path, f"{folder_name}.zip")

        file_paths = [
            os.path.join(dir_path, f)
            for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f)) and f != f"{folder_name}.zip"
        ]

        if not file_paths:
            logger.warning(f"ZIP_DIR: diretório vazio: '{dir_path}'")
            return False, "Diretório vazio"

        return FileCompressUtils.zip_files(
            file_paths=file_paths,
            zip_path=zip_path,
            tool_key=tool_key,
            remove_originals=remove_originals,
        )

    @staticmethod
    def unzip_file(
        zip_path: str,
        extract_dir: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        remove_zip: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        logger = FileCompressUtils._get_logger(tool_key)

        if not os.path.isfile(zip_path):
            logger.warning(f"UNZIP: zip não encontrado: '{zip_path}'")
            return False, "Arquivo zip não encontrado"

        if not os.path.isdir(extract_dir):
            logger.warning(f"UNZIP: diretório inválido: '{extract_dir}'")
            return False, "Diretório de extração inválido"

        try:
            with zipfile.ZipFile(zip_path, mode="r") as zf:
                names = zf.namelist()
                if not names:
                    logger.warning(f"UNZIP: zip vazio: '{zip_path}'")
                    return False, "Arquivo zip vazio"

                for name in names:
                    normalized = os.path.normpath(name)
                    if normalized.startswith("..") or normalized.startswith("/"):
                        logger.error(
                            f"UNZIP: path traversal detectado em '{zip_path}': '{name}'"
                        )
                        return False, "Path traversal detectado no zip"

                zf.extractall(path=extract_dir)

            logger.info(
                f"UNZIP: extraídos {len(names)} arquivo(s) de '{os.path.basename(zip_path)}'"
            )

            if remove_zip:
                os.remove(zip_path)
                logger.info(f"UNZIP: zip removido: '{os.path.basename(zip_path)}'")

            return True, f"Extraídos {len(names)} arquivo(s) com sucesso"

        except zipfile.BadZipFile as e:
            logger.error(f"UNZIP: zip corrompido: '{zip_path}': {e}")
            return False, "Arquivo zip corrompido"
        except Exception as e:
            logger.error(f"UNZIP: erro ao extrair '{zip_path}': {e}")
            return False, f"Erro ao extrair zip: {e}"

    @staticmethod
    def unzip_directory(
        dir_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
        remove_zip: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        logger = FileCompressUtils._get_logger(tool_key)

        if not os.path.isdir(dir_path):
            logger.warning(f"UNZIP_DIR: diretório inválido: '{dir_path}'")
            return False, "Diretório inválido"

        folder_name = os.path.basename(dir_path) or "pasta"
        zip_path = os.path.join(dir_path, f"{folder_name}.zip")

        if not os.path.isfile(zip_path):
            logger.warning(f"UNZIP_DIR: zip não encontrado: '{zip_path}'")
            return False, "Arquivo zip não encontrado no diretório"

        return FileCompressUtils.unzip_file(
            zip_path=zip_path,
            extract_dir=dir_path,
            tool_key=tool_key,
            remove_zip=remove_zip,
        )
