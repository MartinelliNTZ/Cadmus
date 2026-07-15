# -*- coding: utf-8 -*-
"""
PackageManager — Gerenciamento centralizado de pacotes .dist
===============================================================
Classe pública responsável por criar e instalar pacotes de
distribuição (.dist).

Fluxo de chave de licença:
    1. create_package(): se uma chave é fornecida, ela é criptografada
       (XOR + HMAC + Base64) e armazenada no manifest.json como "key_enc"
    2. install_package(): extrai "key_enc" do manifest, descriptografa
       e retorna a chave original via callback on_key_callback

Uso:
    from core.services.PackageManager import PackageManager

    pm = PackageManager()

    # Criar pacote (key será criptografada no manifest)
    pm.create_package(
        dist_path="/caminho/output.dist",
        modules={"plugins": ["MeuModulo.pyc"]},
        static_files=["resources/config.yaml"],
        root_dir=self._root,
        key="MINHA-CHAVE-SECRETA",
    )

    # Instalar pacote (key será descriptografada e passada ao callback)
    pm.install_package(
        dist_path="/caminho/arquivo.dist",
        plugin_root=Path("/caminho/plugin"),
        on_key_callback=lambda key_plain: print(f"Chave: {key_plain}"),
    )

Arquitetura:
    PackageManager é a classe de interface pública. BuildDistribution
    (que contém dados sensíveis) será eliminada futuramente.
"""

import base64
import hashlib
import hmac
import json
import os
import shutil
import tempfile
import zlib
import zipfile
from pathlib import Path
from typing import Callable, Optional, Union

# Chaves usadas para criptografar/descriptografar a chave no manifest
# (mesmo mecanismo do RegistryFileManager, sem depender dele diretamente
#  para evitar problemas de import quando o módulo não existe)
_PM_SECRET_KEY: bytes = b"C4dmu5_S3cr3t_K3y_2026!@#$%^&*()_+="
_PM_HMAC_KEY: bytes = b"C4dmu5_HM4c_K3y_2026!@#$%^&*()_+="


def _pm_generate_keystream(key: bytes, size: int) -> bytes:
    """Gera keystream SHA-256."""
    result = b""
    counter = 0
    while len(result) < size:
        chunk = hashlib.sha256(key + str(counter).encode("utf-8")).digest()
        result += chunk
        counter += 1
    return result[:size]


def _pm_xor_data(data: bytes, keystream: bytes) -> bytes:
    """XOR byte a byte."""
    return bytes(a ^ b for a, b in zip(data, keystream))


def _pm_encrypt_key(plain_key: str) -> str:
    """
    Criptografa a chave para armazenamento seguro no manifest.

    Pipeline: plain_key -> JSON -> HMAC -> compress -> XOR -> Base64
    """
    data = {"k": plain_key}
    json_bytes = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode(
        "utf-8"
    )

    # HMAC
    sig = hmac.new(_PM_HMAC_KEY, json_bytes, hashlib.sha256).hexdigest()
    payload = json_bytes + b"|" + sig.encode("ascii")

    # Compress
    compressed = zlib.compress(payload)

    # XOR
    stream = _pm_generate_keystream(_PM_SECRET_KEY, len(compressed))
    encrypted = _pm_xor_data(compressed, stream)

    # Base64
    return base64.b64encode(encrypted).decode("ascii")


def _pm_decrypt_key(encrypted_b64: str) -> Optional[str]:
    """
    Descriptografa a chave do manifest.
    Retorna a chave original ou None se inválida/adulterada.
    """
    try:
        encrypted = base64.b64decode(encrypted_b64)

        # XOR
        stream = _pm_generate_keystream(_PM_SECRET_KEY, len(encrypted))
        xored = _pm_xor_data(encrypted, stream)

        # Decompress
        decompressed = zlib.decompress(xored)

        # Split payload | HMAC
        if b"|" not in decompressed:
            return None
        json_bytes, sig = decompressed.rsplit(b"|", 1)

        # Verify HMAC
        expected = hmac.new(_PM_HMAC_KEY, json_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig.decode("ascii")):
            return None

        # Parse JSON
        data = json.loads(json_bytes.decode("utf-8"))
        return data.get("k", "")

    except Exception:
        return None


class PackageManager:
    """
    Gerenciamento centralizado de pacotes .dist (criação e instalação).

    A chave de licença é criptografada (XOR + HMAC + zlib + Base64) antes de
    ser armazenada no manifest.json do pacote .dist, garantindo que não fique
    visível em texto plano dentro do arquivo ZIP.
    """

    # ------------------------------------------------------------------
    # API pública — Criação de pacotes
    # ------------------------------------------------------------------

    @staticmethod
    def create_package(
        dist_path: Union[str, Path],
        modules: dict,
        static_files: list,
        root_dir: Union[str, Path] = None,
        key: str = "",
        manifest_extra: Optional[dict] = None,
    ) -> bool:
        """
        Cria um arquivo .dist (ZIP) com os módulos e arquivos estáticos
        especificados.

        Se uma chave for fornecida, ela é criptografada e armazenada
        como "key_enc" no manifest (não como "key" em texto plano).

        Args:
            dist_path: Caminho de destino do arquivo .dist.
            modules: Dicionário { "diretorio_relativo": ["arquivo1.pyc", ...] }
            static_files: Lista de caminhos relativos de arquivos estáticos.
            root_dir: Diretório raiz para resolução dos caminhos.
            key: Chave de licença opcional (será criptografada).
            manifest_extra: Campos extras opcionais para o manifest.json.

        Returns:
            True se bem-sucedido.
        """
        dist_path = Path(dist_path)
        root = Path(root_dir).resolve() if root_dir else Path.cwd()
        print(f"[PackageManager] Criando pacote: {dist_path}")

        try:
            with tempfile.TemporaryDirectory(prefix="pm_dist_") as tmp_dir:
                tmp_zip = os.path.join(tmp_dir, "dist.zip")

                with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                    # Manifest
                    manifest = {
                        "version": 1,
                        "key_enc": "",
                        "modules": {},
                        "static_files": [],
                    }
                    if manifest_extra:
                        manifest.update(manifest_extra)

                    # Criptografa a chave se fornecida
                    if key:
                        manifest["key_enc"] = _pm_encrypt_key(key)
                        print("[PackageManager] Chave criptografada no manifest")

                    # Adiciona módulos
                    for rel_dir, filenames in modules.items():
                        dir_path = root / rel_dir
                        manifest["modules"][rel_dir] = []
                        for filename in filenames:
                            file_path = dir_path / filename
                            if file_path.exists():
                                arcname = f"{rel_dir}/{file_path.name}"
                                zf.write(str(file_path), arcname)
                                manifest["modules"][rel_dir].append(file_path.name)
                                print(f"[PackageManager]   + {arcname}")
                            else:
                                print(
                                    f"[PackageManager]   AVISO: Não encontrado: "
                                    f"{file_path}"
                                )

                    # Adiciona arquivos estáticos
                    for rel_path in static_files:
                        full_path = root / rel_path
                        if full_path.exists():
                            zf.write(str(full_path), rel_path)
                            manifest["static_files"].append(rel_path)
                            print(f"[PackageManager]   + {rel_path} (estático)")
                        else:
                            print(
                                f"[PackageManager]   AVISO: Estático não encontrado: "
                                f"{full_path}"
                            )

                    # Escreve manifest.json no ZIP
                    zf.writestr("manifest.json", json.dumps(manifest, indent=2))

                # Copia para o destino final
                if dist_path.exists():
                    os.remove(dist_path)
                shutil.copy2(tmp_zip, dist_path)

            size_kb = dist_path.stat().st_size // 1024
            print(f"[PackageManager] Pacote gerado: {dist_path.name} ({size_kb} KB)")
            if key:
                print("[PackageManager] Chave protegida incorporada no manifest")
            return True

        except Exception as exc:
            print(f"[PackageManager] ERRO na criação do pacote: {exc}")
            return False

    # ------------------------------------------------------------------
    # API pública — Instalação / restauração de pacotes
    # ------------------------------------------------------------------

    @staticmethod
    def install_package(
        dist_path: Union[str, Path],
        plugin_root: Union[str, Path],
        on_key_callback: Optional[Callable[[str], None]] = None,
        logger=None,
    ) -> dict:
        """
        Instala (restaura) um pacote .dist no diretório do plugin.

        1. Extrai todos os módulos para o plugin_root
        2. Se houver chave criptografada ("key_enc") no manifest,
           descriptografa e chama on_key_callback com a chave original
        3. Retorna resultado com a chave descriptografada

        Args:
            dist_path: Caminho do arquivo .dist.
            plugin_root: Diretório raiz do plugin.
            on_key_callback: Função chamada com a chave de licença
                             DESCRIPTOGRAFADA, se houver.
            logger: Logger opcional para mensagens de depuração.

        Returns:
            dict com:
                "success": bool
                "restored_count": int
                "key": str (chave DESCRIPTOGRAFADA ou "")
                "message": str
        """
        dist_path = Path(dist_path)
        plugin_root = Path(plugin_root)

        if not dist_path.exists():
            msg = f"Arquivo não encontrado: {dist_path}"
            if logger:
                logger.error(msg)
            return {"success": False, "restored_count": 0, "key": "", "message": msg}

        try:
            with zipfile.ZipFile(str(dist_path), "r") as zf:
                # Lê o manifest
                if "manifest.json" not in zf.namelist():
                    msg = "Pacote inválido: manifest.json não encontrado."
                    if logger:
                        logger.error(msg)
                    return {
                        "success": False,
                        "restored_count": 0,
                        "key": "",
                        "message": msg,
                    }

                manifest_data = zf.read("manifest.json")
                manifest = json.loads(manifest_data)

                # Restaura cada módulo primeiro
                modules_info = manifest.get("modules", {})
                restored_count = 0

                for directory, filenames in modules_info.items():
                    target_dir = plugin_root / directory
                    target_dir.mkdir(parents=True, exist_ok=True)

                    for filename in filenames:
                        arcname = f"{directory}/{filename}"
                        if arcname in zf.namelist():
                            data = zf.read(arcname)
                            dest_path = target_dir / filename
                            with open(str(dest_path), "wb") as f:
                                f.write(data)
                            restored_count += 1
                            if logger:
                                logger.debug(f"Restaurado: {directory}/{filename}")

                # Descriptografa a chave do manifest
                package_key_enc = manifest.get("key_enc", "").strip()
                package_key = ""

                if package_key_enc:
                    package_key = _pm_decrypt_key(package_key_enc)
                    if package_key:
                        if logger:
                            logger.info(
                                f"Chave descriptografada do pacote: "
                                f"{package_key[:4]}****"
                            )
                    else:
                        if logger:
                            logger.warning(
                                "Falha ao descriptografar chave do pacote "
                                "(dados inválidos ou adulterados)"
                            )
                        package_key = ""

                # Chama callback com a chave DESCRIPTOGRAFADA
                if package_key and on_key_callback:
                    try:
                        on_key_callback(package_key)
                    except Exception as exc:
                        if logger:
                            logger.warning(f"Erro no callback da chave: {exc}")

                msg = (
                    f"Distribuição restaurada com sucesso!\n\n"
                    f"{restored_count} arquivo(s) restaurado(s).\n"
                    f"{'Licença aplicada automaticamente.' if package_key else ''}\n\n"
                    f"Reinicie o QGIS para carregar as classes."
                )

                if logger:
                    logger.info(
                        f"Pacote restaurado: {restored_count} arquivos, "
                        f"chave={'sim' if package_key else 'não'}"
                    )

                return {
                    "success": True,
                    "restored_count": restored_count,
                    "key": package_key,
                    "message": msg,
                }

        except Exception as exc:
            msg = f"Erro ao restaurar distribuição: {exc}"
            if logger:
                logger.error(
                    "Falha ao restaurar distribuição",
                    code="DIST_RESTORE_ERR",
                    error=str(exc),
                )
            return {
                "success": False,
                "restored_count": 0,
                "key": "",
                "message": msg,
            }
