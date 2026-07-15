# -*- coding: utf-8 -*-
from ..utils.ToolKeys import ToolKey

from .BasePlugin import BasePluginMTL
from ..core.ui.WidgetFactory import WidgetFactory
from ..utils.ProjectUtils import ProjectUtils
from ..utils.QgisMessageUtil import QgisMessageUtil
from ..utils.Preferences import Preferences
from ..i18n.TranslationManager import STR


class CoordResultDialog(BasePluginMTL):
    TOOL_KEY = ToolKey.COORD_CLICK_TOOL

    def __init__(self, iface, info):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.info = info
        self.init(
            tool_key=self.TOOL_KEY, class_name="CoordResultDialog", build_ui=True
        )

        try:
            self.update_info(info)
        except Exception as e:
            self.logger.error(f"Error {e}")

    def _build_ui(self, **kwargs):
        super()._build_ui(
            title=STR.POINT_COORDINATES,
            icon_path="mtl_agro.ico",
            enable_scroll=True,
        )

        ro_layout, self.wgs_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title=STR.WGS84_EPSG4326,
            fields={
                "lat_dec": {"title": STR.LATITUDE_DECIMAL, "value": ""},
                "lon_dec": {"title": STR.LONGITUDE_DECIMAL, "value": ""},
                "lat_dms": {"title": STR.LATITUDE_DMS, "value": ""},
                "lon_dms": {"title": STR.LONGITUDE_DMS, "value": ""},
            },
            num_columns=1,
            copy_all_button_title=STR.COPY_WGS84_FULL,
        )

        ro_layout2, self.utm_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title=STR.UTM_SIRGAS_2000,
            fields={
                "utm_x": {"title": STR.EASTING_X, "value": ""},
                "utm_y": {"title": STR.NORTHING_Y, "value": ""},
            },
            num_columns=1,
            copy_all_button_title=STR.COPY_UTM_FULL,
            separator_bottom=False,
        )
        self.lbl_utm_info = WidgetFactory.create_label(text="", parent=self)

        ro_layout3, self.alt_widget = WidgetFactory.create_readonly_field(
            parent=self,
            title=STR.ALTIMETRY_OPENTOPO,
            fields={
                "altitude": {
                    "title": STR.APPROX_ALTITUDE_METERS,
                    "value": STR.LOADING,
                }
            },
            num_columns=1,
            copy_all_button_title=None,
            separator_top=True,
        )

        self.lbl_municipio = WidgetFactory.create_label(text="", parent=self)
        self.lbl_state_district = WidgetFactory.create_label(text="", parent=self)
        self.lbl_state = WidgetFactory.create_label(text="", parent=self)
        self.lbl_region = WidgetFactory.create_label(text="", parent=self)
        self.lbl_country = WidgetFactory.create_label(text="", parent=self)

        copy_layout, self.btn_copy_all = WidgetFactory.create_simple_button(
            text=STR.COPY_LOCATION_FULL,
            parent=self,
            separator_top=False,
            separator_bottom=False,
        )
        self.btn_copy_all.clicked.connect(self.copy_all_info)

        btn_layout, _ = WidgetFactory.create_bottom_action_buttons(
            parent=self,
            run_callback=lambda: self.close(),
            close_callback=lambda: self.close(),
            info_callback=lambda: self.show_info_dialog(),
            separator_top=False,
            separator_bottom=False,
            tool_key=self.TOOL_KEY,
            run_text=STR.EXECUTE,
            close_text=STR.CLOSE,
        )

        self.layout.add_items(
            [
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
            ]
        )

    def _load_prefs(self):
        self.logger.debug(
            f"_load_prefs: loaded prefs keys={list(self.preferences.keys())}"
        )

    def _save_prefs(self):
        Preferences.save_tool_prefs(self.TOOL_KEY, self.preferences)
        self.logger.debug(
            f"_save_prefs: prefs salvas: {self.preferences.get('window_width')}x{self.preferences.get('window_height')}"
        )

    def copy_all_info(self):
        parts = []

        lat_dec = self.wgs_widget.get_value("lat_dec") or ""
        lon_dec = self.wgs_widget.get_value("lon_dec") or ""
        lat_dms = self.wgs_widget.get_value("lat_dms") or ""
        lon_dms = self.wgs_widget.get_value("lon_dms") or ""
        parts.append(STR.WGS84_EPSG4326)
        parts.append(f"{STR.LATITUDE_DECIMAL}: {lat_dec}")
        parts.append(f"{STR.LONGITUDE_DECIMAL}: {lon_dec}")
        if lat_dms or lon_dms:
            parts.append(f"{STR.LATITUDE_DMS}: {lat_dms}")
            parts.append(f"{STR.LONGITUDE_DMS}: {lon_dms}")

        parts.append(STR.UTM_SIRGAS_2000)
        parts.append(self.lbl_utm_info.text())
        utm_x = self.utm_widget.get_value("utm_x") or ""
        utm_y = self.utm_widget.get_value("utm_y") or ""
        parts.append(f"{STR.EASTING_X}: {utm_x}")
        parts.append(f"{STR.NORTHING_Y}: {utm_y}")

        alt = self.alt_widget.get_value("altitude") or ""
        parts.append(f"{STR.APPROX_ALTITUDE_METERS}: {alt}")

        parts.append(STR.ADDRESS_OSM)
        parts.append(self.lbl_municipio.text())
        parts.append(self.lbl_state_district.text())
        parts.append(self.lbl_state.text())
        parts.append(self.lbl_region.text())
        parts.append(self.lbl_country.text())

        text = "\n".join(parts)
        ok = ProjectUtils.set_clipboard_text(text)
        if ok:
            QgisMessageUtil.bar_success(
                self.iface,
                STR.LOCATION_COPIED_TO_CLIPBOARD,
                title=STR.COPIED,
            )
            self.logger.info(
                "copy_all_info: conteúdo copiado para área de transferência"
            )
        else:
            self.logger.warning(
                "copy_all_info: falha ao copiar para área de transferência"
            )

    def update_info(self, info):
        self.info = info
        self.logger.debug(f"update_info: info={info}")

        self.wgs_widget.set_value("lat_dec", f"{info['lat']:.8f}")
        self.wgs_widget.set_value("lon_dec", f"{info['lon']:.8f}")
        self.wgs_widget.set_value("lat_dms", info.get("lat_dms", ""))
        self.wgs_widget.set_value("lon_dms", info.get("lon_dms", ""))

        self.lbl_utm_info.setText(
            f"EPSG:{info['epsg']} | {STR.ZONE} {info['zona_num']}{info['zona_letra']} | "
            f"{STR.HEMISPHERE} {info['hemisferio']}"
        )

        self.utm_widget.set_value("utm_x", f"{info['utm_x']:.3f}")
        self.utm_widget.set_value("utm_y", f"{info['utm_y']:.3f}")

        self.alt_widget.set_value("altitude", STR.LOADING)
        self.set_address(None)

    def set_altitude(self, value):
        self.alt_widget.set_value(
            "altitude", STR.UNAVAILABLE if value is None else f"{value:.2f} m"
        )
        self.logger.debug(f"set_altitude: {value}")

    def set_address(self, data):
        if not data:
            self.lbl_municipio.setText(f"{STR.CITY}: {STR.LOADING_LOWER}")
            self.lbl_state_district.setText(
                f"{STR.INTERMEDIATE_REGION}: {STR.LOADING_LOWER}"
            )
            self.lbl_state.setText(f"{STR.STATE}: {STR.LOADING_LOWER}")
            self.lbl_region.setText(f"{STR.REGION}: {STR.LOADING_LOWER}")
            self.lbl_country.setText(f"{STR.COUNTRY}: {STR.LOADING_LOWER}")
            return

        self.lbl_municipio.setText(f"{STR.CITY}: {data.get('municipio', '-')}")
        self.lbl_state_district.setText(
            f"{STR.INTERMEDIATE_REGION}: {data.get('state_district', '-')}"
        )
        self.lbl_state.setText(f"{STR.STATE}: {data.get('state', '-')}")
        self.lbl_region.setText(f"{STR.REGION}: {data.get('region', '-')}")
        self.lbl_country.setText(f"{STR.COUNTRY}: {data.get('country', '-')}")
        self.logger.debug(f"set_address: {data}")

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
            QgisMessageUtil.bar_success(
                self.iface,
                STR.ADDRESS_COPIED_TO_CLIPBOARD,
                title=STR.COPIED,
            )
            self.logger.info("copy_address: endereço copiado")
        else:
            self.logger.warning(
                "copy_address: falha ao copiar para área de transferência"
            )
