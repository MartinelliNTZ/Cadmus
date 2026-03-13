"""
Monitoramento de arquivos de log em tempo real.

Detecta quando o arquivo cresce e notifica observadores.
"""
from pathlib import Path
from typing import Callable, Optional, List
from datetime import datetime, timedelta
import threading
import time


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
        check_interval: float = 0.5
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
                name="LogFileWatcher"
            )
            self._watch_thread.start()
    
    def stop(self) -> None:
        """Para o monitoramento com segurança máxima."""
        try:
            # PASSO 1: Sinalizar parada via lock
            try:
                with self._lock:
                    self._is_watching = False
            except Exception:
                pass
            
            # PASSO 2: Aguardar thread terminar com múltiplas tentativas
            if self._watch_thread and self._watch_thread.is_alive():
                # Tentar join com timeout progressivo
                for attempt in range(3):
                    timeout = 1.0 * (attempt + 1)
                    try:
                        self._watch_thread.join(timeout=timeout)
                        if not self._watch_thread.is_alive():
                            break
                    except Exception:
                        pass
            
            self._watch_thread = None
        except Exception:
            pass  # stop() nunca falha
    
    def _update_file_stats(self) -> None:
        """Atualiza tamanho e mtime do arquivo."""
        try:
            if self.log_file_path.exists():
                stat = self.log_file_path.stat()
                self._last_size = stat.st_size
                self._last_mtime = stat.st_mtime
        except Exception:
            pass
    
    def _has_changed(self) -> bool:
        """Verifica se o arquivo foi modificado."""
        try:
            if not self.log_file_path.exists():
                return False
            
            stat = self.log_file_path.stat()
            return stat.st_size != self._last_size or stat.st_mtime != self._last_mtime
        except Exception:
            return False
    
    def _watch_loop(self) -> None:
        """
        Loop de monitoramento (executado em thread).
        
        Extremamente defensivo - qualquer erro termina a thread graciosamente.
        """
        try:
            while True:
                # Checar se deve parar - com máxima proteção
                should_stop = False
                try:
                    with self._lock:
                        should_stop = not self._is_watching
                except Exception:
                    should_stop = True
                
                if should_stop:
                    break
                
                # Checar mudanças com proteção total
                try:
                    if self._has_changed():
                        try:
                            self._update_file_stats()
                        except Exception:
                            pass
                        
                        if self.on_change:
                            try:
                                self.on_change()
                            except Exception:
                                pass
                except Exception:
                    pass
                
                # Sleep com máxima proteção - se falhar, encerrar thread
                try:
                    # Usar loop pequeno em vez de sleep longo para responder ao stop() rápido
                    for _ in range(10):
                        time.sleep(self.check_interval / 10.0)
                        # Checar novamente se foi solicitado parar durante o sleep
                        try:
                            with self._lock:
                                if not self._is_watching:
                                    break
                        except Exception:
                            break
                except Exception:
                    break  # Sleep falhou - terminar thread
        except Exception:
            pass  # Última rede de segurança - thread nunca quebra QGIS
        finally:
            # Garantir que _is_watching seja False
            try:
                with self._lock:
                    self._is_watching = False
            except Exception:
                pass
    
    def is_watching(self) -> bool:
        """Retorna True se está monitorando."""
        with self._lock:
            return self._is_watching
