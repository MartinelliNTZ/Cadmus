# -*- coding: utf-8 -*-

import traceback
from qgis.core import Qgis, QgsMessageLog
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QWidget,
    QProgressBar,
    QPushButton,
    QMessageBox,
)
from ..resources.IconManager import IconManager as IM
from ..core.config.LogUtils import LogUtils
from .BaseUtil import BaseUtil

logger = LogUtils(tool=BaseUtil.TOOL_KEY_UNTRACEABLE, class_name="QgisMessageUtil")


class QgisMessageUtil(BaseUtil):
    """Utilitário estático para exibir mensagens no QGIS.

    Todos os métodos aceitam `iface` (QgisInterface) como primeiro argumento.
    """

    DEFAULT_LOG_TAG = "Cadmus"

    @staticmethod
    def _icon(attr_name):
        """Compatibilidade Qt5/Qt6: Qt5 usa QMessageBox.{attr_name},
        Qt6 usa QMessageBox.Icon.{attr_name}."""
        try:
            return getattr(QMessageBox.Icon, attr_name)
        except AttributeError:
            return getattr(QMessageBox, attr_name)

    @staticmethod
    def _std_button(attr_name):
        """Compatibilidade Qt5/Qt6: Qt5 usa QMessageBox.{attr_name},
        Qt6 usa QMessageBox.StandardButton.{attr_name}."""
        try:
            return getattr(QMessageBox.StandardButton, attr_name)
        except AttributeError:
            return getattr(QMessageBox, attr_name)

    @staticmethod
    def _btn_role(attr_name):
        """Compatibilidade Qt5/Qt6: Qt5 usa QMessageBox.{attr_name},
        Qt6 usa QMessageBox.ButtonRole.{attr_name}."""
        try:
            return getattr(QMessageBox.ButtonRole, attr_name)
        except AttributeError:
            return getattr(QMessageBox, attr_name)

    NOICON = _icon("NoIcon")
    INFO_ICON = _icon("Information")
    WARNING_ICON = _icon("Warning")
    ERROR_ICON = _icon("Critical")
    QUESTION_ICON = _icon("Question")
    YES_BUTTON = _std_button("Yes")
    NO_BUTTON = _std_button("No")
    ACCEPT_ROLE = _btn_role("AcceptRole")
    ACTION_ROLE = _btn_role("ActionRole")
    REJECT_ROLE = _btn_role("RejectRole")

    # ------------------------------
    # Message bar (não modal)
    # ------------------------------
    @staticmethod
    def _push_message_bar(iface, title, message, level=Qgis.Info, duration=3):
        """Push uma mensagem na message bar do QGIS.

        Parameters
        ----------
        iface : QgisInterface
        title : str
        message : str
        level : Qgis.MessageLevel (Qgis.Info/Qgis.Warning/Qgis.Critical)
        duration : int (segundos)
        """
        # iface.messageBar pode não existir em alguns contextos; tente capturar
        try:
            iface.messageBar().pushMessage(title, message, level, duration)
        except Exception as e:
            logger.debug(f"_push_message_bar: failed with error: {e}")
            # fallback para QMessageBox modal se messageBar não estiver disponível
            QMessageBox.information(iface.mainWindow(), title, message)

    @staticmethod
    def _exec_dialog(dialog):
        """Compatibilidade Qt5/Qt6: executa dialog de forma unificada."""
        if hasattr(dialog, "exec_"):
            return dialog.exec_()
        return dialog.exec()

    @staticmethod
    def modal_result_with_folder(
        iface, title: str, message: str, folder_path: str, parent=None
    ):
        """
        Exibe QMessageBox modal com:
        - contador de sucesso
        - link clicável para pasta
        - lista opcional de erros

        Parameters
        ----------
        iface : QgisInterface
        title : str
            Título da caixa de diálogo
        message : str
            Mensagem HTML
        folder_path : str
            Caminho da pasta para exibir link
        parent : QWidget, optional
            Widget pai (default: usar main window do iface)
        """
        try:
            folder_url = QUrl.fromLocalFile(folder_path).toString()

            # Tentar usar parent widget fornecido, caso contrário usar mainWindow
            parent_widget = parent if parent else iface.mainWindow()

            if parent_widget is None:
                QgisMessageUtil.log(
                    "[modal_result_with_folder] AVISO: parent_widget é None, usando fallback",
                    level=Qgis.Warning,
                )
                parent_widget = None

            msg = QMessageBox(parent_widget)
            msg.setWindowTitle(title)
            msg.setIcon(QgisMessageUtil.INFO_ICON)
            msg.setTextFormat(Qt.TextFormat.RichText)

            text = (
                f"<b>{message}</b> .<br><br>"
                f"<b>Pasta:</b> <a href='{folder_url}'>{folder_path}</a>"
            )

            msg.setText(text)
            result = QgisMessageUtil._exec_dialog(msg)

            QgisMessageUtil.log(
                f"[modal_result_with_folder] Diálogo exibido com sucesso: {title}",
                level=Qgis.Info,
            )
            return result

        except Exception as e:
            QgisMessageUtil.log(
                f"[modal_result_with_folder] ERRO ao exibir diálogo: {str(e)}",
                level=Qgis.Critical,
            )
            QgisMessageUtil.log(
                f"Traceback: {traceback.format_exc()}", level=Qgis.Critical
            )
            # Fallback: tentar exibir via message bar
            try:
                if iface and hasattr(iface, "messageBar"):
                    iface.messageBar().pushMessage(
                        title,
                        message.replace("<b>", "")
                        .replace("</b>", "")
                        .replace("<br><br>", " | "),
                        Qgis.Critical,
                        duration=10,
                    )
            except Exception as fallback_e:
                QgisMessageUtil.log(
                    f"[modal_result_with_folder] Fallback também falhou: {str(fallback_e)}",
                    level=Qgis.Critical,
                )

    @staticmethod
    def bar_info(iface, message, title="Info", duration=3):
        QgisMessageUtil._push_message_bar(iface, title, message, Qgis.Info, duration)

    @staticmethod
    def bar_success(iface, message, title="Sucesso", duration=3):
        # não existe 'Success' em Qgis, usar Info com título Sucesso
        QgisMessageUtil._push_message_bar(iface, title, message, Qgis.Info, duration)

    @staticmethod
    def bar_warning(iface, message, title="Aviso", duration=5):
        QgisMessageUtil._push_message_bar(iface, title, message, Qgis.Warning, duration)

    @staticmethod
    def bar_critical(iface, message, title="Erro", duration=5):
        QgisMessageUtil._push_message_bar(
            iface, title, message, Qgis.Critical, duration
        )

    # ------------------------------
    # Modals (bloqueantes)
    # ------------------------------
    @staticmethod
    def modal_info(iface, message, title="Informação"):
        QMessageBox.information(iface.mainWindow(), title, message)

    @staticmethod
    def modal_success(iface, message, title="Sucesso"):
        # idem info, mas semântica de sucesso
        QMessageBox.information(iface.mainWindow(), title, message)

    @staticmethod
    def modal_warning(iface, message, title="Aviso"):
        QMessageBox.warning(iface.mainWindow(), title, message)

    @staticmethod
    def modal_error(iface, message, title="Erro"):
        QMessageBox.critical(iface.mainWindow(), title, message)

    @staticmethod
    def modal_debug(iface, message, title="Debug"):
        # exibe e também grava no log
        QMessageBox.information(iface.mainWindow(), title, str(message))
        QgisMessageUtil.log(str(message), level=Qgis.Info)

    # ------------------------------
    # Confirmação
    # ------------------------------
    @staticmethod
    def confirm(iface, message, title="Confirmação"):
        resp = QMessageBox.question(
            iface.mainWindow(),
            title,
            message,
            QgisMessageUtil.YES_BUTTON | QgisMessageUtil.NO_BUTTON,
            QgisMessageUtil.NO_BUTTON,
        )
        return resp == QgisMessageUtil.YES_BUTTON

    # ------------------------------
    # Exceções e log
    # ------------------------------
    @staticmethod
    def show_exception(iface, exc: Exception, user_message: str = "Erro"):
        """Mostra uma modal com mensagem amigável e adiciona detalhes ao log.

        A caixa modal oferece o resumo (user_message) e um botão para mostrar
        detalhes (traceback) no console/log. Sempre registra o traceback no log
        do QGIS.
        """
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        tb_text = "".join(tb)
        # registrar no log do QGIS
        QgisMessageUtil.log(tb_text, level=Qgis.Critical)
        # mostrar resumo ao usuário
        QMessageBox.critical(iface.mainWindow(), user_message, str(exc))

    @staticmethod
    def log(message, level=Qgis.Info, tag=None):
        """Escreve no log do QGIS (QgsMessageLog)."""
        QgsMessageLog.logMessage(
            str(message), tag or QgisMessageUtil.DEFAULT_LOG_TAG, level
        )

    @staticmethod
    def ask_field_conflict(iface, field_name):
        msg = QMessageBox(iface.mainWindow())
        msg.setIcon(QgisMessageUtil.QUESTION_ICON)
        msg.setWindowTitle("Campo existente")
        msg.setText(f"O campo '{field_name}' já existe.\nO que deseja fazer?")

        btn_replace = msg.addButton("Substituir", QgisMessageUtil.ACCEPT_ROLE)
        btn_rename = msg.addButton("Renomear", QgisMessageUtil.ACTION_ROLE)

        QgisMessageUtil._exec_dialog(msg)

        clicked = msg.clickedButton()
        if clicked == btn_replace:
            return "replace"
        if clicked == btn_rename:
            return "rename"
        return "cancel"

    @staticmethod
    def ask_overwrite(iface, path: str = "") -> str:
        msg = QMessageBox(iface.mainWindow())
        msg.setIcon(QgisMessageUtil.WARNING_ICON)
        msg.setWindowTitle("Arquivo já existe")
        msg.setText(f"O arquivo já existe:\n{path}")
        msg.setInformativeText("Deseja sobrescrever ou renomear?")
        btn_over = msg.addButton("Sobrescrever", QgisMessageUtil.ACCEPT_ROLE)
        btn_rename = msg.addButton("Renomear", QgisMessageUtil.ACTION_ROLE)
        msg.addButton("Cancelar", QgisMessageUtil.REJECT_ROLE)

        QgisMessageUtil._exec_dialog(msg)

        if msg.clickedButton() == btn_over:
            return "overwrite"
        if msg.clickedButton() == btn_rename:
            return "rename"
        return "cancel"

    @staticmethod
    def confirm_destructive(
        parent, title: str, html_text: str, icon=None, red_text=None
    ) -> bool:
        if icon is None:
            icon = QgisMessageUtil.WARNING_ICON
        if red_text:
            html_text = f"<b style='color:red'>{red_text}</b><br><br>" + html_text

        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setIcon(icon)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(html_text)
        msg.setStandardButtons(QgisMessageUtil.YES_BUTTON | QgisMessageUtil.NO_BUTTON)
        return QgisMessageUtil._exec_dialog(msg) == QgisMessageUtil.YES_BUTTON

    # -------------------------
    # 2. Styled message
    # -------------------------
    @staticmethod
    def show_styled_message_bar(
        iface,
        message="Concluído com sucesso",
        background_color="#2ecc71",
        text_color="white",
        duration=4,
    ):
        """
        Exibe uma mensagem customizada com cores e estilo visual.
        Útil para destacar sucesso, erro ou estados importantes.
        """
        widget = QWidget()
        layout = QHBoxLayout()

        label = QLabel(message)
        label.setStyleSheet(f"color: {text_color}; font-weight: bold;")

        layout.addWidget(label)
        widget.setLayout(layout)

        widget.setStyleSheet(
            f"background-color: {background_color}; padding: 8px; border-radius: 5px;"
        )

        iface.messageBar().pushWidget(widget, level=0, duration=duration)

    @staticmethod
    def show_icon_message_bar(
        iface,
        message="Concluído com sucesso",
        icon_path=IM.icon_path(IM.CADMUS_ICON),
        background_color="#202124",
        text_color="#ffffff",
        duration=4,
        border_radius=8,
        padding="8px 12px",
        font_size=12,
        bold=True,
    ):
        """
        Exibe uma message bar visualmente mais rica.

        - Suporte a ícone via path
        - Layout moderno (espaçamento + alinhamento)
        - Gradiente leve no fundo
        - Texto estilizado
        - Cantos arredondados
        """

        from qgis.PyQt.QtWidgets import QWidget, QHBoxLayout, QLabel
        from qgis.PyQt.QtGui import QPixmap
        from qgis.PyQt.QtCore import Qt

        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        # -------------------------
        # Ícone
        # -------------------------
        if icon_path:
            icon_label = QLabel()

            pix = QPixmap(icon_path).scaled(
                18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )

            icon_label.setPixmap(pix)
            layout.addWidget(icon_label)

        # -------------------------
        # Texto
        # -------------------------
        weight = "bold" if bold else "normal"

        label = QLabel(message)
        label.setStyleSheet(f"""
            color: {text_color};
            font-size: {font_size}px;
            font-weight: {weight};
        """)

        layout.addWidget(label)
        layout.addStretch()

        widget.setLayout(layout)

        # -------------------------
        # Estilo moderno (gradiente)
        # -------------------------
        widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {background_color},
                    stop:1 #000000
                );
                border-radius: {border_radius}px;
                padding: {padding};
            }}
        """)

        iface.messageBar().pushWidget(widget, level=0, duration=duration)

    # -------------------------
    # 3. Progress message
    # -------------------------
    @staticmethod
    def show_progress_message_bar(iface, message="Processando...", maximum=100):
        """
        Exibe uma mensagem com barra de progresso.
        Retorna a barra para atualização manual durante o processamento.
        """
        progress = QProgressBar()
        progress.setMaximum(maximum)

        msg = iface.messageBar().createMessage(message)
        msg.layout().addWidget(progress)

        iface.messageBar().pushWidget(msg, level=0)

        return progress, msg

    @staticmethod
    def update_progress(progress_bar, value):
        """
        Atualiza o valor da barra de progresso.
        """
        progress_bar.setValue(value)

    @staticmethod
    def clear_message_bar(iface):
        """
        Remove todas as mensagens da barra do QGIS.
        Útil para finalizar processos com progresso.
        """
        iface.messageBar().clearWidgets()

    # -------------------------
    # 4. Level-based message
    # -------------------------
    @staticmethod
    def show_level_message_bar(
        iface, title="Status", message="Mensagem", level=0, duration=4
    ):
        """
        Exibe mensagem usando os níveis padrão do QGIS (cores automáticas).
        """
        iface.messageBar().pushMessage(title, message, level=level, duration=duration)

    # Níveis:
    # 0 = Info (azul)
    # 1 = Warning (amarelo)
    # 2 = Critical (vermelho)
    # 3 = Success (verde)

    # -------------------------
    # 5. Message with button
    # -------------------------
    @staticmethod
    def show_message_bar_with_button(
        iface, message="Ocorreu um erro", button_text="Detalhes", callback=None, level=2
    ):
        """
        Exibe uma mensagem com botão interativo.
        Pode ser usado para abrir logs, executar ações ou mostrar detalhes.
        """
        msg = iface.messageBar().createMessage(message)

        button = QPushButton(button_text)

        if callback:
            button.clicked.connect(callback)

        msg.layout().addWidget(button)

        iface.messageBar().pushWidget(msg, level=level)
