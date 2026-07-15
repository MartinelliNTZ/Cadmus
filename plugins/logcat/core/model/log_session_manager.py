# -*- coding: utf-8 -*-
"""
Gerenciador de sessões de log.

Descobre, cataloga e fornece acesso às sessões de log disponíveis.
"""
from pathlib import Path
from typing import List, Optional
from .log_session import LogSession


class LogSessionManager:
    """
    Gerencia a descoberta e acesso às sessões de log.
    """

    def __init__(self, log_directory: Path):
        """
        Inicializa o gerenciador.

        Args:
            log_directory: Path para a pasta raiz/log
        """
        self.log_directory = Path(log_directory)
        self._sessions_cache: List[LogSession] = []
        self._last_scan_count = 0
        self.refresh()

    def refresh(self) -> None:
        """
        Rescane a pasta de logs para descobrir novos arquivos.
        """
        if not self.log_directory.exists():
            self.log_directory.mkdir(parents=True, exist_ok=True)
            self._sessions_cache = []
            return

        # Encontrar todos os .log
        log_files = sorted(
            self.log_directory.glob("Cadmus_*.log"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,  # Mais recentes primeiro
        )

        self._sessions_cache = [LogSession(f) for f in log_files]

    def get_sessions(self) -> List[LogSession]:
        """
        Retorna lista de sessões (mais recentes primeiro).
        """
        return self._sessions_cache.copy()

    def get_latest_session(self) -> Optional[LogSession]:
        """
        Retorna a sessão mais recente, ou None se não houver logs.
        """
        sessions = self.get_sessions()
        return sessions[0] if sessions else None

    def get_session_by_name(self, name: str) -> Optional[LogSession]:
        """
        Procura uma sessão pelo nome de arquivo.
        """
        for session in self._sessions_cache:
            if session.log_file_path.name == name:
                return session
        return None

    def has_changed(self) -> bool:
        """
        Verifica se a lista de sessões mudou desde a última refresh.
        """
        return len(self._sessions_cache) != self._last_scan_count

    def count(self) -> int:
        """Retorna o número de sessões."""
        return len(self._sessions_cache)
