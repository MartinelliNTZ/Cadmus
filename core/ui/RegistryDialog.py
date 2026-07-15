# -*- coding: utf-8 -*-


from qgis.PyQt.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QWidget,
)
from ...plugins.BaseDialog import BaseDialog
from ...i18n.TranslationManager import STR
from ...resources.styles.Styles import Styles
from ..config.LogUtils import LogUtils
from ...utils.ToolKeys import ToolKey
from ..ui.WidgetFactory import WidgetFactory
from ..services.PackageManager import PackageManager


class RegistryDialog(BaseDialog):
    """
    Diálogo modal para gerenciamento de licença e restauração de distribuição.

    Layout:
    - QLineEdit para inserir chave
    - Botão 🔑 para validar
    - Grid: Nível, Validade, Status
    - Botão Apagar Licença
    - GridComplexSelector para selecionar arquivo .dist
    - Botão Restaurar
    - Botão Salvar + Fechar
    """

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.logger = LogUtils(tool=ToolKey.SETTINGS, class_name="RegDialog")

        # Lazy import de RegistryManager — se foi compilado/removido = versão premium
        self.lic_mgr = self._init_lic_mgr()
        self._premium = self.lic_mgr is None

        self.setWindowTitle(STR.REG_TITLE)
        self.setMinimumWidth(400)
        self.setModal(True)

        self._input_key = None
        self._btn_validate = None
        self._lbl_level = None
        self._lbl_expiry = None
        self._lbl_status = None
        self._btn_delete = None
        self._btn_save = None
        self._dist_grid = None
        self._btn_restore = None

        self._build_ui()
        self._refresh()

    @staticmethod
    def _init_lic_mgr():
        """
        Tenta importar RegistryManager com lazy/try.
        Se falhar (classe compilada/removida em distribuição), retorna None.
        None significa versão premium → não precisa de licença.
        """
        try:
            from ..config.RegistryManager import RegistryManager

            return RegistryManager(tool_key=ToolKey.SETTINGS)
        except ImportError:
            return None
        except Exception:
            return None

    # ----------------------------------------------------------------
    # UI
    # ----------------------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Linha: input + botão validar
        key_row = QHBoxLayout()
        key_row.setSpacing(4)

        self._input_key = QLineEdit()
        self._input_key.setPlaceholderText("...")
        self._input_key.setStyleSheet(Styles.input())
        key_row.addWidget(self._input_key)

        self._btn_validate = QPushButton("_")
        self._btn_validate.setFixedWidth(32)
        self._btn_validate.setFixedHeight(24)
        self._btn_validate.setToolTip(STR.VALIDATE)
        self._btn_validate.clicked.connect(self._on_validate)
        key_row.addWidget(self._btn_validate)

        layout.addLayout(key_row)

        # Grid: Nível, Validade, Status
        grid_w = QWidget()
        grid = QGridLayout(grid_w)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 4, 0, 4)

        self._lbl_level_title = QLabel(f"{STR.LEVEL}:")
        self._lbl_level_title.setStyleSheet("font-weight: bold;")
        self._lbl_level = QLabel("-")
        grid.addWidget(self._lbl_level_title, 0, 0)
        grid.addWidget(self._lbl_level, 0, 1)

        self._lbl_expiry_title = QLabel(f"{STR.EXPIRATION_DATE}:")
        self._lbl_expiry_title.setStyleSheet("font-weight: bold;")
        self._lbl_expiry = QLabel("-")
        grid.addWidget(self._lbl_expiry_title, 1, 0)
        grid.addWidget(self._lbl_expiry, 1, 1)

        self._lbl_status_title = QLabel(f"{STR.STATUS}:")
        self._lbl_status_title.setStyleSheet("font-weight: bold;")
        self._lbl_status = QLabel(STR.INACTIVE)
        self._lbl_status.setStyleSheet("color: gray;")
        grid.addWidget(self._lbl_status_title, 2, 0)
        grid.addWidget(self._lbl_status, 2, 1)

        layout.addWidget(grid_w)

        # Botão Apagar
        self._btn_delete = QPushButton(f"🗑️ {STR.REMOVE}")
        self._btn_delete.clicked.connect(self._on_delete)
        layout.addWidget(self._btn_delete)

        # GridComplexSelector para selecionar arquivo .dist
        dist_layout, self._dist_grid = WidgetFactory.create_grid_complex_selector(
            specs={
                "Distribuição": {
                    "label_text": "📦 Arquivo de distribuição (.dist):",
                    "file_filter": "Distribuição Cadmus (*.dist);;Todos os arquivos (*)",
                    "mode_type": "input",
                    "allow_file": True,
                    "allow_folder": False,
                    "multiple": False,
                    "show_project_button": False,
                },
            },
            title="Restaurar Distribuição",
            columns=1,
        )
        layout.addLayout(dist_layout)

        # Botão Restaurar
        self._btn_restore = QPushButton("📦 Restaurar")
        self._btn_restore.clicked.connect(self._on_restore_distribution)
        layout.addWidget(self._btn_restore)

        # Botões Salvar + Fechar
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._btn_save = QPushButton(f"💾 {STR.SAVE}")
        self._btn_save.setFixedHeight(28)
        self._btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(self._btn_save)

        btn_close = QPushButton(STR.CLOSE)
        btn_close.setFixedHeight(28)
        btn_close.clicked.connect(self.reject)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

    # ----------------------------------------------------------------
    # Handlers
    # ----------------------------------------------------------------

    def _on_validate(self):
        self._do_save(show_message=False)

    def _on_save(self):
        self._do_save(show_message=True)

    def _do_save(self, show_message: bool):
        if self.lic_mgr is None:
            # Premium — não precisa de licença
            from ...utils.QgisMessageUtil import QgisMessageUtil

            QgisMessageUtil.modal_info(
                self.iface,
                message="Versão premium — licença não necessária.",
                title=STR.REG_TITLE,
            )
            self.accept()
            return

        key = self._input_key.text().strip()
        if not key:
            self._refresh()
            if show_message:
                from ...utils.QgisMessageUtil import QgisMessageUtil

                QgisMessageUtil.modal_warning(
                    self.iface,
                    message=STR.REGISTRY_EMPTY,
                    title=STR.REG_TITLE,
                )
            return

        result = self.lic_mgr.save_lic_key(key)
        self._refresh()

        if show_message:
            from ...utils.QgisMessageUtil import QgisMessageUtil

            if result.get("success"):
                QgisMessageUtil.modal_info(
                    self.iface,
                    message=STR.REGISTRY_SAVED_SUCCESS,
                    title=STR.REG_TITLE,
                )
                self.accept()
            else:
                QgisMessageUtil.modal_warning(
                    self.iface,
                    message=result.get("message", STR.REGISTRY_INVALID),
                    title=STR.REG_TITLE,
                )

    def _on_delete(self):
        if self.lic_mgr is None:
            return
        self.lic_mgr.delete_lic()
        self._input_key.clear()
        self._refresh()
        from ...utils.QgisMessageUtil import QgisMessageUtil

        QgisMessageUtil.modal_info(
            self.iface,
            message=STR.REGISTRY_DELETED_SUCCESS,
            title=STR.REG_TITLE,
        )

    def _on_restore_distribution(self):
        """
        Restaura as classes do arquivo .dist selecionado para as pastas
        corretas. Delega a instalação para PackageManager.install_package().
        Se o pacote contiver uma chave de licença, ela é aplicada
        automaticamente via callback.
        """
        from ...utils.QgisMessageUtil import QgisMessageUtil
        from pathlib import Path

        # Obtém o caminho do arquivo do GridComplexSelector
        dist_selector = self._dist_grid.get("Distribuição")
        if not dist_selector:
            QgisMessageUtil.modal_warning(
                self.iface,
                message="Seletor de distribuição não encontrado.",
                title="Restaurar Distribuição",
            )
            return

        file_paths = dist_selector.get_paths()
        if not file_paths or not file_paths[0]:
            QgisMessageUtil.modal_warning(
                self.iface,
                message="Selecione um arquivo .dist primeiro.",
                title="Restaurar Distribuição",
            )
            return

        file_path = file_paths[0]
        plugin_root = Path(__file__).resolve().parent.parent.parent

        # Callback para aplicar chave de licença
        def _on_key(key: str):
            self.logger.info(
                f"Chave de licença encontrada no pacote: " f"{key[:4]}****"
            )
            self._input_key.setText(key)
            # Re-inicializa _mgr — agora RegistryManager está disponível
            self.lic_mgr = self._init_lic_mgr()
            self._premium = self.lic_mgr is None

            if self.lic_mgr is not None:
                result = self.lic_mgr.save_lic_key(key)
                if result.get("success"):
                    self.logger.info("Licença do pacote aplicada com sucesso")
                else:
                    self.logger.warning(
                        f"Falha ao aplicar licença do pacote: "
                        f"{result.get('message')}"
                    )

            else:
                self.logger.warning(
                    "Chave encontrada no pacote mas RegistryManager "
                    "não pôde ser carregado após restauração"
                )
            self._refresh()

        # Delega para PackageManager
        result = PackageManager.install_package(
            dist_path=file_path,
            plugin_root=plugin_root,
            on_key_callback=_on_key,
            logger=self.logger,
        )

        if result["success"]:
            # Re-inicializa _lic_mgr
            self.lic_mgr = self._init_lic_mgr()
            self._premium = self.lic_mgr is None

            QgisMessageUtil.modal_info(
                self.iface,
                message=result["message"],
                title="Restaurar Distribuição",
            )

        else:
            QgisMessageUtil.modal_warning(
                self.iface,
                message=result["message"],
                title="Restaurar Distribuição",
            )
        self._refresh()

    def _refresh(self):
        self.logger.info(f"Iniciando refresh{self.lic_mgr}")
        if self.lic_mgr is None:
            # Premium — esconde campos de licença
            self.setWindowTitle(STR.REG_TITLE)
            self._lbl_level_title.setVisible(False)
            self._lbl_level.setVisible(False)
            self._lbl_expiry_title.setVisible(False)
            self._lbl_expiry.setVisible(False)
            self._lbl_status_title.setVisible(False)
            self._lbl_status.setVisible(False)
            self._btn_delete.setVisible(False)
            self._btn_save.setVisible(False)
            self._btn_validate.setVisible(False)
            self._input_key.setVisible(False)
            self._lbl_level_title.setParent(None)
            self._lbl_level.setParent(None)
            self._lbl_expiry_title.setParent(None)
            self._lbl_expiry.setParent(None)
            self._lbl_status_title.setParent(None)
            self._lbl_status.setParent(None)
            self.logger.info(f"Licensa nao encontrada {self.lic_mgr}")
            return

        info = self.lic_mgr.get_registry_info()

        has_key = info.get("has_key", False)
        is_active = info.get("is_active", False)
        is_valid = has_key and is_active

        nivel = info.get("nivel", 0)
        self._lbl_level.setText(str(nivel) if is_valid and nivel > 0 else "")
        self._lbl_expiry.setText(info.get("expiry") if is_valid else "")
        self.logger.info(
            f"Debug has lic: {has_key} lice manager: {self.lic_mgr}, is_valid: {is_valid},is active: {is_active}, info: {info}, nivel: {nivel}"
        )

        # Show/hide title labels based on whether a lic exists
        self._lbl_level_title.setVisible(is_valid)
        self._lbl_expiry_title.setVisible(is_valid)
        self._lbl_status_title.setVisible(is_valid)

        if is_valid:
            self.setWindowTitle(STR.REG_TITLE)
            self._btn_delete.setText(f"🗑️ {STR.REMOVE}")
            self._btn_save.setText(f"💾 {STR.SAVE}")

            days = info.get("days_remaining", 0)
            self._lbl_status.setText(f"{STR.ACTIVE} ({days} {STR.REMAINING_DAYS})")
            self._lbl_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.setWindowTitle("")
            self._btn_delete.setText("")
            self._btn_save.setText("")

            if not has_key:
                self._lbl_status.setText("")
                self._lbl_status.setStyleSheet("color: gray;")
            else:
                self._lbl_status.setText("")
                self._lbl_status.setStyleSheet("color: red; font-weight: bold;")
