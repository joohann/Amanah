"""
Amanah Aquarium Monitor — __init__.py
Coordinator, MQTT listener, status evaluatie en device setup.

Versie : 1.0.0
Datum  : 2026-03-06
Auteur : Amanah project
"""
from __future__ import annotations
import json
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import DOMAIN, DEFAULT_THRESHOLDS, CONF_MQTT_TOPIC, CONF_AQUARIUM_PROFILE, PROFILE_FRESHWATER, VERSION

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]
SIGNAL_UPDATE = f"{DOMAIN}_update"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = AmanahCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_setup()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_unload()
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok


def _evaluate(sensor_data: dict, thresholds: dict) -> str:
    status = "green"
    for key, t in thresholds.items():
        val = sensor_data.get(key)
        if val is None:
            continue
        try:
            v = float(val)
        except (TypeError, ValueError):
            continue
        if (t.get("red_low") and v < t["red_low"]) or (t.get("red_high") and v > t["red_high"]):
            return "red"
        if (t.get("orange_low") and v < t["orange_low"]) or (t.get("orange_high") and v > t["orange_high"]):
            status = "orange"
    return status


class AmanahCoordinator:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.sensor_data: dict = {}
        self.overall_status = "green"
        self.base_topic: str = entry.data.get(CONF_MQTT_TOPIC, "amanah")
        profile = entry.data.get(CONF_AQUARIUM_PROFILE, PROFILE_FRESHWATER)
        self.thresholds = entry.options.get("thresholds", DEFAULT_THRESHOLDS.get(profile, {}))
        self._unsubs = []

    async def async_setup(self):
        unsub = await mqtt.async_subscribe(
            self.hass, f"{self.base_topic}/#", self._on_message, qos=1
        )
        self._unsubs.append(unsub)

    async def async_unload(self):
        for u in self._unsubs:
            u()
        self._unsubs.clear()

    @callback
    def _on_message(self, msg) -> None:
        topic: str = msg.topic
        key = topic.removeprefix(f"{self.base_topic}/").replace("/", "_")

        if key.startswith("set_") or key == "overall_status":
            return

        try:
            data = json.loads(msg.payload)
            value = data.get("value", msg.payload)
        except (json.JSONDecodeError, AttributeError):
            value = msg.payload

        try:
            self.sensor_data[key] = float(value)
        except (TypeError, ValueError):
            self.sensor_data[key] = value

        new_status = _evaluate(self.sensor_data, self.thresholds)
        if new_status != self.overall_status:
            self.overall_status = new_status
            # Publiceer status terug naar display
            self.hass.async_create_task(
                mqtt.async_publish(
                    self.hass,
                    f"{self.base_topic}/overall_status",
                    new_status,
                    retain=True,
                )
            )

        async_dispatcher_send(self.hass, f"{SIGNAL_UPDATE}_{self.entry.entry_id}", key)
