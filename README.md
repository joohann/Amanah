# 🐠 Amanah — Aquarium Monitor

[![HACS][hacs-badge]][hacs-url]
[![Validate][validate-badge]][validate-url]
[![Release][release-badge]][release-url]
[![License: MIT][license-badge]][license-url]

> **Amanah** (Arabic: امانة — *trust, duty of care*) — a fully automated monitoring and control system for freshwater and saltwater aquariums, built on ESPHome + Home Assistant.

---

## 📸 Screenshots

| Boot screen | Temperature | Status | Network |
|:-----------:|:-----------:|:------:|:-------:|
| *boot logo with gradient* | *2 sensors landscape* | *status ring* | *WiFi + RSSI* |

---

## ✨ Features

- 🌡️ **Multiple DS18B20 temperature sensors** on a single 1-Wire bus (GP4)
- 🟢🟠🔴 **Three-level status system** — green / orange / red with push notifications
- 📺 **Landscape IPS display** (320×172, ST7789) with 4 information pages
- 💡 **RGB status LED** — pulses on warning or danger
- 📶 **WiFi + MQTT info** live on display (SSID, IP address, signal strength)
- 🔆 **Dimmable display** from Home Assistant (1–100%)
- 🧩 **HACS integration** — install via the HACS UI
- ⚙️ **Configuration wizard** in Home Assistant — no manual YAML required
- 🐠 Supports **freshwater** and **saltwater** profiles with adjustable thresholds

---

## 🛒 Required Hardware

| Component | Recommended | Notes |
|-----------|-------------|-------|
| Main controller | [Waveshare ESP32-S3-LCD-1.47B][ws-board] | ESP32-S3, 1.47" IPS, RGB LED, SD slot |
| BLE bridge (Chihiros) | ESP32 (any) | Only needed for Chihiros WRGB lighting |
| Temperature sensor | DS18B20 (waterproof) | Multiple on one 1-Wire bus (GP4) |
| Resistor | 4.7kΩ | Pull-up from DATA to 3.3V |
| Power supply | 5V USB-C | Via board USB-C connector |

### Pin Layout — Waveshare ESP32-S3-LCD-1.47B

```
GP0  → Page button (built-in BOOT button)
GP4  → 1-Wire bus — all DS18B20 temperature sensors + 4.7kΩ to 3V3
GP5  → pH sensor (analog, ADC)
GP6  → Pump relay (digital out)
GP7  → Buzzer / alarm (digital)
GP8  → Water flow sensor (pulse counter)
GP9  → Water level sensor (analog, ADC)
GP10 → Leak detection (analog, ADC)
GP2  → I2C SDA (TCS color sensor, BME280, etc.)
GP3  → I2C SCL
GP1  → Reserved
GP11 → Reserved (ADC)
```

---

## 📦 Installation

### Requirements

- Home Assistant 2024.1.0 or newer
- [HACS][hacs-install] installed
- Active MQTT broker (e.g. Mosquitto add-on)
- ESPHome add-on (recommended, for automatic firmware installation)

### Step 1 — Install via HACS

1. In Home Assistant go to **HACS → Integrations**
2. Click **⋮ → Custom repositories** in the top right
3. Add: `https://github.com/joohann/amanah` with category **Integration**
4. Search for **Amanah** and click **Download**
5. Restart Home Assistant

### Step 2 — Configure the integration

1. Go to **Settings → Devices & services → Add integration**
2. Search for **Amanah**
3. Follow the configuration wizard:

   **Step 1 — MQTT**
   - Broker IP (auto-filled)
   - MQTT topic prefix (default: `amanah`)
   - Aquarium profile: freshwater or saltwater

   **Step 2 — ESPHome display**
   - Choose GPIO pin for 1-Wire bus (default: **GP4**)
   - Optional: direct OTA installation via WiFi

### Step 3 — DS18B20 wiring

```
DS18B20 pin 1 (GND)  → GND
DS18B20 pin 2 (DATA) → GP4  ──┬── 4.7kΩ ── 3V3
DS18B20 pin 3 (VCC)  → 3V3    │
                               │ (multiple sensors in parallel on the same line)
```

> **Tip:** After the first flash, ESPHome logs all discovered 1-Wire addresses. Add the address per sensor for correct identification of top/bottom water temperature.

---

## 🖥️ Display Pages

The display shows 4 pages that rotate automatically (every 6 seconds) or manually via the **BOOT button**. Long press (1s+) toggles between automatic and manual mode.

| Page | Content |
|------|---------|
| **1 — Temperature** | Sensor 1 & 2 large with color coding, delta value |
| **2 — Status** | Large status ring (green/orange/red), T1 & T2 mini |
| **3 — Network** | SSID, IP address, MQTT broker, graphical signal strength |
| **4 — System** | Uptime, firmware version, hardware info, settings |

### Display Brightness

Display brightness is adjustable from Home Assistant via the **light entity** `Amanah Display Brightness`. The setting is remembered after a restart.

---

## 📡 MQTT Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `amanah/temperature_1` | ESP → HA | Temperature sensor 1 (°C) |
| `amanah/temperature_2` | ESP → HA | Temperature sensor 2 (°C) |
| `amanah/temperature_N` | ESP → HA | Additional temperature sensors |
| `amanah/overall_status` | HA → ESP | `green` / `orange` / `red` (retained) |

Payload format: `{"value": 25.3}`

---

## 🌡️ Thresholds

Configurable via **Settings → Devices & services → Amanah → Configure**

### Freshwater defaults

| Parameter | 🟠 Orange | 🔴 Red |
|-----------|-----------|--------|
| Temperature low | < 23°C | < 20°C |
| Temperature high | > 28°C | > 30°C |

### Saltwater defaults

| Parameter | 🟠 Orange | 🔴 Red |
|-----------|-----------|--------|
| Temperature low | < 24°C | < 22°C |
| Temperature high | > 27°C | > 29°C |

---

## 🔧 ESPHome Firmware

The YAML template is located in `esphome/amanah-display.yaml` and is automatically created by the integration in `/config/esphome/`.

**Manually enabling extra sensors:**

Open `amanah-display.yaml` in the ESPHome editor and remove `#` from the desired sensor block. All sensor templates (pH, flow, water level, leak detection, I2C) are included as commented-out blocks ready to activate.

**Adding extra DS18B20 sensors:**

1. Flash without an `address:` — ESPHome automatically logs all addresses
2. Copy the address from the logs
3. Add to the YAML:
   ```yaml
   - platform: dallas_temp
     name: "Amanah Temperature 2"
     address: 0xABCDEF1234567890
   ```

---

## 🤝 Contributing

Pull requests are welcome! Check the [contributing guidelines](CONTRIBUTING.md) and use the issue templates for bugs and feature requests.

### Branch strategy

```
main    — stable releases
dev     — active development
feat/*  — new features
fix/*   — bug fixes
```

---

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for all changes per version.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

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
