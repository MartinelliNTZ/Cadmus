# -*- coding: utf-8 -*-
import os
from ...core.config.LogUtils import LogUtils
from ...plugins.BaseDialog import BaseDialog
from ...core.ui.WidgetFactory import WidgetFactory
from ...i18n.TranslationManager import STR
from ...utils.ToolKeys import ToolKey


class InfoDialog(BaseDialog):
    def __init__(self, instructions_path: str, parent=None, title=STR.APP_NAME, tool_key=ToolKey.UNTRACEABLE):
        super().__init__(parent)
        self.logger = LogUtils(
            tool=tool_key, class_name=self.__class__.__name__, level=LogUtils.DEBUG
        )
        self.logger.debug(f"Inicializando InfoDialog com arquivo: {instructions_path}")

        # Use BaseDialog layout builder so dialogs share the same shell
        self._build_ui(title=title, enable_scroll=False, minimum_size=(700, 550))

        browser = WidgetFactory.create_text_browser(parent=self)

        if os.path.exists(instructions_path):
            with open(instructions_path, "r", encoding="utf-8") as f:
                md_text = f.read()

            # 🔥 Renderização Markdown NATIVA do Qt
            doc = browser.document()
            if hasattr(doc, "setMarkdown"):
                # QGIS mais novo (Qt >= 5.14)
                doc.setMarkdown(md_text)
            else:
                # QGIS 3.16 fallback
                html = self._markdown_to_html(md_text)
                browser.setHtml(html)

        else:
            browser.setPlainText(
                f"{STR.FILE_NOT_FOUND}:\n{instructions_path}"
            )

        self.layout.addWidget(browser)
        btn_layout, btn_widget = WidgetFactory.create_simple_button(
            text=STR.CLOSE, parent=self, spacing=20
        )
        try:
            btn_widget.clicked.connect(self.close)
        except Exception as e:
            self.logger.error(f"InfoDialog: failed to connect close button: {e}")
        self.layout.addLayout(btn_layout)
        self.logger.debug(
            "InfoDialog UI construída com sucesso usando BaseDialog layout."
        )

    def _markdown_to_html(self, text: str) -> str:
        """
        Conversão simples de Markdown para HTML
        Compatível com QGIS 3.16 (sem setMarkdown)
        """
        self.logger.debug("Convertendo Markdown para HTML (fallback)")
        import re

        html = text

        # Títulos
        html = re.sub(r"^###### (.*)", r"<h6>\1</h6>", html, flags=re.MULTILINE)
        html = re.sub(r"^##### (.*)", r"<h5>\1</h5>", html, flags=re.MULTILINE)
        html = re.sub(r"^#### (.*)", r"<h4>\1</h4>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.*)", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.*)", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.*)", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Negrito
        html = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html)

        # Itálico
        html = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html)

        # Quebra de linha
        html = html.replace("\n", "<br>")

        return f"<html><body>{html}</body></html>"
