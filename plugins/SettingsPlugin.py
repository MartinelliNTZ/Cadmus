# -*- coding: utf-8 -*-
"""
SettingsPlugin - Configurações do Cadmus

Exibe preferências do aplicativo e configurações de cálculo vetorial.
"""

from qgis.PyQt.QtWidgets import QLabel, QMessageBox
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import QUrl, Qt

from ..plugins.BasePlugin import BasePluginMTL
from ..utils.Preferences import load_tool_prefs, save_tool_prefs
from ..utils.ToolKeys import ToolKey
from ..core.ui.WidgetFactory import WidgetFactory
from ..core.config.LogUtils import LogUtils
from ..utils.StringUtils import StringUtils


class SettingsPlugin(BasePluginMTL):
    """
    Plugin de configurações do Cadmus.
    
    Permite ao usuário:
    - Acessar preferências do aplicativo
    - Configurar método de cálculo vetorial (Elipsoidal, Cartesiana, Ambos)
    """

    CALCULATION_METHODS = ["Elipsoidal", "Cartesiana", "Ambos"]

    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.init(ToolKey.SETTINGS, "SettingsPlugin")
        self.logger.info("SettingsPlugin inicializado")

    def _build_ui(self, **kwargs):
        """Constrói a interface de configurações."""
        self.logger.debug("Construindo interface de configurações")
        
        super()._build_ui(
            title="Configurações Cadmus",
            icon_path="system.ico",
            instructions_file="settings_help.md"
        )
        
        self.logger.info("Construindo componentes de interface")

        # ========== SEÇÃO 1: Preferências do App ==========
        prefs_label = QLabel("📋 Preferências do Aplicativo")
        prefs_label.setStyleSheet("font-weight: bold; font-size: 11pt;")

        # Link clicável para preferências
        pref_link = QLabel(
            '<a href="open_prefs" style="color: #0066cc; text-decoration: underline;">Abrir Pasta de Preferências</a>'
        )
        pref_link.setOpenExternalLinks(False)
        pref_link.setCursor(Qt.PointingHandCursor)
        pref_link.linkActivated.connect(self._on_open_preferences)

        self.logger.debug("Link de preferências adicionado")

        # ========== SEÇÃO 2: Método de Cálculo Vetorial ==========
        calc_layout, self.radio_calc = WidgetFactory.create_radio_button_grid(
            items=self.CALCULATION_METHODS,
            columns=3,
            title="⚙️ Método de Cálculo Vetorial",
            checked_index=0,
            tool_key=ToolKey.SETTINGS,
            separator_top=True,
            separator_bottom=True,
            parent=self
        )
        self.logger.debug("Widget de cálculo vetorial adicionado")
        
        # ========== SEÇÃO 3: Precisão para campos vetoriais ==========
        prec_layout, self.spin_precision = WidgetFactory.create_double_spin_input(
            "🎯 Precisão de campos vetoriais (casas decimais):",
            decimals=0,
            step=1,
            minimum=0,
            maximum=10,
            value=2,
            separator_top=True,
            separator_bottom=False,
        )
        self.logger.debug("Widget de precisão de campos vetoriais adicionado")

        # ========== SEÇÃO 4: Limiar de processamento assíncrono ==========
        # Agora o valor é o número máximo de feições que podem ser processadas
        # de forma síncrona; tudo acima irá disparar execução em segundo plano.
        thresh_layout, self.spin_threshold = WidgetFactory.create_double_spin_input(
            "📦 Limiar assíncrono (nº de feições):",
            decimals=0,
            step=1,
            minimum=1,
            maximum=100000000,  # valor alto para não limitar demais
            value=1000,
            separator_top=False,
            separator_bottom=True,
        )
        self.logger.debug("Widget de limiar assíncrono por feições adicionado")

        # ========== BOTÕES DE AÇÃO ==========
        buttons_layout, self.action_buttons = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=self.execute_tool,
            close_callback=self.close,
            info_callback=self.show_info_dialog,
            tool_key=ToolKey.SETTINGS,
            run_text = "Salvar"
        )
        
        # ========== ADICIONAR TODOS OS ITEMS DE UMA VEZ ==========
        # Importante: adicionar items em uma ÚNICA chamada a add_items()
        # para evitar reparentings repetidos que destroem widgets internos
        self.layout.add_items([
            prefs_label,
            pref_link,
            calc_layout,
            prec_layout,
            thresh_layout,
            buttons_layout
        ])
        self.logger.info("Interface de configurações construída com sucesso")

    def _load_prefs(self):
        """Carrega preferências salvas."""
        self.logger.debug("Carregando preferências")
        self.preferences = load_tool_prefs(ToolKey.SETTINGS)

        # Carregar método de cálculo selecionado
        calc_method = self.preferences.get('calculation_method', 'Elipsoidal')
        try:
            idx = self.CALCULATION_METHODS.index(calc_method)
            self.radio_calc.set_selected_index(idx)
            self.logger.debug(f"Método de cálculo carregado: {calc_method}")
        except (ValueError, IndexError):
            self.logger.warning(f"Método de cálculo inválido: {calc_method}, usando padrão")
            self.radio_calc.set_selected_index(0)

        # Carregar limiar assíncrono (número de feições)
        # suporte retrocompatível: se usuário ainda tiver threshold em bytes, avisar e usar padrão
        if 'async_threshold_features' in self.preferences:
            thresh_feats = self.preferences.get('async_threshold_features', 1000)
        else:
            old_bytes = self.preferences.get('async_threshold_bytes')
            if old_bytes is not None:
                self.logger.warning("Preferência antiga 'async_threshold_bytes' encontrada, substituindo por limite de feições padrão")
            thresh_feats = 1000
        try:
            self.spin_threshold.setValue(int(thresh_feats))
            self.logger.debug(f"Limiar assíncrono carregado: {thresh_feats} feições")
        except Exception:
            self.logger.warning(f"Erro ao carregar limiar assíncrono: {thresh_feats}")

        # Carregar precisão de campos vetoriais
        prec = self.preferences.get('vector_field_precision', 2)
        try:
            self.spin_precision.setValue(int(prec))
            self.logger.debug(f"Precisão de campos vetoriais carregada: {prec}")
        except Exception:
            self.logger.warning(f"Erro ao carregar precisão de campos vetoriais: {prec}")

    def _save_prefs(self):
        """Salva preferências."""
        self.logger.debug("Salvando preferências")
        
        # Salvar método de cálculo selecionado
        selected_text = self.radio_calc.get_selected_text()
        self.preferences['calculation_method'] = selected_text

        # Salvar limiar assíncrono (número de feições)
        feats_value = int(self.spin_threshold.value())
        self.preferences['async_threshold_features'] = feats_value
        self.logger.debug(f"Limiar assíncrono por feições salvo: {feats_value} feições")

        # Salvar precisão de campos vetoriais
        precision_val = int(self.spin_precision.value())
        self.preferences['vector_field_precision'] = precision_val
        self.logger.debug(f"Precisão de campos vetoriais salva: {precision_val} casas")

        save_tool_prefs(ToolKey.SETTINGS, self.preferences)
        self.logger.info(f"Preferências salvas: cálculo={selected_text}")

    def execute_tool(self):
        """Executa as configurações e fecha o diálogo."""
        self.logger.info("Aplicando configurações")
        self._save_prefs()
        
        selected_method = self.radio_calc.get_selected_text()
        QMessageBox.information(
            self,
            "Configurações Salvas",
            f"Método de cálculo vetorial: {selected_method}\n\n"
            f"As configurações foram salvas com sucesso."
        )
        
        self.logger.info("Configurações aplicadas e salvas")
        self.close()

    def _on_open_preferences(self):
        """Abre a pasta de preferências do Cadmus."""
        self.logger.debug("Abrindo pasta de preferências")
        
        from ..utils.Preferences import PREF_FOLDER
        import os
        
        if os.path.exists(PREF_FOLDER):
            self.logger.info(f"Abrindo pasta: {PREF_FOLDER}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(PREF_FOLDER))
        else:
            self.logger.warning(f"Pasta de preferências não encontrada: {PREF_FOLDER}")
            QMessageBox.warning(
                self,
                "Aviso",
                f"Pasta de preferências não encontrada:\n{PREF_FOLDER}"
            )


def run_settings(iface):
    """Função de entrada do plugin."""
    dlg = SettingsPlugin(iface)
    dlg.setModal(False)
    dlg.show()
    return dlg
