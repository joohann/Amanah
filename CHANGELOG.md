# Changelog — Amanah Aquarium Monitor

Alle wijzigingen per versie worden hier bijgehouden.
Formaat: `[versie] - datum` → wat is er veranderd.

---

## [1.0.0] - 2025-03-06

### Toegevoegd
- Eerste stabiele release van de Amanah HACS integratie
- MQTT-gebaseerde sensordata ontvangst
- 3-niveau status systeem: 🟢 groen / 🟠 oranje / 🔴 rood
- Drempelwaarden instelbaar via Home Assistant UI
- Zoetwater en zoutwater profielen met standaardwaarden
- Temperatuursensoren (2x DS18B20) als HA entiteiten
- Automatische detectie van ESPHome add-on tijdens setup
- Automatisch aanmaken van `amanah-display.yaml` in ESPHome
- Display firmware voor ideaspark ESP32 1.9" ST7789 (170×320)
- 2 display pagina's wisselbaar via ingebouwde knop:
  - Pagina 1: Temperatuur 1 & 2 met kleurcodering
  - Pagina 2: Status overzicht (grote statusbol)
- Backlight PWM dimbaar vanuit Home Assistant
- Overall status terugkoppeling van HA naar display via MQTT
- Nederlandse vertalingen (nl.json)
- OTA firmware updates via ESPHome

---

## [0.2.0] - 2025-02-20

### Toegevoegd
- ESPHome YAML template voor ideaspark ESP32 display
- Basis MQTT sensor integratie (temperatuur)
- Config flow wizard in Home Assistant UI

### Gewijzigd
- Overgestapt van Arduino firmware naar ESPHome

### Verwijderd
- Handmatige Arduino `.ino` firmware (vervangen door ESPHome YAML)

---

## [0.1.0] - 2025-02-01

### Toegevoegd
- Initiële projectstructuur
- Basis HACS integratie setup
- ESP8266 Arduino firmware prototype
- MQTT communicatie basis
