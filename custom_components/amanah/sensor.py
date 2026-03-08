"""
Amanah Aquarium Monitor — sensor.py
Temperatuur sensoren, status sensor en versie sensor entiteiten.

Versie : 1.0.0
Datum  : 2026-03-06
Auteur : Amanah project
"""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN, SIGNAL_UPDATE, AmanahCoordinator
from .const import VERSION, VERSION_DATE, MANUFACTURER, MODEL

TEMP_SENSORS = {
    "temperature_1": "Temperatuur 1",
    "temperature_2": "Temperatuur 2",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator: AmanahCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AmanahTempSensor(coordinator, entry, k, n)
        for k, n in TEMP_SENSORS.items()
    ]
    entities.append(AmanahVersionSensor(coordinator, entry))
    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    """Gedeelde device info — versienummer zichtbaar in HA apparaatinfo header."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Amanah Aquarium",
        manufacturer=MANUFACTURER,
        model=MODEL,
        sw_version=VERSION,
        configuration_url="https://github.com/joohann/amanah/blob/main/CHANGELOG.md",
    )


class AmanahTempSensor(SensorEntity):
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "°C"
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: AmanahCoordinator, entry: ConfigEntry, key: str, name: str):
        self._coordinator = coordinator
        self._key = key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = f"Amanah {name}"

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self._entry)

    @property
    def native_value(self):
        val = self._coordinator.sensor_data.get(self._key)
        try:
            return round(float(val), 1) if val is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self):
        return {
            "status": self._coordinator.overall_status,
            "amanah_version": VERSION,
        }

    async def async_added_to_hass(self):
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_UPDATE}_{self._entry.entry_id}",
                self._on_update,
            )
        )

    @callback
    def _on_update(self, key):
        if key is None or key == self._key:
            self.async_write_ha_state()


class AmanahVersionSensor(SensorEntity):
    """Versie sensor — toont huidige Amanah versie in HA."""

    _attr_icon = "mdi:tag-outline"

    def __init__(self, coordinator: AmanahCoordinator, entry: ConfigEntry):
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_version"
        self._attr_name = "Amanah Versie"

    @property
    def device_info(self) -> DeviceInfo:
        return _device_info(self._entry)

    @property
    def native_value(self) -> str:
        return VERSION

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "versie": VERSION,
            "release_datum": VERSION_DATE,
            "changelog": "https://github.com/joohann/amanah/blob/main/CHANGELOG.md",
            "esphome_device": self._entry.data.get("esphome_filename", "niet aangemaakt"),
            "aquarium_profiel": self._entry.data.get("aquarium_profile", "onbekend"),
            "mqtt_topic": self._entry.data.get("mqtt_topic", "amanah"),
        }

    async def async_added_to_hass(self):
        pass
