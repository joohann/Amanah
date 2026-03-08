# 🐠 Amanah — Aquarium Monitor

[![HACS][hacs-badge]][hacs-url]
[![Validate][validate-badge]][validate-url]
[![Release][release-badge]][release-url]
[![License: MIT][license-badge]][license-url]

> **Amanah** (Arabic: امانة — *vertrouwen, zorgplicht*) — een volledig geautomatiseerd bewakings- en controlesysteem voor zoet- en zoutwateraquaria, gebouwd op ESPHome + Home Assistant.

---

## 📸 Schermafbeeldingen

| Boot scherm | Temperatuur | Status | Netwerk |
|:-----------:|:-----------:|:------:|:-------:|
| *boot logo met gradient* | *2 sensoren landscape* | *statusring* | *WiFi + RSSI* |

---

## ✨ Functies

- 🌡️ **Meerdere DS18B20 temperatuursensoren** op één 1-Wire bus (GP4)
- 🟢🟠🔴 **Drie-niveau statussysteem** — groen / oranje / rood met push notificaties
- 📺 **Landscape IPS display** (320×172, ST7789) met 4 informatiepagina's
- 💡 **RGB status LED** — pulseert bij waarschuwing of gevaar
- 📶 **WiFi + MQTT info** live op display (SSID, IP, signaalsterkte)
- 🔆 **Dimbaar display** vanuit Home Assistant (1–100%)
- 🧩 **HACS integratie** — instaleer via de HACS UI
- ⚙️ **Configuratiewizard** in Home Assistant — geen handmatige YAML nodig
- 🐠 Ondersteunt **zoetwater** en **zoutwater** profielen met aanpasbare drempelwaarden

---

## 🛒 Benodigde hardware

| Component | Aanbevolen | Opmerkingen |
|-----------|-----------|-------------|
| Hoofd controller | [Waveshare ESP32-S3-LCD-1.47B][ws-board] | ESP32-S3, 1.47" IPS, RGB LED, SD slot |
| BLE bridge (Chihiros) | ESP32 (willekeurig) | Alleen nodig voor Chihiros WRGB verlichting |
| Temperatuursensor | DS18B20 (waterproof) | Meerdere op één 1-Wire bus (GP4) |
| Weerstand | 4.7kΩ | Pull-up van DATA naar 3.3V |
| Voeding | 5V USB-C | Via board USB-C connector |

### Pinindeling — Waveshare ESP32-S3-LCD-1.47B

```
GP0  → Pagina knop (ingebouwd BOOT knop)
GP4  → 1-Wire bus — alle DS18B20 temperatuursensoren + 4.7kΩ naar 3V3
GP5  → pH sensor (analoog, ADC)
GP6  → Pomp relay (digitaal uit)
GP7  → Buzzer / alarm (digitaal)
GP8  → Waterflow sensor (pulse counter)
GP9  → Waterstand sensor (analoog, ADC)
GP10 → Lekdetectie (analoog, ADC)
GP2  → I2C SDA (TCS kleurensensor, BME280, etc.)
GP3  → I2C SCL
GP1  → Reserve
GP11 → Reserve (ADC)
```

---

## 📦 Installatie

### Vereisten

- Home Assistant 2024.1.0 of nieuwer
- [HACS][hacs-install] geïnstalleerd
- MQTT broker actief (bijv. Mosquitto add-on)
- ESPHome add-on (aanbevolen, voor automatische firmware installatie)

### Stap 1 — Installeer via HACS

1. Ga in Home Assistant naar **HACS → Integraties**
2. Klik rechtsboven op **⋮ → Aangepaste repositories**
3. Voeg toe: `https://github.com/joohann/amanah` met categorie **Integratie**
4. Zoek op **Amanah** en klik **Downloaden**
5. Herstart Home Assistant

### Stap 2 — Integratie instellen

1. Ga naar **Instellingen → Apparaten & diensten → Integratie toevoegen**
2. Zoek op **Amanah**
3. Volg de configuratiewizard:

   **Stap 1 — MQTT**
   - Broker IP (automatisch ingevuld)
   - MQTT topic prefix (standaard: `amanah`)
   - Aquarium profiel: zoetwater of zoutwater

   **Stap 2 — ESPHome display**
   - Kies GPIO pin voor 1-Wire bus (standaard: **GP4**)
   - Optioneel: directe OTA installatie via WiFi

### Stap 3 — DS18B20 aansluitschema

```
DS18B20 pin 1 (GND)  → GND
DS18B20 pin 2 (DATA) → GP4  ──┬── 4.7kΩ ── 3V3
DS18B20 pin 3 (VCC)  → 3V3    │
                               │ (meerdere sensoren parallel op dezelfde lijn)
```

> **Tip:** Na de eerste flash logt ESPHome alle gevonden 1-Wire adressen. Voeg het adres toe per sensor voor correcte identificatie van boven/onder watertemperatuur.

---

## 🖥️ Display pagina's

Het display toont 4 pagina's die automatisch wisselen (elke 6 seconden) of handmatig via de **BOOT knop**. Lang indrukken (1s+) wisselt tussen automatisch en handmatig.

| Pagina | Inhoud |
|--------|--------|
| **1 — Temperatuur** | Sensor 1 & 2 groot met kleurcodering, delta waarde |
| **2 — Status** | Grote statusring (groen/oranje/rood), T1 & T2 mini |
| **3 — Netwerk** | SSID, IP adres, MQTT broker, signaalsterkte grafisch |
| **4 — Systeem** | Uptime, firmware versie, hardware info, instellingen |

### Displayhelderheid

De displayhelderheid is instelbaar vanuit Home Assistant via het **light entity** `Amanah Display Helderheid`. De instelling wordt onthouden na herstart.

---

## 📡 MQTT topics

| Topic | Richting | Beschrijving |
|-------|----------|--------------|
| `amanah/temperature_1` | ESP → HA | Temperatuur sensor 1 (°C) |
| `amanah/temperature_2` | ESP → HA | Temperatuur sensor 2 (°C) |
| `amanah/temperature_N` | ESP → HA | Extra temperatuursensoren |
| `amanah/overall_status` | HA → ESP | `green` / `orange` / `red` (retained) |

Payload formaat: `{"value": 25.3}`

---

## 🌡️ Drempelwaarden

Instelbaar via **Instellingen → Apparaten & diensten → Amanah → Configureren**

### Standaardwaarden zoetwater

| Parameter | 🟠 Oranje | 🔴 Rood |
|-----------|-----------|---------|
| Temperatuur laag | < 23°C | < 20°C |
| Temperatuur hoog | > 28°C | > 30°C |

### Standaardwaarden zoutwater

| Parameter | 🟠 Oranje | 🔴 Rood |
|-----------|-----------|---------|
| Temperatuur laag | < 24°C | < 22°C |
| Temperatuur hoog | > 27°C | > 29°C |

---

## 🔧 ESPHome firmware

De YAML template staat in `esphome/amanah-display.yaml` en wordt automatisch aangemaakt door de integratie in `/config/esphome/`.

**Handmatig extra sensoren activeren:**

Open `amanah-display.yaml` in de ESPHome editor en verwijder `#` voor de gewenste sensor.
Alle sensor templates (pH, flow, waterstand, lekdetectie, I2C) staan als commentaar klaar.

**Extra DS18B20 toevoegen:**

1. Flash zonder `address:` — ESPHome logt alle adressen automatisch
2. Kopieer het adres uit de logs
3. Voeg toe aan de YAML:
   ```yaml
   - platform: dallas_temp
     name: "Amanah Temperatuur 2"
     address: 0xABCDEF1234567890
   ```

---

## 🤝 Bijdragen

Pull requests zijn welkom! Bekijk de [contributing guidelines](CONTRIBUTING.md) en gebruik de issue templates voor bugs en feature verzoeken.

### Branch strategie

```
main    — stabiele releases
dev     — actieve ontwikkeling
feat/*  — nieuwe functies
fix/*   — bugfixes
```

---

## 📋 Changelog

Zie [CHANGELOG.md](CHANGELOG.md) voor alle wijzigingen per versie.

---

## 📄 Licentie

MIT License — zie [LICENSE](LICENSE) voor details.

---

<!-- badges -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
[validate-badge]: https://github.com/joohann/amanah/actions/workflows/validate.yml/badge.svg
[validate-url]: https://github.com/joohann/amanah/actions/workflows/validate.yml
[release-badge]: https://img.shields.io/github/v/release/joohann/amanah
[release-url]: https://github.com/joohann/amanah/releases
[license-badge]: https://img.shields.io/badge/License-MIT-blue.svg
[license-url]: LICENSE
[hacs-install]: https://hacs.xyz/docs/use/download/download/
[ws-board]: https://www.waveshare.com/wiki/ESP32-S3-LCD-1.47B
