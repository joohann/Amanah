"""
Amanah Aquarium Monitor — const.py
Versie, domeinnaam, MQTT topics, drempelwaarden en profielen.

Versie : 1.0.0
Datum  : 2026-03-06
Auteur : Amanah project
"""

DOMAIN = "amanah"
MANUFACTURER = "Amanah"
MODEL = "Aquarium Monitor"

# Versie — altijd synchroon houden met manifest.json en CHANGELOG.md
VERSION = "1.0.0"
VERSION_DATE = "2025-03-06"

# Config keys
CONF_MQTT_TOPIC = "mqtt_topic"
CONF_AQUARIUM_PROFILE = "aquarium_profile"
CONF_ESPHOME_DEVICE = "esphome_device"
CONF_MQTT_BROKER = "mqtt_broker"
CONF_SKIP_ESPHOME = "skip_esphome"

# Aquarium profielen
PROFILE_FRESHWATER = "freshwater"
PROFILE_SALTWATER = "saltwater"
PROFILES = {
    PROFILE_FRESHWATER: "Zoetwater",
    PROFILE_SALTWATER:  "Zoutwater",
}

# Standaard drempelwaarden per profiel
DEFAULT_THRESHOLDS = {
    PROFILE_FRESHWATER: {
        "temperature_1": {"orange_low": 23.0, "red_low": 20.0, "orange_high": 28.0, "red_high": 30.0},
        "temperature_2": {"orange_low": 23.0, "red_low": 20.0, "orange_high": 28.0, "red_high": 30.0},
    },
    PROFILE_SALTWATER: {
        "temperature_1": {"orange_low": 24.0, "red_low": 22.0, "orange_high": 27.0, "red_high": 29.0},
        "temperature_2": {"orange_low": 24.0, "red_low": 22.0, "orange_high": 27.0, "red_high": 29.0},
    },
}

# ESPHome dashboard Supervisor API
ESPHOME_ADDON_SLUG = "5c53de3b_esphome"
ESPHOME_ADDON_ALT  = "a0d7b954_esphome"  # alternatieve slug (oudere HA versies)
SUPERVISOR_API      = "http://supervisor"
