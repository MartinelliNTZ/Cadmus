# -*- coding: utf-8 -*-
"""
ImageUtils — Utilitário para manipulação de imagens
=====================================================
Fornece métodos para conversão de imagens para base64 e outras operações
relacionadas a imagens no Cadmus.

Uso:
    from ..utils.ImageUtils import ImageUtils

    # Converter foto para base64
    b64 = ImageUtils.photo_to_base64("C:/fotos/foto.jpg", tool_key=ToolKey.SYSTEM)
"""

import base64
import os
from typing import Optional

from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil


class ImageUtils(BaseUtil):
    """Utilitário para conversão e manipulação de imagens.

    Métodos estáticos, log com LogUtils, tool_key em todos os métodos que logam.
    """

    # ── Constantes ───────────────────────────────────────────────────

    SUPPORTED_EXTENSIONS: tuple = (
        ".jpg", ".jpeg", ".png", ".tif", ".tiff",
        ".bmp", ".gif", ".webp", ".ico",
    )

    # ── Logger ───────────────────────────────────────────────────────

    @staticmethod
    def _get_logger(tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE) -> LogUtils:
        """Retorna instância de LogUtils para ImageUtils."""
        return LogUtils(tool=tool_key, class_name="ImageUtils")

    # ── Métodos Públicos ─────────────────────────────────────────────

    @staticmethod
    def photo_to_base64(
        file_path: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> Optional[str]:
        """Converte uma foto (arquivo de imagem) para string base64.

        Lê o arquivo de imagem do disco e retorna seu conteúdo codificado
        em base64 com prefixo de data URI (ex: ``data:image/jpeg;base64,...``).

        Args:
            file_path: Caminho absoluto para o arquivo de imagem.
            tool_key: Chave da ferramenta para rastreamento de logs.

        Returns:
            String base64 com data URI se bem-sucedido, ou None em caso de erro.

        Exemplo:
            >>> b64 = ImageUtils.photo_to_base64("C:/foto.jpg", tool_key=ToolKey.SYSTEM)
            >>> print(b64[:50])
            data:image/jpeg;base64,/9j/4AAQSkZJRg...
        """
        logger = ImageUtils._get_logger(tool_key)

        # ── Validações ───────────────────────────────────────────
        if not file_path:
            logger.error("photo_to_base64: caminho do arquivo vazio")
            return None

        if not os.path.isfile(file_path):
            logger.error(
                f"photo_to_base64: arquivo não encontrado: '{file_path}'")
            return None

        # ── Verifica extensão ────────────────────────────────────
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ImageUtils.SUPPORTED_EXTENSIONS:
            logger.warning(
                f"photo_to_base64: extensão '{ext}' não é uma extensão de imagem típica, "
                f"mas tentando conversão mesmo assim"
            )

        # ── Leitura e codificação ────────────────────────────────
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
        except (IOError, OSError, PermissionError) as e:
            logger.error(
                f"photo_to_base64: erro ao ler arquivo '{file_path}': {e}")
            return None
        except Exception as e:
            logger.exception(
                f"photo_to_base64: erro inesperado ao ler arquivo '{file_path}': {e}",
            )
            return None

        if not image_bytes:
            logger.error(f"photo_to_base64: arquivo vazio: '{file_path}'")
            return None

        # ── Codifica para base64 ─────────────────────────────────
        try:
            b64_bytes = base64.b64encode(image_bytes)
            b64_str = b64_bytes.decode("ascii")
        except Exception as e:
            logger.exception(
                f"photo_to_base64: erro ao codificar base64: {e}",
            )
            return None

        # ── Monta data URI ───────────────────────────────────────
        mime_type = ImageUtils._guess_mime_type(ext)
        data_uri = f"data:{mime_type};base64,{b64_str}"

        logger.info(
            f"photo_to_base64: imagem '{os.path.basename(file_path)}' "
            f"convertida para base64 ({len(b64_str)} chars)"
        )
        return data_uri

    # ── Métodos Auxiliares Privados ──────────────────────────────────

    @staticmethod
    def _guess_mime_type(extension: str) -> str:
        """Retorna o MIME type correspondente à extensão do arquivo.

        Args:
            extension: Extensão do arquivo (ex: '.jpg', '.png').

        Returns:
            String com o MIME type (ex: 'image/jpeg').
        """
        mime_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".bmp": "image/bmp",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".ico": "image/x-icon",
        }
        return mime_map.get(extension.lower(), "application/octet-stream")

    @staticmethod
    def base64_to_bytes(
        data_uri: str,
        tool_key: str = BaseUtil.TOOL_KEY_UNTRACEABLE,
    ) -> Optional[bytes]:
        """Converte uma string base64 (com ou sem data URI) de volta para bytes..

        Args:
            data_uri: String base64, podendo conter prefixo ``data:...;base64,``.
            tool_key: Chave da ferramenta para rastreamento de logs.

        Returns:
            Bytes decodificados, ou None em caso de erro.
        """
        logger = ImageUtils._get_logger(tool_key)

        if not data_uri:
            logger.error("base64_to_bytes: string vazia")
            return None

        try:
            # Remove prefixo data URI se presente
            if "," in data_uri:
                _, b64_part = data_uri.split(",", 1)
            else:
                b64_part = data_uri

            return base64.b64decode(b64_part)
        except (ValueError, base64.binascii.Error) as e:
            logger.error(f"base64_to_bytes: erro ao decodificar base64: {e}")
            return None
        except Exception as e:
            logger.exception(f"base64_to_bytes: erro inesperado: {e}")
            return None
