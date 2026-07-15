# -*- coding: utf-8 -*-
"""
Modelo Qt para tabela de logs.

Implementa QAbstractTableModel para suportar grandes volumes de dados.
Nenhuma lógica de UI aqui - apenas model puro.
"""

from typing import List, Optional
from qgis.PyQt.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from qgis.PyQt.QtGui import QColor
from ..core.model.log_entry import LogEntry
from ..core.color.class_color_provider import ClassColorProvider


# Compatibilidade Qt5/Qt6: Qt5 usa Qt.DisplayRole, Qt6 usa Qt.ItemDataRole.DisplayRole
def _qt_display_role():
    try:
        return Qt.ItemDataRole.DisplayRole
    except AttributeError:
        return Qt.DisplayRole


def _qt_foreground_role():
    """Compatibilidade Qt5/Qt6: retorna ForegroundRole."""
    try:
        return Qt.ItemDataRole.ForegroundRole
    except AttributeError:
        return Qt.ForegroundRole


def _qt_tool_tip_role():
    """Compatibilidade Qt5/Qt6: retorna ToolTipRole."""
    try:
        return Qt.ItemDataRole.ToolTipRole
    except AttributeError:
        return Qt.ToolTipRole


def _qt_user_role():
    """Compatibilidade Qt5/Qt6: retorna UserRole."""
    try:
        return Qt.ItemDataRole.UserRole
    except AttributeError:
        return Qt.UserRole


class LogTableModel(QAbstractTableModel):
    """
    Modelo Qt para exibição de logs em tabela.

    Colunas:
    - Timestamp
    - Level
    - Tool
    - Class
    - Message (truncada)
    """

    COLUMNS = [
        ("Timestamp", "ts"),
        ("Level", "level"),
        ("Tool", "tool"),
        ("Class", "class_name"),
        ("Message", "msg"),
    ]

    def __init__(self, parent=None):
        """Inicializa o modelo."""
        super().__init__(parent)
        self._entries: List[LogEntry] = []
        # Usar ClassColorProvider para AMBAS as colunas (tool + class)
        # Cores determinísticas e consistentes para cada valor único
        self._color_provider = ClassColorProvider()

        # Setup logging
        self._logger = self._get_logger()
        self._set_entries_error_count = 0
        self._data_error_count = 0
        self._logger.info(
            "LogTableModel inicializado", tool="logcat", class_name="LogTableModel"
        )

    @staticmethod
    def _get_logger():
        """Obtém logger para este módulo."""

        from ....core.config.LogUtils import LogUtils

        return LogUtils(tool="logcat", class_name="LogTableModel")

    def set_entries(self, entries: List[LogEntry]) -> None:
        """
        Define as entradas a exibir.
        Usa layoutChanged em vez de beginResetModel para preservar seleção.
        CRÍTICO: Bloqueia atualizações de proxy model durante operação.
        """
        try:
            self._entries = list(entries) if entries else []

            # IMPORTANTE: Bloquear proxy model para evitar crashes durante sincronização
            # Isso previne que QTableView tente acessar índices inválidos durante layoutChanged
            if self.parent() and hasattr(self.parent(), "setDynamicSortFilter"):

                self.parent().setDynamicSortFilter(False)

            # Emitir layoutChanged em vez de beginResetModel
            self.layoutChanged.emit()

            # Re-habilitar proxy model após layoutChanged
            if self.parent() and hasattr(self.parent(), "setDynamicSortFilter"):

                self.parent().setDynamicSortFilter(
                    False
                )  # Manter como False (mais seguro)

        except Exception as e:
            self._set_entries_error_count += 1
            self._logger.error(
                f"Erro em set_entries (ocorrência {self._set_entries_error_count}): {str(e)}",
                error_type=type(e).__name__,
                entries_type=type(entries).__name__,
            )

    def append_entries(self, entries: List[LogEntry]) -> None:
        """
        Adiciona novas entradas ao final.
        Mais eficiente que set_entries para atualizações incrementais.
        """
        try:
            if not entries:
                return

            entries_count = len(entries)
            start_row = len(self._entries)
            end_row = start_row + entries_count - 1

            self.beginInsertRows(QModelIndex(), start_row, end_row)
            try:
                self._entries.extend(entries)
            finally:
                self.endInsertRows()

        except Exception as e:
            self._logger.error(
                f"Erro em append_entries: {e}",
                error_type=type(e).__name__,
                entries_count=len(entries) if entries else 0,
            )

    def clear(self) -> None:
        """Limpa todas as entradas."""
        self.beginResetModel()
        self._entries.clear()
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna número de linhas."""
        if parent.isValid():
            return 0
        return len(self._entries)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna número de colunas."""
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = _qt_display_role()
    ) -> QVariant:
        """Retorna cabeçalho das colunas."""
        if role != _qt_display_role():
            return QVariant()

        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(
            self.COLUMNS
        ):
            return QVariant(self.COLUMNS[section][0])

        if orientation == Qt.Orientation.Vertical:
            return QVariant(str(section + 1))

        return QVariant()

    def data(self, index: QModelIndex, role: int = _qt_display_role()) -> QVariant:
        """Retorna dados para uma célula."""
        try:
            if not index.isValid():
                return QVariant()

            row = index.row()
            col = index.column()

            if not (0 <= row < len(self._entries)):
                return QVariant()

            entry = self._entries[row]
            col_name = self.COLUMNS[col][1]

            # Dados para exibição
            if role == _qt_display_role():
                text = self._get_display_text(entry, col_name)
                return QVariant(text)

            # Cor de texto (level - fonte colorida, não fundo)
            if role == _qt_foreground_role() and col_name == "level":
                try:
                    color = self._get_level_color(entry.level)
                    return QVariant(QColor(color))
                except Exception as e:
                    self._logger.warning(f"Erro ao obter cor de level: {str(e)}")
                    return QVariant()

            # Cor de texto (tool) - usando ClassColorProvider para determinismo
            if role == _qt_foreground_role() and col_name == "tool":
                try:
                    color = self._color_provider.get_color(entry.tool)
                    return QVariant(QColor(color))
                except Exception as e:
                    self._logger.warning(f"Erro ao obter cor de tool: {str(e)}")
                    return QVariant()

            # Cor de texto (class) - usando ClassColorProvider para determinismo
            if role == _qt_foreground_role() and col_name == "class_name":
                try:
                    color = self._color_provider.get_color(entry.class_name)
                    return QVariant(QColor(color))
                except Exception as e:
                    self._logger.warning(f"Erro ao obter cor de class_name: {str(e)}")
                    return QVariant()

            # Tooltip com informação completa (construir string segura)
            if role == _qt_tool_tip_role():
                try:
                    details = f"{entry.ts} | {entry.level} | {entry.tool} | {entry.class_name}\n{entry.msg}"
                    return QVariant(details)
                except Exception as e:
                    self._logger.warning(f"Erro ao obter tooltip: {str(e)}")
                    return QVariant()

            # User role para acesso programático (retornar entry diretamente)
            if role == _qt_user_role():
                return entry  # Retornar diretamente, não em QVariant

            return QVariant()

        except Exception as e:
            self._data_error_count += 1
            self._logger.error(
                f"Erro CRÍTICO em data() (ocorrência {self._data_error_count}): {str(e)}",
                error_type=type(e).__name__,
                role=role,
                index_row=index.row() if index.isValid() else -1,
                index_col=index.column() if index.isValid() else -1,
            )
            return QVariant()

    def _get_display_text(self, entry: LogEntry, col_name: str) -> str:
        """Retorna texto a exibir para uma coluna."""
        if col_name == "ts":
            return entry.ts or "N/A"
        elif col_name == "level":
            return entry.level
        elif col_name == "tool":
            return entry.tool
        elif col_name == "class_name":
            return entry.class_name
        elif col_name == "msg":
            return entry.get_short_message(100)
        return ""

    def _get_level_color(self, level: str) -> str:
        """
        Retorna cor para nível de log.
        Importa cores de LogUtils.
        """
        from ....core.config.LogUtils import LogUtils

        return LogUtils.LEVEL_COLORS.get(level, "#FFFFFF")

    def get_entry(self, index: QModelIndex) -> Optional[LogEntry]:
        """Retorna a entrada em um índice (para detalhe)."""
        if not index.isValid() or index.row() >= len(self._entries):
            return None
        return self._entries[index.row()]

    def get_entry_at(self, row: int) -> Optional[LogEntry]:
        """Retorna a entrada em uma linha específica (por índice inteiro)."""
        if row < 0 or row >= len(self._entries):
            return None
        return self._entries[row]

    def get_all_entries(self) -> List[LogEntry]:
        """Retorna todas as entradas."""
        return self._entries.copy()
