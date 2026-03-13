"""
Variáveis globais compartilhadas para sincronização de logging.
"""
import threading

# Lock único e global para sincronizar leitura/escrita do arquivo de log
LOG_FILE_LOCK = threading.Lock()
