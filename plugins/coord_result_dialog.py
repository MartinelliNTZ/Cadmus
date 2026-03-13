# -*- coding: utf-8 -*-
from .BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.Preferences import load_tool_prefs, save_tool_prefs


class CoordResultDialog(BasePluginMTL):

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self, iface, info):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.info = info
        # Inicializa logger e preferences do BasePlugin e constrói UI via _build_ui
        self.init(tool_key="coord_result", class_name="CoordResultDialog", build_ui=True)

        # Atualiza com as informações iniciais (widgets já criados em _build_ui)
        try:
            self.update_info(info)
        except Exception:
            pass

    def _build_ui(self, **kwargs):
        """Constrói a UI do diálogo: segue o padrão de GenerateTrailPlugin.        """
        super()._build_ui(
            title="Coordenadas do Ponto",
            icon_path="mtl_agro.ico",
            instructions_file="standard.md",
            enable_scroll=True
        )

        ro_layout, self.wgs_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title="WGS 84 (EPSG:4326)",
            fields={
                'lat_dec': {'title': 'Latitude (Decimal)', 'value': ''},
                'lon_dec': {'title': 'Longitude (Decimal)', 'value': ''},
                'lat_dms': {'title': 'Latitude (DMS)', 'value': ''},
                'lon_dms': {'title': 'Longitude (DMS)', 'value': ''},
            },
            num_columns=1,
            copy_all_button_title="Copiar WGS 84 (Completo)",
        )

        ro_layout2, self.utm_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title="UTM SIRGAS 2000",
            fields={
                'utm_x': {'title': 'Easting (X)', 'value': ''},
                'utm_y': {'title': 'Northing (Y)', 'value': ''},
            },
            num_columns=1,
            copy_all_button_title="Copiar UTM (Completo)",
            separator_bottom=False,
        )
        self.lbl_utm_info = WidgetFactory.create_label(text="", parent=self)

        ro_layout3, self.alt_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title="Altimetria (OpenTopoData)",
            fields={'altitude': {'title': 'Altitude aproximada (m)', 'value': 'Carregando...'}},
            num_columns=1,
            copy_all_button_title=None,
            separator_top=True,
        )
        # Address labels
        self.lbl_municipio = WidgetFactory.create_label(text="", parent=self)
        self.lbl_state_district = WidgetFactory.create_label(text="", parent=self)
        self.lbl_state = WidgetFactory.create_label(text="", parent=self)
        self.lbl_region = WidgetFactory.create_label(text="", parent=self)
        self.lbl_country = WidgetFactory.create_label(text="", parent=self)

        # Botão: Copiar tudo (localização completa) - entre endereço e botões inferiores
        copy_layout, self.btn_copy_all = WidgetFactory.create_simple_button(
            text="Copiar Localização (Completo)",
            parent=self,
            separator_top=False,
            separator_bottom=False,
        )
        self.btn_copy_all.clicked.connect(self.copy_all_info)
        # Bottom action buttons: Executar (fecha), Fechar (fecha), Info (mostra instruções)
        btn_layout, _ = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=lambda: self.close(),
            close_callback=lambda: self.close(),
            info_callback=lambda: self.show_info_dialog(),
            separator_top=False,
            separator_bottom=False,
            tool_key="coord_result",
            run_text="Executar",
            close_text="Fechar",
        )
        # Add everything in a single call
        self.layout.add_items([
            ro_layout,
            ro_layout2,
            self.lbl_utm_info,
            ro_layout3,
            self.lbl_municipio,
            self.lbl_state_district,
            self.lbl_state,
            self.lbl_region,
            self.lbl_country,
            copy_layout,
            btn_layout,
        ])


    def _load_prefs(self):
        """Carrega preferências específicas do diálogo (executado após _build_ui)."""
        try:
            self.preferences = load_tool_prefs(self.TOOL_KEY)
            # Restaurar tamanho da janela se salvo (BasePlugin já faz resize, isto é apenas fallback)
            w = self.preferences.get('window_width')
            h = self.preferences.get('window_height')
            if w and h:
                try:
                    self.resize(int(w), int(h))
                except Exception:
                    pass
            self.logger.debug(f"_load_prefs: loaded prefs keys={list(self.preferences.keys())}")
        except Exception as e:
            try:
                self.logger.warning(f"_load_prefs: erro ao carregar preferencias: {e}")
            except Exception:
                pass

    def _save_prefs(self):
        """Salva preferências do diálogo (window size e outras chaves)."""
        try:
            self.preferences['window_width'] = self.width()
            self.preferences['window_height'] = self.height()
            save_tool_prefs(self.TOOL_KEY, self.preferences)
            try:
                self.logger.debug(f"_save_prefs: prefs salvas: {self.preferences.get('window_width')}x{self.preferences.get('window_height')}")
            except Exception:
                pass
        except Exception as e:
            try:
                self.logger.warning(f"_save_prefs: erro ao salvar preferencias: {e}")
            except Exception:
                pass


    # ==================================================
    # HELPERS
    # ==================================================

    def copy_all_info(self):
        parts = []

        # WGS
        lat_dec = self.wgs_widget.get_value('lat_dec') or ''
        lon_dec = self.wgs_widget.get_value('lon_dec') or ''
        lat_dms = self.wgs_widget.get_value('lat_dms') or ''
        lon_dms = self.wgs_widget.get_value('lon_dms') or ''
        parts.append("WGS 84 (EPSG:4326)")
        parts.append(f"Latitude (Decimal): {lat_dec}")
        parts.append(f"Longitude (Decimal): {lon_dec}")
        if lat_dms or lon_dms:
            parts.append(f"Latitude (DMS): {lat_dms}")
            parts.append(f"Longitude (DMS): {lon_dms}")

        # UTM
        parts.append("UTM SIRGAS 2000")
        parts.append(self.lbl_utm_info.text())
        utm_x = self.utm_widget.get_value('utm_x') or ''
        utm_y = self.utm_widget.get_value('utm_y') or ''
        parts.append(f"Easting (X): {utm_x}")
        parts.append(f"Northing (Y): {utm_y}")

        # Altitude
        alt = self.alt_widget.get_value('altitude') or ''
        parts.append(f"Altitude aproximada (m): {alt}")

        # Address
        parts.append("Endereço (OSM):")
        parts.append(self.lbl_municipio.text())
        parts.append(self.lbl_state_district.text())
        parts.append(self.lbl_state.text())
        parts.append(self.lbl_region.text())
        parts.append(self.lbl_country.text())

        text = "\n".join(parts)
        ok = ProjectUtils.set_clipboard_text(text)
        if ok:   
            QgisMessageUtil.bar_success(self.iface, "Localização copiada para a área de transferência", title="Copiado")   
            self.logger.info("copy_all_info: conteúdo copiado para área de transferência") 
        else:  
            self.logger.warning("copy_all_info: falha ao copiar para área de transferência")
   

    # ==================================================
    # UPDATE (USADO PELO MAPTOOL)
    # ==================================================
    def update_info(self, info):
        self.info = info        
        self.logger.debug(f"update_info: info={info}")

        # WGS
        self.wgs_widget.set_value('lat_dec', f"{info['lat']:.8f}")
        self.wgs_widget.set_value('lon_dec', f"{info['lon']:.8f}")
        self.wgs_widget.set_value('lat_dms', info.get('lat_dms', ''))
        self.wgs_widget.set_value('lon_dms', info.get('lon_dms', ''))

        # UTM
        self.lbl_utm_info.setText(
            f"EPSG:{info['epsg']} | Zona {info['zona_num']}{info['zona_letra']} | "
            f"Hemisfério {info['hemisferio']}"
        )

        self.utm_widget.set_value('utm_x', f"{info['utm_x']:.3f}")
        self.utm_widget.set_value('utm_y', f"{info['utm_y']:.3f}")

        # Reset async fields
        self.alt_widget.set_value('altitude', "Carregando...")
        self.set_address(None)

    # ==================================================
    # TASK CALLBACKS
    # ==================================================
    def set_altitude(self, value):
        self.alt_widget.set_value('altitude',
            "Indisponível" if value is None else f"{value:.2f} m"
        )
        try:
            self.logger.debug(f"set_altitude: {value}")
        except Exception:
            pass

    def set_address(self, data):
        if not data:
            self.lbl_municipio.setText("Município: carregando...")
            self.lbl_state_district.setText("Região Intermediária: carregando...")
            self.lbl_state.setText("Estado: carregando...")
            self.lbl_region.setText("Região: carregando...")
            self.lbl_country.setText("País: carregando...")
            return

        self.lbl_municipio.setText(f"Município: {data.get('municipio', '-')}")
        self.lbl_state_district.setText(
            f"Região Intermediária: {data.get('state_district', '-')}"
        )
        self.lbl_state.setText(f"Estado: {data.get('state', '-')}")
        self.lbl_region.setText(f"Região: {data.get('region', '-')}")
        self.lbl_country.setText(f"País: {data.get('country', '-')}")

        try:
            self.logger.debug(f"set_address: {data}")
        except Exception:
            pass


    def copy_address(self):
        text = (
            f"{self.lbl_municipio.text()}\n"
            f"{self.lbl_state_district.text()}\n"
            f"{self.lbl_state.text()}\n"
            f"{self.lbl_region.text()}\n"
            f"{self.lbl_country.text()}"
        )
        ok = ProjectUtils.set_clipboard_text(text)
        if ok:            
            QgisMessageUtil.bar_success(self.iface, "Endereço copiado para a área de transferência", title="Copiado")
            self.logger.info("copy_address: endereço copiado")

