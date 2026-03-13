"""
Proxy model para tabela de logs com suporte a sort.

Permite ordenar por qualquer coluna em ordem crescente/decrescente.
"""
from qgis.PyQt.QtCore import Qt, QSortFilterProxyModel, QDateTime, QModelIndex
from pathlib import Path


class LogSortFilterProxyModel(QSortFilterProxyModel):
    """
    Proxy model que adiciona suporte a sort e filter à tabela de logs.
    """
    
    def __init__(self, parent=None):
        """Inicializa o proxy model."""
        super().__init__(parent)
        # Configurar sort
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        # Suportar sort por múltiplas colunas
        self.setRecursiveFilteringEnabled(True)
        
        # Setup de logging
        self._logger = self._get_logger()
        self._lessThan_error_count = 0
        self._parent_error_count = 0
        self._logger.info("LogSortFilterProxyModel inicializado", tool="logcat", class_name="LogSortFilterProxyModel")
    
    @staticmethod
    def _get_logger():
        """Obtém logger para este módulo."""
        try:
            from ....core.config.LogUtils import LogUtils
            return LogUtils(tool="logcat", class_name="LogSortFilterProxyModel")
        except:
            # Fallback - logger fake
            class FakeLogger:
                def debug(self, msg, **kwargs): pass
                def info(self, msg, **kwargs): pass
                def warning(self, msg, **kwargs): pass
                def error(self, msg, **kwargs): pass
            return FakeLogger()
    
    def parent(self, child):
        """
        CRÍTICO: Sobrescreve parent() para evitar crash em QTableView::visualRect.
        Qt 5.11 em QGIS 3.16 falha ao validar índices de pai.
        
        MÁXIMA PROTEÇÃO: Captura QUALQUER erro e retorna index seguro.
        Isso evita que QTableView.visualRect() cause crash do app.
        """
        try:
            # Validação rigorosa do índice filho - NUNCA falha
            try:
                if not child.isValid():
                    return QModelIndex()
            except Exception as e:
                self._parent_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao validar child: {str(e)}")
                return QModelIndex()
            
            # Chamar parent do proxy model - ENVOLTO EM PROTEÇÃO
            try:
                result = super().parent(child)
            except RuntimeError as e:
                self._parent_error_count += 1
                self._logger.error(f"RuntimeError capturado em super().parent(): {str(e)}")
                return QModelIndex()
            except Exception as e:
                self._parent_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro em super().parent(): {str(e)}")
                return QModelIndex()
            
            # Validar resultado - PROTEÇÃO MÁXIMA
            try:
                if result.isValid():
                    try:
                        row = result.row()
                    except Exception as e:
                        self._parent_error_count += 1
                        self._logger.critical(f"CRASH PROTECTED: Erro ao acessar result.row(): {str(e)}")
                        return QModelIndex()
                    
                    # Verificar range - NÃO chamar rowCount() durante mudança de modelo
                    # rowCount() pode ser inseguro durante sync
                    try:
                        if 0 <= row < 100000:  # Limite máximo razoável
                            return result
                    except Exception as e:
                        self._parent_error_count += 1
                        self._logger.critical(f"CRASH PROTECTED: Erro ao validar range: {str(e)}")
                    
                    return QModelIndex()
                else:
                    return result  # Índice inválido é OK para root
            except Exception as e:
                self._parent_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao validar result: {str(e)}")
                return QModelIndex()
        
        except Exception as e:
            # ÚLTIMO BACKUP - Catchall final
            self._parent_error_count += 1
            self._logger.critical(
                f"CRASH PROTECTED FINAL: Erro não capturado em parent() (#{self._parent_error_count}): {str(e)}",
                error_type=type(e).__name__
            )
            return QModelIndex()
    
    def lessThan(self, source_left, source_right):
        """
        Implementa comparação customizada para sort.
        
        MÁXIMA PROTEÇÃO: Captura qualquer erro e retorna False seguro.
        Evita crash durante troca de sessão/modelo.
        """
        try:
            # Validar índices - crucial para evitar crash quando proxy está sincronizando
            try:
                if not source_left.isValid() or not source_right.isValid():
                    return False
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao validar índices em lessThan: {str(e)}")
                return False
            
            try:
                col = source_left.column()
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao obter coluna em lessThan: {str(e)}")
                return False
            
            try:
                source_model = self.sourceModel()
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao obter sourceModel em lessThan: {str(e)}")
                return False
            
            # Validar modelo
            if not source_model:
                return False
            
            try:
                if not hasattr(source_model, 'COLUMNS') or col < 0 or col >= len(source_model.COLUMNS):
                    return False
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao validar COLUMNS em lessThan: {str(e)}")
                return False
            
            try:
                col_name = source_model.COLUMNS[col][1]
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro ao obter col_name em lessThan: {str(e)}")
                return False
            
            # Tentar obter entries diretamente do modelo com validação
            entry_left = None
            entry_right = None
            
            if hasattr(source_model, '_entries'):
                try:
                    entries = source_model._entries
                    left_row = source_left.row()
                    right_row = source_right.row()
                    
                    # Validação rigorosa de índices
                    if entries and 0 <= left_row < len(entries) and 0 <= right_row < len(entries):
                        entry_left = entries[left_row]
                        entry_right = entries[right_row]
                except (IndexError, AttributeError, TypeError, RuntimeError) as e:
                    self._lessThan_error_count += 1
                    self._logger.error(f"CRASH PROTECTED: Erro ao acessar entries em lessThan: {str(e)}")
                    return False
                except Exception as e:
                    self._lessThan_error_count += 1
                    self._logger.critical(f"CRASH PROTECTED: Erro inesperado ao acessar entries: {str(e)}")
                    return False
            
            # Se conseguiu ambas as entries, usar lógica customizada
            if entry_left and entry_right:
                try:
                    # Sort por timestamp (ISO format é ordenável como string)
                    if col_name == "ts":
                        try:
                            return (entry_left.ts or "") < (entry_right.ts or "")
                        except Exception as e:
                            self._lessThan_error_count += 1
                            self._logger.critical(f"CRASH PROTECTED: Erro em sort timestamp: {str(e)}")
                            return False
                    
                    # Sort por level (usando ordem lógica)
                    if col_name == "level":
                        try:
                            level_order = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
                            left_val = level_order.get(entry_left.level, 99)
                            right_val = level_order.get(entry_right.level, 99)
                            return left_val < right_val
                        except Exception as e:
                            self._lessThan_error_count += 1
                            self._logger.critical(f"CRASH PROTECTED: Erro em sort level: {str(e)}")
                            return False
                except Exception as e:
                    self._lessThan_error_count += 1
                    self._logger.critical(f"CRASH PROTECTED: Erro em comparação customizada: {str(e)}")
                    return False
            
            # Sort padrão para outros campos
            try:
                return super().lessThan(source_left, source_right)
            except (RuntimeError, IndexError) as e:
                self._lessThan_error_count += 1
                self._logger.error(f"CRASH PROTECTED: Erro em sort padrão: {str(e)}")
                return False
            except Exception as e:
                self._lessThan_error_count += 1
                self._logger.critical(f"CRASH PROTECTED: Erro inesperado em sort padrão: {str(e)}")
                return False
        
        except Exception as e:
            # ÚLTIMO BACKUP - Catchall final
            self._lessThan_error_count += 1
            self._logger.critical(
                f"CRASH PROTECTED FINAL: Erro não capturado em lessThan (#{self._lessThan_error_count}): {str(e)}"
            )
            return False
