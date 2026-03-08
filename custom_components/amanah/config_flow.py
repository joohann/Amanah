"""
Amanah Aquarium Monitor — config_flow.py
Setup wizard: MQTT config, ESPHome detectie, sensor pin keuze.

Versie : 1.0.0
Datum  : 2026-03-06
Auteur : Amanah project
"""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    VERSION,
    DOMAIN,
    CONF_MQTT_TOPIC,
    CONF_AQUARIUM_PROFILE,
    CONF_MQTT_BROKER,
    CONF_SKIP_ESPHOME,
    PROFILES,
    PROFILE_FRESHWATER,
    DEFAULT_THRESHOLDS,
)
from .esphome_setup import check_esphome_addon, create_esphome_device, trigger_esphome_install

_LOGGER = logging.getLogger(__name__)


class AmanahConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Setup wizard voor Amanah."""

    VERSION = 1

    def __init__(self):
        self._data = {}
        self._esphome_available = False

    async def async_step_user(self, user_input=None):
        """Stap 1: Basis aquarium instellingen."""
        errors = {}

        if user_input is not None:
            self._data.update(user_input)

            # Controleer of ESPHome add-on beschikbaar is
            self._esphome_available = await check_esphome_addon(self.hass)

            if self._esphome_available:
                return await self.async_step_esphome()
            else:
                # ESPHome niet beschikbaar — sla stap over
                return await self.async_step_done()

        # HA server IP automatisch detecteren als standaard MQTT broker
        try:
            default_broker = self.hass.config.api.local_ip
        except Exception:
            default_broker = "192.168.1.100"

        schema = vol.Schema({
            vol.Required(CONF_MQTT_TOPIC, default="amanah"): str,
            vol.Required(CONF_MQTT_BROKER, default=default_broker): str,
            vol.Required(CONF_AQUARIUM_PROFILE, default=PROFILE_FRESHWATER): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=k, label=v)
                        for k, v in PROFILES.items()
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "version": f"v{VERSION}",
            },
        )

    async def async_step_esphome(self, user_input=None):
        """
        Stap 2: ESPHome display instellen.
        Vraagt GPIO pin + biedt aan om automatisch het ESPHome device aan te maken én te installeren.
        """
        errors = {}

        if user_input is not None:
            skip = user_input.get(CONF_SKIP_ESPHOME, False)
            sensor_pin = user_input.get("sensor_pin", "GPIO4")
            install_after = user_input.get("install_after_create", False)

            self._data["sensor_pin"] = sensor_pin

            if not skip:
                # Maak het ESPHome device aan
                success, message = await create_esphome_device(
                    self.hass,
                    mqtt_broker=self._data[CONF_MQTT_BROKER],
                    mqtt_base=self._data[CONF_MQTT_TOPIC],
                    sensor_pin=sensor_pin,
                )
                if success:
                    self._data["esphome_created"] = True
                    self._data["esphome_filename"] = message
                    _LOGGER.info("ESPHome device aangemaakt: %s", message)

                    # Optioneel: direct installeren via ESPHome Supervisor API
                    if install_after:
                        install_ok = await trigger_esphome_install(
                            self.hass, device_name="amanah-display"
                        )
                        self._data["esphome_install_triggered"] = install_ok
                        if not install_ok:
                            _LOGGER.warning(
                                "ESPHome install trigger mislukt — flash handmatig via ESPHome dashboard"
                            )
                else:
                    errors["base"] = "esphome_create_failed"
                    self._data["esphome_error"] = message
                    _LOGGER.warning("ESPHome aanmaken mislukt: %s", message)
                    # Toon form opnieuw met foutmelding
                    if errors:
                        return self._show_esphome_form(errors, sensor_pin)

            return await self.async_step_done()

        return self._show_esphome_form({})

    def _show_esphome_form(self, errors, sensor_pin="GPIO4"):
        """Toon het ESPHome configuratieformulier."""
        schema = vol.Schema({
            vol.Required("sensor_pin", default=sensor_pin): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value="GPIO4",  label="GP4  — 1-Wire bus aanbevolen ✓"),
                        selector.SelectOptionDict(value="GPIO1",  label="GP1  — vrij"),
                        selector.SelectOptionDict(value="GPIO2",  label="GP2  — vrij (ADC)"),
                        selector.SelectOptionDict(value="GPIO3",  label="GP3  — vrij (ADC)"),
                        selector.SelectOptionDict(value="GPIO5",  label="GP5  — vrij (ADC)"),
                        selector.SelectOptionDict(value="GPIO6",  label="GP6  — vrij"),
                        selector.SelectOptionDict(value="GPIO7",  label="GP7  — vrij"),
                        selector.SelectOptionDict(value="GPIO8",  label="GP8  — vrij (ADC)"),
                        selector.SelectOptionDict(value="GPIO9",  label="GP9  — vrij (ADC)"),
                        selector.SelectOptionDict(value="GPIO11", label="GP11 — vrij (ADC)"),
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required("install_after_create", default=False): selector.BooleanSelector(),
            vol.Optional(CONF_SKIP_ESPHOME, default=False): selector.BooleanSelector(),
        })

        return self.async_show_form(
            step_id="esphome",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "device_name": "amanah-display",
                "board": "ideaspark ESP32 1.9\" ST7789",
                "wiring": (
                    "DS18B20 aansluiting:\n"
                    "  VCC  →  3.3V\n"
                    "  GND  →  GND\n"
                    "  DATA →  GP4 (1-Wire bus)  +  4.7kΩ weerstand naar 3.3V\n\n**Pinindeling:**\n| Pin | Functie |\n|-----|---------|\n| GP4 | 1-Wire — alle DS18B20 temperatuursensoren |\n| GP5 | pH sensor (ADC) |\n| GP6 | Pomp relay |\n| GP7 | Buzzer / alarm |\n| GP8 | Waterflow (pulse) |\n| GP9 | Waterstand (ADC) |\n| GP10 | Lekdetectie (ADC) |\n| GP2/GP3 | I2C (SDA/SCL) |\n| GP0 | Pagina knop (ingebouwd) |"
                ),
                "install_note": (
                    "Direct installeren werkt alleen als de ESP32 al eerder via USB "
                    "met ESPHome is geflasht en op WiFi bereikbaar is."
                ),
            },
        )

    async def async_step_done(self, user_input=None):
        """Afsluiten en entry aanmaken."""
        return self.async_create_entry(
            title="Amanah Aquarium",
            data=self._data,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AmanahOptionsFlow(config_entry)


class AmanahOptionsFlow(config_entries.OptionsFlow):
    """Opties flow — drempelwaarden aanpassen na setup."""

    def __init__(self, config_entry):
        self._entry = config_entry
        self._profile = config_entry.data.get(CONF_AQUARIUM_PROFILE, PROFILE_FRESHWATER)
        self._thresholds = config_entry.options.get(
            "thresholds",
            DEFAULT_THRESHOLDS.get(self._profile, {}),
        )

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            new_thresholds = self._parse_form(user_input)
            # Push naar coordinator indien aanwezig
            coordinator = self.hass.data.get(DOMAIN, {}).get(self._entry.entry_id)
            if coordinator:
                coordinator.thresholds = new_thresholds
            return self.async_create_entry(title="", data={"thresholds": new_thresholds})

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_schema(),
            description_placeholders={
                "profile": PROFILES.get(self._profile, self._profile)
            },
        )

    def _build_schema(self) -> vol.Schema:
        fields = {}
        for sensor_key in ("temperature_1", "temperature_2"):
            t = self._thresholds.get(sensor_key, {})
            label_map = {
                "orange_low": f"{sensor_key} ⚠️ min °C",
                "red_low":    f"{sensor_key} 🚨 min °C",
                "orange_high": f"{sensor_key} ⚠️ max °C",
                "red_high":    f"{sensor_key} 🚨 max °C",
            }
            for bound, label in label_map.items():
                key = f"{sensor_key}__{bound}"
                default = t.get(bound, 0.0)
                fields[vol.Optional(key, default=default)] = selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        mode=selector.NumberSelectorMode.BOX,
                        step=0.5,
                        unit_of_measurement="°C",
                    )
                )
        return vol.Schema(fields)

    def _parse_form(self, data: dict) -> dict:
        out = {}
        for key, val in data.items():
            if "__" not in key:
                continue
            sensor, bound = key.split("__", 1)
            out.setdefault(sensor, {})[bound] = val
        return out
