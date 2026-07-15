# -*- coding: utf-8 -*-
"""
Monitoramento de arquivos de log em tempo real.

Detecta quando o arquivo cresce e notifica observadores.
"""
from pathlib import Path
from typing import Callable, Optional
import threading
import time
import logging


class LogFileWatcher:
    """
    Monitora mudanças em arquivo de log em tempo real.

    Usa timer + checagem de tamanho (simples e portável).
    Notifica callbacks quando há novas linhas.
    """

    def __init__(
        self,
        log_file_path: Path,
        on_change: Optional[Callable] = None,
        check_interval: float = 0.5,
    ):
        """
        Inicializa o watcher.

        Args:
            log_file_path: Path para o arquivo .log
            on_change: Callable() chamado quando arquivo muda
            check_interval: Intervalo de checagem em segundos (padrão 0.5s)
        """
        self.log_file_path = Path(log_file_path)
        self.on_change = on_change
        self.check_interval = check_interval

        self._is_watching = False
        self._watch_thread: Optional[threading.Thread] = None
        self._last_size = 0
        self._last_mtime = 0.0
        self._lock = threading.Lock()
        # Logger local (não importa LogUtils para evitar loops durante init)
        self.logger = logging.getLogger("Cadmus.logcat.LogFileWatcher")

    def start(self) -> None:
        """Inicia monitoramento em thread separada."""
        with self._lock:
            if self._is_watching:
                return

            self._is_watching = True
            self._update_file_stats()

            # NÃO usar daemon=True - garantir limpeza apropriada
            self._watch_thread = threading.Thread(
                target=self._watch_loop,
                daemon=False,  # Não é daemon - aguarda stop()
                name="LogFileWatcher",
            )
            self._watch_thread.start()

    def stop(self) -> None:
        """Para o monitoramento com segurança máxima."""
        try:
            # PASSO 1: Sinalizar parada via lock
            with self._lock:
                self._is_watching = False

            # PASSO 2: Aguardar thread terminar com múltiplas tentativas
            if self._watch_thread and self._watch_thread.is_alive():
                # Tentar join com timeout progressivo
                for attempt in range(3):
                    timeout = 1.0 * (attempt + 1)
                    self._watch_thread.join(timeout=timeout)
                    if not self._watch_thread.is_alive():
                        break

            self._watch_thread = None

        except Exception as e:
            self.logger.error(f"Erro ao parar monitoramento: {e}")

    def _update_file_stats(self) -> None:
        """Atualiza tamanho e mtime do arquivo."""
        try:
            if self.log_file_path.exists():
                stat = self.log_file_path.stat()
                self._last_size = stat.st_size
                self._last_mtime = stat.st_mtime
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas do arquivo: {e}")

    def _has_changed(self) -> bool:
        """Verifica se o arquivo foi modificado."""
        try:
            if not self.log_file_path.exists():
                return False

            stat = self.log_file_path.stat()
            return stat.st_size != self._last_size or stat.st_mtime != self._last_mtime
        except Exception as e:
            self.logger.error(f"Erro ao checar mudanças no arquivo: {e}")
            return False

    def _watch_loop(self) -> None:
        """
        Loop de monitoramento (executado em thread).

        Extremamente defensivo - qualquer erro termina a thread graciosamente.
        """
        try:
            while True:
                # Checar se deve parar
                with self._lock:
                    if not self._is_watching:
                        break

                # Checar mudanças
                if self._has_changed():
                    self._update_file_stats()

                    if self.on_change:
                        self.on_change()

                # Sleep curto para responder rápido ao stop()
                for _ in range(10):
                    time.sleep(self.check_interval / 10.0)

                    with self._lock:
                        if not self._is_watching:
                            break

        except Exception as e:
            self.logger.error(f"Erro no loop de monitoramento: {e}")

        finally:
            # Garantir que _is_watching seja False
            try:
                with self._lock:
                    self._is_watching = False
            except Exception as e:
                self.logger.error(f"Erro ao finalizar monitoramento: {e}")

    def is_watching(self) -> bool:
        """Retorna True se está monitorando."""
        with self._lock:
            return self._is_watching
