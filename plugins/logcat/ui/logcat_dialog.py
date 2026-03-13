"""
Diálogo principal do Logcat.

Ferramenta de visualização, análise e filtragem de logs em tempo real.
Inspirada no Logcat do Android Studio.
"""
from pathlib import Path
from typing import Optional, Set, List
from datetime import datetime, timedelta
import os

from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableView, QLineEdit, QPushButton,
    QComboBox, QLabel, QHeaderView, QAbstractItemView, QMessageBox,
    QDateTimeEdit, QCheckBox, QFrame, QScrollArea, QWidget, QListWidget,
    QListWidgetItem
)
from qgis.PyQt.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QModelIndex
from qgis.PyQt.QtGui import QIcon

from ..core.model.log_entry import LogEntry
from ..core.model.log_session_manager import LogSessionManager
from ..core.io.log_loader import LogLoader
from ..core.io.log_file_watcher import LogFileWatcher
from ..core.filter.log_filter_engine import LogFilterEngine
from .log_table_model import LogTableModel
from .log_detail_dialog import LogDetailDialog
from .log_multiple_detail_dialog import LogMultipleDetailDialog
from .log_sort_filter_proxy_model import LogSortFilterProxyModel


class LogcatDialog(QDialog):
    """
    Diálogo principal do Logcat.
    
    Responsabilidades:
    - Gerenciar sessões de log
    - Coordenar carregamento incremental
    - Aplicar filtros
    - Atualizar UI em tempo real
    - Deletar logs (delegando para LogCleanupUtils)
    """
    
    # Sinais para comunicação inter-widgets (thread-safe)
    logs_updated = pyqtSignal()  # Emitido quando logs são atualizados
    file_changed = pyqtSignal()  # Emitido pela thread watcher (thread-safe communication)
    
    def __init__(self, parent=None):
        """
        Inicializa o diálogo.
        
        Args:
            plugin_root: Path para raiz do plugin
            parent: Widget pai
        """
        super().__init__(parent)
        
        # Setup de logging
        self._logger = self._get_logger()
        self._logger.info("LogcatDialog inicialização começando")
        
        # Calcular plugin_root: vai 5 níveis acima (ui -> logcat -> plugins -> Cadmus)
        plugin_root = Path(__file__).resolve().parent.parent.parent.parent
        self.plugin_root = Path(plugin_root)
        self.log_dir = self.plugin_root / "log"
        
        # Componentes de backend
        self.session_manager = LogSessionManager(self.log_dir)
        self.current_session = None
        self.current_loader: Optional[LogLoader] = None
        self.file_watcher: Optional[LogFileWatcher] = None
        
        # Filtros e dados
        self.filter_engine = LogFilterEngine()
        self.all_entries: List[LogEntry] = []
        
        # UI
        self.table_model = LogTableModel()
        
        # Timer para atualizações
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_update_timer)
        
        # Timer para debounce de busca (evitar múltiplos recálculos enquanto digita)
        self.search_debounce_timer = QTimer()
        self.search_debounce_timer.setSingleShot(True)
        self.search_debounce_timer.timeout.connect(self._on_search_debounce_timeout)
        self.search_debounce_timeout_ms = 300  # Esperar 300ms sem digitação para aplicar filtro
        
        # Configuração da janela
        self.setWindowTitle("Cadmus - Logcat")
        self.setMinimumSize(1000, 600)
        self.setModal(False)
        
        # Conectar signal file_changed para atualizar UI de forma thread-safe
        self.file_changed.connect(self._on_file_changed)
        
        # IMPORTANTE: Conectar destroyed signal para garantir cleanup mesmo para diálogos não-modais
        self.destroyed.connect(self._on_destroyed)
        
        # Construir UI
        self._build_ui()
        
        # Carregar sessão padrão (mais recente)
        self._load_default_session()
        
        # Iniciar timer de atualização em tempo real
        self.update_timer.start(1000)  # Atualizar a cada 1 segundo
    
    @staticmethod
    def _get_logger():
        """Obtém logger para este módulo."""
        try:
            from ....core.config.LogUtils import LogUtils
            return LogUtils(tool="logcat", class_name="LogcatDialog")
        except:
            # Fallback - logger fake
            class FakeLogger:
                def debug(self, msg, **kwargs): pass
                def info(self, msg, **kwargs): pass
                def warning(self, msg, **kwargs): pass
                def error(self, msg, **kwargs): pass
                def critical(self, msg, **kwargs): pass
            return FakeLogger()
    
    def _build_ui(self):
        """Constrói a interface do usuário."""
        main_layout = QVBoxLayout()
        
        # ========== Barra de Seleção de Sessão ==========
        session_layout = QHBoxLayout()
        
        session_layout.addWidget(QLabel("Session:"))
        self.combo_sessions = QComboBox()
        self.combo_sessions.currentIndexChanged.connect(self._on_session_changed)
        session_layout.addWidget(self.combo_sessions)
        
        btn_refresh_sessions = QPushButton("Refresh Sessions")
        btn_refresh_sessions.clicked.connect(self._refresh_session_list)
        session_layout.addWidget(btn_refresh_sessions)
        
        session_layout.addStretch()
        main_layout.addLayout(session_layout)
        
        # ========== Barra de Filtros ==========
        filter_layout = QHBoxLayout()
        
        # Filtro de texto livre
        filter_layout.addWidget(QLabel("Search:"))
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Search in all fields...")
        # CRÍTICO: Não conectar direto ao _on_filter_changed para evitar múltiplos recálculos
        # Usar debounce timer em vez disso
        self.edit_search.textChanged.connect(self._on_search_text_changed)
        filter_layout.addWidget(self.edit_search)
        
        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        filter_layout.addWidget(sep1)
        
        # Filtro de Level
        filter_layout.addWidget(QLabel("Level:"))
        self.btn_filter_level = QPushButton("All")
        self.btn_filter_level.clicked.connect(self._on_filter_level_clicked)
        filter_layout.addWidget(self.btn_filter_level)
        
        # Filtro de Tool
        filter_layout.addWidget(QLabel("Tool:"))
        self.btn_filter_tool = QPushButton("All")
        self.btn_filter_tool.clicked.connect(self._on_filter_tool_clicked)
        filter_layout.addWidget(self.btn_filter_tool)
        
        # Filtro de Class
        filter_layout.addWidget(QLabel("Class:"))
        self.btn_filter_class = QPushButton("All")
        self.btn_filter_class.clicked.connect(self._on_filter_class_clicked)
        filter_layout.addWidget(self.btn_filter_class)
        
        # Botão para limpar filtros
        btn_clear_filters = QPushButton("Clear Filters")
        btn_clear_filters.clicked.connect(self._on_clear_filters)
        filter_layout.addWidget(btn_clear_filters)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # ========== Tabela de Logs ==========
        # Criar proxy model para sort
        self.proxy_model = LogSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.table_model)
        # CRÍTICO: Desabilitar dynamic sort durante atualizações em massa (QGIS 3.16 é muito lento)
        # Habilitar apenas quando necessário sorting via UI
        self.proxy_model.setDynamicSortFilter(False)
        
        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)  # Habilitar sort via header
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.MultiSelection)  # Multi-seleção
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setColumnWidth(0, 150)  # Timestamp
        self.table_view.setColumnWidth(1, 80)   # Level
        self.table_view.setColumnWidth(2, 100)  # Tool
        self.table_view.setColumnWidth(3, 120)  # Class
        self.table_view.setColumnWidth(4, 400)  # Message
        
        # Ajustar tamanho de linhas
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSortIndicatorShown(True)  # Mostrar indicador de sort
        
        # Conectar clique duplo para abrir detalhe
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        main_layout.addWidget(self.table_view)
        
        # ========== Barra de Status e Botões ==========
        status_layout = QHBoxLayout()
        
        self.label_status = QLabel("Loading...")
        status_layout.addWidget(self.label_status)
        
        status_layout.addStretch()
        
        # Botão para exportar seleção
        btn_export_selection = QPushButton("Export Selection")
        btn_export_selection.clicked.connect(self._on_export_selection)
        status_layout.addWidget(btn_export_selection)
        
        # Botão para exportar filtro (todos os itens filtrados)
        btn_export_filter = QPushButton("Export Filter")
        btn_export_filter.clicked.connect(self._on_export_filter)
        status_layout.addWidget(btn_export_filter)
        
        # Botões de ação
        btn_clear_session = QPushButton("Clear Session")
        btn_clear_session.clicked.connect(self._on_clear_session)
        status_layout.addWidget(btn_clear_session)
        
        btn_clear_all = QPushButton("Clear All Logs")
        btn_clear_all.clicked.connect(self._on_clear_all_logs)
        status_layout.addWidget(btn_clear_all)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        status_layout.addWidget(btn_close)
        
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
    
    def _load_default_session(self):
        """Carrega a sessão mais recente."""
        latest = self.session_manager.get_latest_session()
        if latest:
            self._load_session(latest)
            self._refresh_session_list()
    
    def _refresh_session_list(self):
        """Atualiza lista de sessões disponíveis."""
        self.session_manager.refresh()
        sessions = self.session_manager.get_sessions()
        
        self.combo_sessions.blockSignals(True)
        self.combo_sessions.clear()
        
        for session in sessions:
            self.combo_sessions.addItem(session.display_name, session)
        
        # Reselecionar sessão atual se existir (BLOQUEANDO signals para evitar loop!)
        if self.current_session:
            for i in range(self.combo_sessions.count()):
                if self.combo_sessions.itemData(i).log_file_path == self.current_session.log_file_path:
                    self.combo_sessions.setCurrentIndex(i)  # Seguro porque blockSignals está True
                    break
        
        # CRUCIAL: Desbloquear APENAS no final
        self.combo_sessions.blockSignals(False)
    
    def _on_session_changed(self, index: int):
        """Chamado quando a sessão é mudada no combo."""
        if index < 0:
            return
        
        session = self.combo_sessions.itemData(index)
        if session:
            self._load_session(session)
    
    def _load_session(self, session):
        """
        Carrega uma sessão de log.
        
        Args:
            session: LogSession a carregar
        """
        try:
            # Parar watcher antigo se existir (evita múltiplas threads)
            if self.file_watcher:
                try:
                    self.file_watcher.stop()
                    self.file_watcher = None
                except Exception as e:
                    self._logger.error(f"Erro ao parar watcher antigo: {str(e)}")
            
            # Limpar saved scroll ao mudar sessão (esperado resetar para topo)
            self._saved_scroll_value = None
            
            # CRÍTICO: Desabilitar proxy model ANTES de mudar dados
            # Isso evita que Qt tente sincronizar durante reorganização
            try:
                self.table_view.setModel(None)
                self.proxy_model.setSourceModel(None)
            except Exception as e:
                self._logger.error(f"Erro ao desabilitar proxy: {str(e)}")
            
            # Carregar nova sessão
            self.current_session = session
            self.current_loader = LogLoader(session.log_file_path)
            
            # Carregar entradas
            self.all_entries = self.current_loader.load_all()
            
            # Limpar modelo antes de popular
            try:
                self.table_model.set_entries([])
            except Exception as e:
                self._logger.error(f"Erro ao limpar modelo: {str(e)}")
            
            # Aplicar filtros (popula table_model com novos dados)
            try:
                search_text = self.edit_search.text()
                self.filter_engine.set_text_filter(search_text)
                filtered = self.filter_engine.apply(self.all_entries)
                self.table_model.set_entries(filtered)
            except Exception as e:
                self._logger.error(f"Erro ao aplicar filtros: {str(e)}")
            
            # Reconectar proxy model DEPOIS que dados estão carregados
            try:
                self.proxy_model.setSourceModel(self.table_model)
                self.table_view.setModel(self.proxy_model)
                self.table_view.resizeColumnsToContents()
            except Exception as e:
                self._logger.error(f"Erro ao reconectar proxy: {str(e)}")
            
            # Iniciar watcher para atualizações em tempo real
            # MAS NÃO monitorar o arquivo do próprio processo (evita loop infinito)
            if not str(session.log_file_path).endswith(f"_pid{os.getpid()}.log"):
                # Arquivo é de outro processo - monitorar
                self.file_watcher = LogFileWatcher(
                    session.log_file_path,
                    on_change=lambda: self.file_changed.emit(),
                    check_interval=1.0
                )
                self.file_watcher.start()
            else:
                self.file_watcher = None
            
            # Atualizar status
            self._update_status()
            
        except Exception as e:
            self._logger.critical(
                f"CRASH PROTECTED: Erro em _load_session: {str(e)}",
                error_type=type(e).__name__,
                session_path=str(session.log_file_path) if hasattr(session, 'log_file_path') else "unknown"
            )
    
    def _on_file_changed(self):
        """Slot chamado de forma thread-safe quando arquivo é modificado."""
        try:
            # Carregar novas linhas
            if self.current_loader:
                new_entries = self.current_loader.load_incremental()
                
                if new_entries:
                    self.all_entries.extend(new_entries)
                    
                    # Salvar posição do scroll ANTES de atualizar
                    self._save_scroll_position()
                    
                    # SOLUÇÃO: Desconectar models antes de atualizar (evita scroll reset)
                    try:
                        # Bloquear signals
                        self.table_view.blockSignals(True)
                        self.proxy_model.blockSignals(True)
                        
                        # Desconectar models
                        self.table_view.setModel(None)
                        self.proxy_model.setSourceModel(None)
                        
                        # Adicionar entradas
                        try:
                            self.table_model.append_entries(new_entries)
                        except Exception as model_e:
                            self._logger.error(f"Erro em append_entries: {str(model_e)}")
                            # Fallback: aplicar todos os filtros
                            self._apply_filters()
                            return
                        
                        # Reconectar models
                        self.proxy_model.setSourceModel(self.table_model)
                        self.table_view.setModel(self.proxy_model)
                        
                    finally:
                        try:
                            self.proxy_model.blockSignals(False)
                            self.table_view.blockSignals(False)
                        except:
                            pass
                    
                    # Restaurar posição do scroll DEPOIS da atualização
                    self._restore_scroll_position()
        
        except Exception as e:
            self._logger.error(
                f"Erro em _on_file_changed: {str(e)}",
                error_type=type(e).__name__
            )
    
    def _on_update_timer(self):
        """Timer para atualizar UI periodicamente."""
        # Verificar novas sessões
        if self.session_manager.has_changed():
            self._refresh_session_list()
    
    def _on_search_text_changed(self):
        """
        Chamado quando texto de busca muda (textChanged signal).
        Implementa debounce para evitar múltiplos recálculos enquanto digita.
        """
        try:
            # Reiniciar timer de debounce
            self.search_debounce_timer.stop()
            self.search_debounce_timer.start(self.search_debounce_timeout_ms)
        except Exception as e:
            self._logger.error(f"Erro em _on_search_text_changed: {str(e)}")
    
    def _on_search_debounce_timeout(self):
        """Chamado quando timeout de debounce expira (300ms sem digitação)."""
        self._on_filter_changed()
    
    def _on_filter_changed(self):
        """Chamado quando filtros são alterados."""
        self._apply_filters()
    
    def _on_filter_level_clicked(self):
        """Abre seletor de níveis."""
        self._show_filter_popup("Level", "level")
    
    def _on_filter_tool_clicked(self):
        """Abre seletor de ferramentas."""
        self._show_filter_popup("Tool", "tool")
    
    def _on_filter_class_clicked(self):
        """Abre seletor de classes."""
        self._show_filter_popup("Class", "class")
    
    def _show_filter_popup(self, title: str, filter_type: str):
        """
        Mostra popup para seleção de filtro.
        
        Args:
            title: Título da popup
            filter_type: Tipo de filtro ("level", "tool", "class")
        """
        # Obter valores únicos
        if filter_type == "level":
            unique_values = sorted(self.filter_engine.get_unique_levels(self.all_entries))
            current_filter = self.filter_engine.level_filter
        elif filter_type == "tool":
            unique_values = sorted(self.filter_engine.get_unique_tools(self.all_entries))
            current_filter = self.filter_engine.tool_filter
        elif filter_type == "class":
            unique_values = sorted(self.filter_engine.get_unique_classes(self.all_entries))
            current_filter = self.filter_engine.class_filter
        else:
            return
        
        # Criar lista widgets
        list_widget = QListWidget()
        for value in unique_values:
            item = QListWidgetItem(value)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if value in current_filter else Qt.Unchecked)
            list_widget.addItem(item)
        
        # Criar dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Filter by {title}")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        def on_ok():
            selected = set()
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if item.checkState() == Qt.Checked:
                    selected.add(item.text())
            
            if filter_type == "level":
                self.filter_engine.set_level_filter(selected)
            elif filter_type == "tool":
                self.filter_engine.set_tool_filter(selected)
            elif filter_type == "class":
                self.filter_engine.set_class_filter(selected)
            
            self._apply_filters()
            dialog.accept()
        
        btn_ok.clicked.connect(on_ok)
        btn_cancel.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def _save_scroll_position(self):
        """Salva posição atual do scroll (para preservar durante filtros)."""
        try:
            scrollbar = self.table_view.verticalScrollBar()
            self._saved_scroll_value = scrollbar.value()
        except Exception as e:
            self._logger.error(f"Erro ao salvar scroll: {str(e)}")
            self._saved_scroll_value = None
    
    def _restore_scroll_position(self):
        """Restaura posição anterior do scroll de forma confiável."""
        try:
            if hasattr(self, '_saved_scroll_value') and self._saved_scroll_value is not None:
                scrollbar = self.table_view.verticalScrollBar()
                saved_val = self._saved_scroll_value  # CRÍTICO: Capturar por valor (não por referência)
                # Usar QTimer com 50ms para garantir que Qt terminou layout
                QTimer.singleShot(50, lambda sv=saved_val: scrollbar.setValue(sv))
        except Exception as e:
            self._logger.error(f"Erro ao restaurar scroll: {str(e)}")
    
    def _do_restore_scroll(self, target_value):
        """[REMOVIDO] Função consolidada em _restore_scroll_position()"""
        pass
    
    def _on_clear_filters(self):
        """Limpa todos os filtros."""
        self.edit_search.setText("")
        self.filter_engine.clear_all()
        self.btn_filter_level.setText("All")
        self.btn_filter_tool.setText("All")
        self.btn_filter_class.setText("All")
        self._apply_filters()
    
    def _apply_filters(self):
        """Aplica filtros e atualiza tabela, preservando scroll e seleção."""
        try:
            # Salvar posição do scroll ANTES de atualizar
            self._save_scroll_position()
            
            # Obter texto de busca
            search_text = self.edit_search.text()
            self.filter_engine.set_text_filter(search_text)
            
            # Aplicar filtros
            filtered = self.filter_engine.apply(self.all_entries)
            
            # SOLUÇÃO PARA SCROLL RESET: Desconectar proxy model antes de atualizar dados
            # Isso evita que QUALQUER signal Qt cause reset automático
            try:
                # Bloquear signals da tabela e proxy
                self.table_view.blockSignals(True)
                self.proxy_model.blockSignals(True)
                
                # Desconectar models
                self.table_view.setModel(None)
                self.proxy_model.setSourceModel(None)
                
                # Atualizar dados
                try:
                    self.table_model.set_entries(filtered)
                except Exception as model_e:
                    self._logger.critical(
                        f"CRASH PROTECTED: Erro em set_entries: {str(model_e)}",
                        error_type=type(model_e).__name__
                    )
                    # Fallback: limpar modelo
                    try:
                        self.table_model.set_entries([])
                    except:
                        pass
                    raise
                
                # Reconectar models
                self.proxy_model.setSourceModel(self.table_model)
                self.table_view.setModel(self.proxy_model)
                
            finally:
                try:
                    self.proxy_model.blockSignals(False)
                    self.table_view.blockSignals(False)
                except:
                    pass
            
            # Atualizar botões de filtro
            try:
                self._update_filter_buttons(filtered)
            except Exception as e:
                self._logger.error(f"Erro ao atualizar filter buttons: {str(e)}")
            
            # Restaurar posição do scroll DEPOIS da atualização
            self._restore_scroll_position()
            
            # Atualizar status
            try:
                self._update_status()
            except Exception as e:
                self._logger.error(f"Erro ao atualizar status: {str(e)}")
            
        except Exception as e:
            self._logger.critical(
                f"CRASH PROTECTED: Erro em _apply_filters: {str(e)}",
                error_type=type(e).__name__,
                all_entries_count=len(self.all_entries) if self.all_entries else 0
            )
    
    def _update_filter_buttons(self, entries: List[LogEntry]):
        """Atualiza rótulos dos botões de filtro."""
        level_count = len(self.filter_engine.level_filter)
        tool_count = len(self.filter_engine.tool_filter)
        class_count = len(self.filter_engine.class_filter)
        
        self.btn_filter_level.setText(
            f"All" if not level_count else f"{level_count} selected"
        )
        self.btn_filter_tool.setText(
            f"All" if not tool_count else f"{tool_count} selected"
        )
        self.btn_filter_class.setText(
            f"All" if not class_count else f"{class_count} selected"
        )
    
    def _on_table_double_click(self, index: QModelIndex):
        """
        Chamado ao duplo-clique na tabela.
        
        CRÍTICO: O índice recebido é do PROXY MODEL (após sorting/filtering).
        Precisa converter para índice do SOURCE MODEL (table_model original).
        """
        try:
            # O index aqui é do proxy_model, converter para source model
            source_index = self.proxy_model.mapToSource(index)
            
            if not source_index.isValid():
                self._logger.warning(f"Índice inválido após mapToSource: proxy_index={index.row()}")
                return
            
            # Agora usar o índice correto do modelo original
            entry = self.table_model.get_entry(source_index)
            if entry:
                self._logger.info(f"Abrindo detalhe: row={source_index.row()}, entry_id={id(entry)}")
                dialog = LogDetailDialog(entry, self)
                dialog.exec_()
            else:
                self._logger.warning(f"Entrada não encontrada em source_index: {source_index.row()}")
        except Exception as e:
            self._logger.error(f"Erro em _on_table_double_click: {str(e)}")
            import traceback
            self._logger.error(f"Stack: {traceback.format_exc()}")
    
    def _on_clear_session(self):
        """Limpa logs da sessão atual."""
        if not self.current_session:
            QMessageBox.warning(self, "Warning", "No session selected")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Clear logs from current session?\n\n{self.current_session.display_name}"
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delegado para LogCleanupUtils
        try:
            from ....core.config.LogCleanupUtils import LogCleanupUtils
            
            # Parar watcher
            if self.file_watcher:
                self.file_watcher.stop()
            
            # Usar LogCleanupUtils.clear_current_session()
            success = LogCleanupUtils.clear_current_session(self.plugin_root)
            
            if success:
                # Recarregar
                self.all_entries.clear()
                self.table_model.clear()
                self._refresh_session_list()
                QMessageBox.information(self, "Success", "Session logs cleared")
            else:
                QMessageBox.warning(self, "Warning", "Could not clear session logs")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear session:\n{str(e)}")
    
    def _on_clear_all_logs(self):
        """Limpa todos os logs."""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Clear ALL log files?\n\nThis cannot be undone."
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Delegado para LogCleanupUtils
        try:
            from ....core.config.LogCleanupUtils import LogCleanupUtils
            
            # Parar watcher
            if self.file_watcher:
                self.file_watcher.stop()
            
            # Usar LogCleanupUtils.clear_all_logs()
            deleted_count = LogCleanupUtils.clear_all_logs(self.plugin_root)
            
            # Recarregar
            self.all_entries.clear()
            self.table_model.clear()
            self._refresh_session_list()
            
            QMessageBox.information(
                self,
                "Success",
                f"Cleared {deleted_count} log file(s)"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear logs:\n{str(e)}")
    
    def _update_status(self):
        """Atualiza barra de status."""
        try:
            total = len(self.all_entries)
            displayed = self.table_model.rowCount()
            
            if self.current_session:
                status_text = f"Showing {displayed}/{total} entries | Session: {self.current_session.display_name}"
            else:
                status_text = f"No session loaded"
            
            self.label_status.setText(status_text)
        except Exception as e:
            self._logger.error(f"Erro ao atualizar status: {str(e)}")
    
    def _on_export_selection(self):
        """Exporta as linhas selecionadas para LogMultipleDetailDialog."""
        # Obter linhas selecionadas (como índices do proxy model)
        selected_indexes = self.table_view.selectionModel().selectedRows()
        
        if not selected_indexes:
            QMessageBox.warning(self, "Warning", "No rows selected")
            return
        
        # Converter índices do proxy para índices do source model
        selected_entries = []
        for proxy_index in selected_indexes:
            source_index = self.proxy_model.mapToSource(proxy_index)
            if source_index.isValid():
                entry = self.table_model.get_entry_at(source_index.row())
                if entry:
                    selected_entries.append(entry)
        
        if not selected_entries:
            QMessageBox.warning(self, "Warning", "Could not retrieve selected entries")
            return
        
        # Se apenas 1 entrada, abrir detalhe único
        if len(selected_entries) == 1:
            dialog = LogDetailDialog(selected_entries[0], self)
            dialog.exec_()
        else:
            # Se múltiplas, abrir diálogo de múltiplas
            dialog = LogMultipleDetailDialog(selected_entries, self)
            dialog.exec_()
    
    def _on_export_filter(self):
        """Exporta todos os itens filtrados para LogMultipleDetailDialog."""
        # Obter todas as linhas visíveis no proxy model (filtradas)
        filtered_entries = []
        for row in range(self.proxy_model.rowCount()):
            index = self.proxy_model.index(row, 0)
            source_index = self.proxy_model.mapToSource(index)
            if source_index.isValid():
                entry = self.table_model.get_entry_at(source_index.row())
                if entry:
                    filtered_entries.append(entry)
        
        if not filtered_entries:
            QMessageBox.warning(self, "Warning", "No filtered entries to export")
            return
        
        # Se apenas 1 entrada, abrir detalhe único
        if len(filtered_entries) == 1:
            dialog = LogDetailDialog(filtered_entries[0], self)
            dialog.exec_()
        else:
            # Se múltiplas, abrir diálogo de múltiplas
            dialog = LogMultipleDetailDialog(filtered_entries, self)
            dialog.exec_()
    
    def closeEvent(self, event):
        """Chamado ao fechar o diálogo - limpeza agressiva."""
        try:
            # PRIORIDADE 1: Parar a thread watcher IMEDIATAMENTE
            if self.file_watcher:
                try:
                    self.file_watcher.stop()
                except Exception:
                    pass
                self.file_watcher = None
            
            # PRIORIDADE 2: Parar timers
            try:
                if self.update_timer and self.update_timer.isActive():
                    self.update_timer.stop()
            except Exception:
                pass
            
            # PRIORIDADE 2b: Parar debounce timer
            try:
                if self.search_debounce_timer and self.search_debounce_timer.isActive():
                    self.search_debounce_timer.stop()
            except Exception:
                pass
            
            # PRIORIDADE 3: Desconectar signals
            try:
                self.file_changed.disconnect()
            except Exception:
                pass
            
            # PRIORIDADE 4: Limpar dados em memória
            try:
                self.all_entries.clear()
                if self.table_model:
                    self.table_model.clear()
            except Exception:
                pass
            
        except Exception:
            pass  # closeEvent nunca falha
        finally:
            event.accept()
    
    def _on_destroyed(self):
        """Slot chamado quando o widgets é destruído (mesmo não-modal)."""
        # Executar mesma limpeza de closeEvent
        try:
            if self.file_watcher:
                try:
                    self.file_watcher.stop()
                except Exception:
                    pass
                self.file_watcher = None
            
            if self.update_timer:
                try:
                    if self.update_timer.isActive():
                        self.update_timer.stop()
                except Exception:
                    pass
            
            if self.search_debounce_timer:
                try:
                    if self.search_debounce_timer.isActive():
                        self.search_debounce_timer.stop()
                except Exception:
                    pass
        except Exception:
            pass  # _on_destroyed nunca falha
