"""
Amanah Aquarium Monitor — esphome_setup.py
ESPHome add-on detectie, YAML template generatie en OTA install trigger.

Versie : 1.0.0
Datum  : 2026-03-06
Auteur : Amanah project
"""
from __future__ import annotations

import logging
import aiohttp

from homeassistant.core import HomeAssistant

from .const import (
    ESPHOME_ADDON_SLUG,
    ESPHOME_ADDON_ALT,
    SUPERVISOR_API,
)

_LOGGER = logging.getLogger(__name__)

# De YAML template die we in ESPHome aanmaken
# mqtt_broker en device_name worden ingevuld via substitutions
ESPHOME_YAML_TEMPLATE = """\
# ============================================================
# Amanah Display — ESPHome firmware
# Versie : 1.0.0
# Datum  : 2026-03-07
# Board  : Waveshare ESP32-S3-LCD-1.47B / DIY NOW ESP32-S3-LCD-1.47
# Gegenereerd door Amanah HACS integratie — niet handmatig aanpassen,
# gebruik de Amanah integratie opties om instellingen te wijzigen.
# ============================================================

substitutions:
  device_name: amanah-display
  friendly_name: "Amanah Display"
  mqtt_broker: "{mqtt_broker}"
  mqtt_base: "{mqtt_base}"
  sensor_pin: "{sensor_pin}"
  # Aanbevolen pinindeling Waveshare ESP32-S3-LCD-1.47B:
  # GP0  = Pagina knop (BOOT, ingebouwd)
  # GP4  = 1-Wire bus — alle DS18B20 temperatuursensoren (+ 4.7kΩ naar 3V3)
  # GP5  = pH sensor (analoog, ADC)
  # GP6  = Pomp relay (digitaal uit)
  # GP7  = Alarm buzzer / reserve (digitaal)
  # GP8  = Waterflow sensor (pulse counter)
  # GP9  = Waterstand sensor (analoog, ADC)
  # GP10 = Lekdetectie (analoog, ADC)
  # GP2  = I2C SDA — TCS kleurensensor / waterkwaliteit
  # GP3  = I2C SCL — TCS kleurensensor / waterkwaliteit
  # GP11 = Reserve (ADC)
  # GP1  = Reserve

esphome:
  name: ${{device_name}}
  friendly_name: ${{friendly_name}}
  project:
    name: "amanah.display"
    version: "1.0.0"
  on_boot:
    priority: -100
    then:
      - light.turn_on:
          id: backlight
          brightness: 100%
      # RGB LED: groen bij opstarten, totdat status van HA binnenkomt
      - light.turn_on:
          id: rgb_led
          red: 0%
          green: 100%
          blue: 0%
          brightness: 40%
          effect: none

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  framework:
    type: arduino

logger:
  level: INFO

ota:
  - platform: esphome

api:

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "Amanah Setup"
    password: "amanah123"

captive_portal:

mqtt:
  broker: ${{mqtt_broker}}
  port: 1883
  client_id: "amanah_display"
  on_message:
    - topic: "${{mqtt_base}}/temperature_1"
      then:
        - lambda: |-
            json::parse_json(x, [](JsonObject root) -> bool {{
              if (root.containsKey("value")) id(temp1_val) = root["value"].as<float>();
              return true;
            }});
    - topic: "${{mqtt_base}}/temperature_2"
      then:
        - lambda: |-
            json::parse_json(x, [](JsonObject root) -> bool {{
              if (root.containsKey("value")) id(temp2_val) = root["value"].as<float>();
              return true;
            }});
    - topic: "${{mqtt_base}}/overall_status"
      then:
        - lambda: |-
            id(overall_status_str) = x;
        - if:
            condition:
              lambda: 'return x == "green";'
            then:
              - light.turn_on:
                  id: rgb_led
                  red: 0%
                  green: 100%
                  blue: 0%
                  brightness: 40%
                  effect: none
        - if:
            condition:
              lambda: 'return x == "orange";'
            then:
              - light.turn_on:
                  id: rgb_led
                  red: 100%
                  green: 45%
                  blue: 0%
                  brightness: 60%
                  effect: "Langzaam pulsen"
        - if:
            condition:
              lambda: 'return x == "red";'
            then:
              - light.turn_on:
                  id: rgb_led
                  red: 100%
                  green: 0%
                  blue: 0%
                  brightness: 100%
                  effect: "Langzaam pulsen"

globals:
  - id: current_page
    type: int
    restore_value: false
    initial_value: "0"
  - id: auto_rotate
    type: bool
    restore_value: false
    initial_value: "true"
  - id: temp1_val
    type: float
    restore_value: false
    initial_value: "-99"
  - id: temp2_val
    type: float
    restore_value: false
    initial_value: "-99"
  - id: boot_ticks
    type: int
    restore_value: false
    initial_value: "0"
  - id: overall_status_str
    type: std::string
    restore_value: false
    initial_value: '"green"'

spi:
  clk_pin: GPIO40
  mosi_pin: GPIO45

interval:
  - interval: 6s
    then:
      - if:
          condition:
            lambda: 'return id(auto_rotate);'
          then:
            - lambda: |-
                id(current_page) = (id(current_page) + 1) % 4;

display:
  - platform: ili9xxx
    model: ST7789
    cs_pin: GPIO42
    dc_pin: GPIO41
    reset_pin: GPIO39
    rotation: 90°
    dimensions:
      width: 320
      height: 172
    invert_colors: true
    update_interval: 100ms
    lambda: |-

      // ── Kleurenpalet ──────────────────────────────────────
      auto BLACK      = Color(0,   0,   0);
      auto WHITE      = Color(255, 255, 255);
      auto GREEN      = Color(0,   230, 118);
      auto ORANGE     = Color(255, 160, 0);
      auto RED        = Color(255, 60,  60);
      auto CYAN       = Color(0,   220, 255);
      auto TEAL       = Color(0,   180, 160);
      auto GOLD       = Color(255, 200, 50);
      auto DIM        = Color(70,  70,  70);
      auto DARKBG     = Color(4,   8,   20);
      auto PANEL      = Color(12,  20,  45);
      auto PANELBRD   = Color(0,   70,  110);
      auto ACCENT     = Color(0,   150, 200);
      auto ACCENTDIM  = Color(0,   50,  80);

      // ── Boot scherm (eerste 3 seconden) ──────────────────
      if (id(boot_ticks) < 30) {{
        id(boot_ticks) += 1;
        // Gradient achtergrond
        for (int y = 0; y < 172; y++) {{
          int b = 18 + (y * 55) / 172;
          int g = (y * 10) / 172;
          it.horizontal_line(0, y, 320, Color(0, g, b));
        }}
        // Decoratieve lijnen
        it.horizontal_line(0,  52, 320, Color(0, 70, 110));
        it.horizontal_line(0,  54, 320, Color(0, 30, 50));
        it.horizontal_line(0, 118, 320, Color(0, 70, 110));
        it.horizontal_line(0, 116, 320, Color(0, 30, 50));

        // Logo
        it.print(160, 58, id(font_logo), TextAlign::TOP_CENTER, WHITE, "AMANAH");
        it.print(160, 98, id(font_medium), TextAlign::TOP_CENTER, TEAL, "Aquarium Monitor");
        it.print(160, 122, id(font_tiny), TextAlign::TOP_CENTER, DIM, "v1.0  ·  ESPHome  ·  ESP32-S3");

        // Progress bar
        int prog = (id(boot_ticks) * 320) / 30;
        it.filled_rectangle(0, 158, 320, 5, Color(0, 25, 45));
        it.filled_rectangle(0, 158, prog, 5, CYAN);
        it.print(160, 165, id(font_tiny), TextAlign::TOP_CENTER, Color(0, 90, 120), "Initialiseren...");
        return;
      }}

      // ── Screensaver: geen WiFi ────────────────────────────
      if (!id(wifi_connected).state) {{
        it.fill(DARKBG);
        int pulse = id(boot_ticks) % 60;
        int r = (pulse < 30) ? (pulse * 4) : ((60 - pulse) * 4);
        it.filled_circle(160, 86, 44, Color(0, r/5, r));
        it.filled_circle(160, 86, 32, Color(0, r/4, r));
        it.filled_circle(160, 86, 20, Color(0, r/3, r));
        it.filled_circle(160, 86, 9,  CYAN);
        it.print(160, 138, id(font_small), TextAlign::TOP_CENTER, Color(0, 80, 110), "Verbinden met WiFi...");
        id(boot_ticks) += 1;
        return;
      }}
      id(boot_ticks) += 1;

      // ── Vaste header (alle paginas) ───────────────────────
      // Hoogte: 28px
      it.fill(DARKBG);
      it.filled_rectangle(0, 0, 320, 28, PANEL);
      it.horizontal_line(0, 28, 320, PANELBRD);

      // Links: logo
      it.print(8, 4, id(font_bold), CYAN, "AMANAH");

      // Midden: pagina naam
      const char* page_titles[] = {{"TEMPERATUUR", "STATUS", "NETWERK", "SYSTEEM"}};
      it.print(160, 6, id(font_tiny), TextAlign::TOP_CENTER, ACCENT, page_titles[id(current_page)]);

      // Rechts: WiFi signaal bars
      auto rssi = id(wifi_rssi).state;
      int bars = 0;
      if (rssi > -60) bars = 4;
      else if (rssi > -70) bars = 3;
      else if (rssi > -80) bars = 2;
      else if (rssi > -90) bars = 1;
      int bx = 289;
      for (int b = 0; b < 4; b++) {{
        Color bc = (b < bars) ? CYAN : ACCENTDIM;
        int bh = 4 + b * 3;
        it.filled_rectangle(bx + b*6, 20 - bh, 4, bh, bc);
      }}

      // Dot indicators
      int dot_x = 160 - 14;
      for (int i = 0; i < 4; i++) {{
        if (i == id(current_page)) it.filled_circle(dot_x + i*9, 24, 3, CYAN);
        else it.filled_circle(dot_x + i*9, 24, 2, ACCENTDIM);
      }}

      // ── PAGINA 0: Temperatuur — landscape 2 kolommen ─────
      if (id(current_page) == 0) {{

        // Linker kolom: Sensor 1
        it.print(12, 34, id(font_tiny), ACCENT, "SENSOR 1");
        it.vertical_line(160, 32, 140, PANELBRD);

        Color c1 = GREEN;
        if (id(temp1_val) < 23.0f || id(temp1_val) > 28.0f) c1 = ORANGE;
        if (id(temp1_val) < 20.0f || id(temp1_val) > 30.0f) c1 = RED;
        if (id(temp1_val) == -99.0f) {{
          it.print(12, 50, id(font_xlarge), DIM, "--.-");
          it.print(12, 108, id(font_small), DIM, "geen sensor");
        }} else {{
          it.printf(12, 48, id(font_xlarge), c1, "%.1f", id(temp1_val));
          it.print(118, 62, id(font_medium), DIM, "\xB0C");
          // Status blokje
          it.filled_rectangle(12, 110, 60, 16, Color(c1.r/6, c1.g/6, c1.b/6));
          it.rectangle(12, 110, 60, 16, c1);
          it.print(42, 112, id(font_tiny), TextAlign::TOP_CENTER, c1,
            (id(temp1_val) < 20.0f || id(temp1_val) > 30.0f) ? "KRITIEK" :
            (id(temp1_val) < 23.0f || id(temp1_val) > 28.0f) ? "LET OP" : "OK");
        }}

        // Rechter kolom: Sensor 2
        it.print(172, 34, id(font_tiny), ACCENT, "SENSOR 2");

        Color c2 = GREEN;
        if (id(temp2_val) < 23.0f || id(temp2_val) > 28.0f) c2 = ORANGE;
        if (id(temp2_val) < 20.0f || id(temp2_val) > 30.0f) c2 = RED;
        if (id(temp2_val) == -99.0f) {{
          it.print(172, 50, id(font_xlarge), DIM, "--.-");
          it.print(172, 108, id(font_small), DIM, "geen sensor");
        }} else {{
          it.printf(172, 48, id(font_xlarge), c2, "%.1f", id(temp2_val));
          it.print(278, 62, id(font_medium), DIM, "\xB0C");
          it.filled_rectangle(172, 110, 60, 16, Color(c2.r/6, c2.g/6, c2.b/6));
          it.rectangle(172, 110, 60, 16, c2);
          it.print(202, 112, id(font_tiny), TextAlign::TOP_CENTER, c2,
            (id(temp2_val) < 20.0f || id(temp2_val) > 30.0f) ? "KRITIEK" :
            (id(temp2_val) < 23.0f || id(temp2_val) > 28.0f) ? "LET OP" : "OK");
        }}

        // Delta onderaan
        it.horizontal_line(0, 132, 320, PANELBRD);
        if (id(temp1_val) != -99.0f && id(temp2_val) != -99.0f) {{
          float delta = id(temp1_val) - id(temp2_val);
          it.print(12, 138, id(font_tiny), DIM, "DELTA");
          it.printf(70, 134, id(font_medium), GOLD, "%+.2f \xB0C", delta);
        }}
        it.print(220, 138, id(font_tiny), DIM, "1-Wire  ·  GP4");

      // ── PAGINA 1: Status ──────────────────────────────────
      }} else if (id(current_page) == 1) {{

        Color sc = GREEN;
        const char* sl  = "ALLES OK";
        const char* sl2 = "Alle parameters zijn";
        const char* sl3 = "binnen de normale grenzen";
        if (id(overall_status_str) == "orange") {{
          sc = ORANGE; sl = "WAARSCHUWING";
          sl2 = "Een of meer parameters"; sl3 = "vereisen aandacht";
        }}
        if (id(overall_status_str) == "red") {{
          sc = RED; sl = "KRITIEK!";
          sl2 = "Directe actie vereist"; sl3 = "Controleer het aquarium";
        }}

        // Links: status ring
        it.circle(75, 100, 58, sc);
        it.circle(75, 100, 54, Color(sc.r/4, sc.g/4, sc.b/4));
        it.filled_circle(75, 100, 50, Color(sc.r/8, sc.g/8, sc.b/8));
        it.print(75, 88, id(font_bold), TextAlign::TOP_CENTER, sc, sl);

        // Rechts: details
        it.vertical_line(148, 32, 140, PANELBRD);
        it.print(158, 36, id(font_tiny), DIM, sl2);
        it.print(158, 52, id(font_tiny), DIM, sl3);
        it.horizontal_line(148, 72, 172, ACCENTDIM);

        // T1 en T2 mini
        it.print(158, 78, id(font_tiny), DIM, "TEMP 1");
        Color mc1 = GREEN;
        if (id(temp1_val) < 23.0f || id(temp1_val) > 28.0f) mc1 = ORANGE;
        if (id(temp1_val) != -99.0f)
          it.printf(158, 92, id(font_large), mc1, "%.1f\xB0", id(temp1_val));
        else it.print(158, 92, id(font_large), DIM, "--\xB0");

        it.print(245, 78, id(font_tiny), DIM, "TEMP 2");
        Color mc2 = GREEN;
        if (id(temp2_val) < 23.0f || id(temp2_val) > 28.0f) mc2 = ORANGE;
        if (id(temp2_val) != -99.0f)
          it.printf(245, 92, id(font_large), mc2, "%.1f\xB0", id(temp2_val));
        else it.print(245, 92, id(font_large), DIM, "--\xB0");

      // ── PAGINA 2: Netwerk ─────────────────────────────────
      }} else if (id(current_page) == 2) {{

        // Linker blok: netwerk
        it.print(12, 34, id(font_tiny), ACCENT, "NETWERK");
        it.print(12, 48, id(font_tiny), DIM, "SSID");
        it.print(12, 62, id(font_medium), WHITE, id(wifi_ssid).c_str());

        it.horizontal_line(8, 90, 148, ACCENTDIM);
        it.print(12, 96, id(font_tiny), DIM, "IP ADRES");
        it.print(12, 110, id(font_medium), CYAN, id(wifi_ip).c_str());

        it.horizontal_line(8, 136, 148, ACCENTDIM);
        it.print(12, 140, id(font_tiny), DIM, "MQTT BROKER");
        it.print(12, 154, id(font_small), TEAL, "${mqtt_broker}");

        // Rechter blok: signaal
        it.vertical_line(164, 32, 140, PANELBRD);
        it.print(174, 34, id(font_tiny), ACCENT, "SIGNAALSTERKTE");

        Color rssi_color = GREEN;
        const char* rssi_label = "Uitstekend";
        if (rssi < -60) {{ rssi_color = TEAL;   rssi_label = "Goed"; }}
        if (rssi < -70) {{ rssi_color = ORANGE; rssi_label = "Matig"; }}
        if (rssi < -80) {{ rssi_color = RED;    rssi_label = "Zwak"; }}

        it.printf(174, 50, id(font_large), rssi_color, "%d", (int)rssi);
        it.print(242, 62, id(font_tiny), DIM, "dBm");
        it.print(260, 56, id(font_medium), rssi_color, rssi_label);

        // Grafische bars
        it.horizontal_line(170, 130, 120, ACCENTDIM);
        for (int b = 0; b < 4; b++) {{
          Color bc = (b < bars) ? CYAN : ACCENTDIM;
          int bh = 14 + b * 12;
          it.filled_rectangle(176 + b * 26, 130 - bh, 18, bh, bc);
        }}

      // ── PAGINA 3: Systeem ─────────────────────────────────
      }} else if (id(current_page) == 3) {{

        // Links: uptime en firmware
        it.print(12, 34, id(font_tiny), ACCENT, "UPTIME");
        auto uptime_s = (uint32_t) id(sys_uptime).state;
        uint32_t h = uptime_s / 3600;
        uint32_t m = (uptime_s % 3600) / 60;
        uint32_t s = uptime_s % 60;
        it.printf(12, 50, id(font_large), WHITE, "%02d:%02d", h, m);
        it.printf(110, 62, id(font_small), DIM, ":%02d", s);

        it.horizontal_line(8, 98, 148, ACCENTDIM);
        it.print(12, 104, id(font_tiny), DIM, "FIRMWARE");
        it.print(12, 118, id(font_small), TEAL, "Amanah v1.0");
        it.print(12, 134, id(font_tiny), DIM, "ESPHome  ·  ESP32-S3");
        it.print(12, 148, id(font_tiny), DIM, "Waveshare S3-LCD-1.47B");

        // Rechts: auto-rotate + pagina info
        it.vertical_line(164, 32, 140, PANELBRD);
        it.print(174, 34, id(font_tiny), ACCENT, "INSTELLINGEN");
        it.print(174, 50, id(font_tiny), DIM, "PAGINAWISSEL");
        if (id(auto_rotate)) {{
          it.print(174, 64, id(font_medium), CYAN, "Automatisch");
          it.print(174, 84, id(font_tiny), DIM, "Elke 6 seconden");
        }} else {{
          it.print(174, 64, id(font_medium), DIM, "Handmatig");
          it.print(174, 84, id(font_tiny), DIM, "Druk: volgende pagina");
        }}

        it.horizontal_line(170, 106, 148, ACCENTDIM);
        it.print(174, 112, id(font_tiny), DIM, "DISPLAY");
        it.print(174, 126, id(font_tiny), DIM, "320x172  ST7789  IPS  90\xB0");
        it.print(174, 142, id(font_tiny), DIM, "Helderheid via Home Assistant");
      }}

      // ── Footer ────────────────────────────────────────────
      it.horizontal_line(0, 162, 320, PANELBRD);
      it.filled_rectangle(0, 163, 320, 9, PANEL);
      if (id(auto_rotate)) {{
        it.print(6, 164, id(font_tiny), CYAN, "\xBB AUTO");
      }} else {{
        it.print(6, 164, id(font_tiny), DIM, "\xBB HANDMATIG");
      }}
      it.printf(284, 164, id(font_tiny), ACCENTDIM, "%d/4", id(current_page) + 1);

font:
  - file: "gfonts://Orbitron"
    id: font_logo
    size: 28
  - file: "gfonts://Orbitron"
    id: font_bold
    size: 16
  - file: "gfonts://Share Tech Mono"
    id: font_large
    size: 42
  - file: "gfonts://Share Tech Mono"
    id: font_xlarge
    size: 52
  - file: "gfonts://Share Tech Mono"
    id: font_medium
    size: 18
  - file: "gfonts://Share Tech Mono"
    id: font_small
    size: 13
  - file: "gfonts://Share Tech Mono"
    id: font_tiny
    size: 10


output:
  - platform: ledc
    pin: GPIO48
    id: backlight_pwm

light:
  - platform: monochromatic
    output: backlight_pwm
    name: "Amanah Display Helderheid"
    id: backlight
    restore_mode: RESTORE_DEFAULT_ON
    icon: mdi:brightness-6

  # Onboard RGB LED (WS2812, GPIO38) — toont aquarium status kleur
  - platform: neopixelbus
    type: GRB
    variant: WS2812
    pin: GPIO38
    num_leds: 1
    name: "Amanah Status LED"
    id: rgb_led
    restore_mode: ALWAYS_ON
    effects:
      - pulse:
          name: "Langzaam pulsen"
          transition_length: 2s
          update_interval: 2s

binary_sensor:
  - platform: gpio
    pin:
      number: GPIO0
      inverted: true
      mode:
        input: true
        pullup: true
    name: "Amanah Pagina Knop"
    id: page_button
    filters:
      - delayed_on: 50ms
    on_press:
      then:
        - lambda: |-
            id(current_page) = (id(current_page) + 1) % 4;
    on_multi_click:
      - timing:
          - ON for at least 1s
        then:
          - lambda: |-
              id(auto_rotate) = !id(auto_rotate);

  - platform: status
    name: "Amanah WiFi Status"
    id: wifi_connected

wifi_info:
  ssid:
    id: wifi_ssid
    name: "Amanah WiFi SSID"
    update_interval: 60s
  ip_address:
    id: wifi_ip
    name: "Amanah IP Adres"
    update_interval: 60s

sensor:
  - platform: wifi_signal
    name: "Amanah WiFi Signaal"
    id: wifi_rssi
    update_interval: 10s

  - platform: uptime
    name: "Amanah Uptime"
    id: sys_uptime
    update_interval: 6s

# ============================================================
# 1-Wire bus — alle DS18B20 temperatuursensoren op één draad
# Sluit alle DS18B20's parallel aan op GP4 + 4.7kΩ pull-up
# naar 3V3. Voeg extra sensors toe door address te kopiëren.
# Adres achterhalen: flash zonder address, lees seriele log.
# ============================================================
one_wire:
  - platform: gpio
    pin: ${sensor_pin}

# ============================================================
# SENSOR CONFIGURATIE
# GP4  = 1-Wire bus (alle DS18B20 temperatuursensoren)
# GP5  = pH (ADC)     GP8 = Waterflow (pulse)
# GP9  = Waterstand   GP10 = Lekdetectie
# GP2/GP3 = I2C (SDA/SCL)   GP6 = Pomp   GP7 = Buzzer
# ============================================================

sensor:

  # Temperatuur 1 (1-Wire, GP4)
  # Eerste flash: geen address nodig, log toont alle adressen
  - platform: dallas_temp
    name: "Amanah Temperatuur 1"
    id: temp_sensor
    # address: 0x0000000000000000  # invullen na eerste flash
    update_interval: 30s
    on_value:
      then:
        - globals.set:
            id: temp1_val
            value: !lambda "return x;"
        - mqtt.publish_json:
            topic: !lambda 'return (std::string)"{mqtt_base}/temperature_1";'
            payload: "root[\"value\"] = x;"

  # Temperatuur 2 (zelfde 1-Wire bus, tweede DS18B20)
  # - platform: dallas_temp
  #   name: "Amanah Temperatuur 2"
  #   address: 0x0000000000000000
  #   update_interval: 30s
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/temperature_2";'
  #           payload: "root[\"value\"] = x;"

  # Extra DS18B20 (kopieer dit blok per sensor, pas address + name aan)
  # - platform: dallas_temp
  #   name: "Amanah Temperatuur 3"
  #   address: 0x0000000000000000
  #   update_interval: 30s
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/temperature_3";'
  #           payload: "root[\"value\"] = x;"

  # pH sensor (GP5, analoog 0-3.3V)
  # - platform: adc
  #   pin: GPIO5
  #   name: "Amanah pH"
  #   unit_of_measurement: "pH"
  #   accuracy_decimals: 2
  #   update_interval: 10s
  #   attenuation: 11db
  #   filters:
  #     - lambda: 'return (x - 0.5) * 14.0 / 2.5;'  # kalibreer met pH 4 + 7 buffers
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/ph";'
  #           payload: "root[\"value\"] = x;"

  # Waterflow (GP8, pulse counter - bijv. YF-S201)
  # - platform: pulse_counter
  #   pin: GPIO8
  #   name: "Amanah Waterflow"
  #   unit_of_measurement: "L/min"
  #   update_interval: 6s
  #   filters:
  #     - multiply: 0.00416  # YF-S201: 450 pulsen/L -> L/min
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/flow";'
  #           payload: "root[\"value\"] = x;"

  # Waterstand (GP9, ADC)
  # - platform: adc
  #   pin: GPIO9
  #   name: "Amanah Waterstand"
  #   unit_of_measurement: "%"
  #   update_interval: 30s
  #   attenuation: 11db
  #   filters:
  #     - lambda: 'return (x / 3.3) * 100.0;'
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/level";'
  #           payload: "root[\"value\"] = x;"

  # Lekdetectie (GP10, ADC)
  # - platform: adc
  #   pin: GPIO10
  #   name: "Amanah Lekdetectie"
  #   unit_of_measurement: "%"
  #   update_interval: 6s
  #   attenuation: 11db
  #   filters:
  #     - lambda: 'return (x / 3.3) * 100.0;'
  #   on_value:
  #     then:
  #       - mqtt.publish_json:
  #           topic: !lambda 'return (std::string)"{mqtt_base}/leak";'
  #           payload: "root[\"value\"] = x;"

# I2C bus (GP2=SDA, GP3=SCL) - voor TCS kleurensensor, BME280, etc.
# Voeg toe boven sensor::
# i2c:
#   sda: GPIO2
#   scl: GPIO3
#   scan: true

# Pomp relay (GP6)
# switch:
#   - platform: gpio
#     pin: GPIO6
#     name: "Amanah Pomp"
#     id: pump_relay

# Buzzer / alarm (GP7)
# output:
#   - platform: ledc
#     pin: GPIO7
#     id: buzzer_out
#     frequency: 1000Hz
# rtttl:
#   output: buzzer_out
"""


async def check_esphome_addon(hass: HomeAssistant) -> bool:
    """
    Controleer of de ESPHome add-on aanwezig is.

    Strategie 1: Check of /config/esphome/ map bestaat (meest betrouwbaar).
    Strategie 2: Supervisor API als SUPERVISOR_TOKEN beschikbaar is (alleen in add-ons).
    Custom components hebben geen SUPERVISOR_TOKEN — strategie 1 is de primaire check.
    """
    import os

    # Primaire check: bestaat de ESPHome config map al?
    esphome_dir = hass.config.path("esphome")
    if os.path.isdir(esphome_dir):
        _LOGGER.debug("ESPHome map gevonden: %s", esphome_dir)
        return True

    # Secundaire check: Supervisor API (werkt alleen vanuit add-on context)
    token = os.environ.get("SUPERVISOR_TOKEN", "")
    if not token:
        _LOGGER.debug("Geen SUPERVISOR_TOKEN — waarschijnlijk niet in HA add-on context")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            for slug in [ESPHOME_ADDON_SLUG, ESPHOME_ADDON_ALT]:
                url = f"{SUPERVISOR_API}/addons/{slug}/info"
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        state = data.get("data", {}).get("state", "")
                        _LOGGER.debug("ESPHome add-on gevonden: slug=%s state=%s", slug, state)
                        return state == "started"
    except Exception as err:
        _LOGGER.debug("Supervisor API niet bereikbaar: %s", err)

    return False


async def create_esphome_device(
    hass: HomeAssistant,
    mqtt_broker: str,
    mqtt_base: str,
    sensor_pin: str = "GPIO4",
) -> tuple[bool, str]:
    """
    Maak een nieuw ESPHome device aan door de YAML direct naar /config/esphome/ te schrijven.

    Custom components draaien als onderdeel van HA core en hebben directe toegang
    tot het bestandssysteem — geen Supervisor API nodig voor het schrijven van bestanden.

    Returns: (succes: bool, bericht: str)
    """
    import os
    import asyncio

    yaml_content = ESPHOME_YAML_TEMPLATE.format(
        mqtt_broker=mqtt_broker,
        mqtt_base=mqtt_base,
        sensor_pin=sensor_pin,
    )

    filename = "amanah-display.yaml"
    # Pad relatief aan de HA config directory
    esphome_dir = hass.config.path("esphome")
    filepath = os.path.join(esphome_dir, filename)

    try:
        # Maak de esphome map aan als die nog niet bestaat
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: os.makedirs(esphome_dir, exist_ok=True)
        )

        # Schrijf de YAML — overschrijf niet als bestand al bestaat
        if os.path.exists(filepath):
            _LOGGER.info("ESPHome YAML bestaat al: %s — niet overschreven", filepath)
            return True, filename

        def _write():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(yaml_content)

        await asyncio.get_event_loop().run_in_executor(None, _write)
        _LOGGER.info("Amanah ESPHome YAML geschreven naar: %s", filepath)
        return True, filename

    except PermissionError:
        msg = f"Geen schrijfrechten voor {esphome_dir}"
        _LOGGER.error(msg)
        return False, msg
    except Exception as err:
        _LOGGER.error("Fout bij aanmaken ESPHome device: %s", err)
        return False, str(err)

async def trigger_esphome_install(hass: HomeAssistant, device_name: str = "amanah-display") -> bool:
    """
    Trigger een OTA install van het ESPHome device via de ESPHome add-on REST API.
    Werkt alleen als het device al eerder via WiFi is geconfigureerd (ESPHome API actief).

    Returns: True als de install-opdracht succesvol is verstuurd.
    """
    import os
    import aiohttp

    token = os.environ.get("SUPERVISOR_TOKEN", "")
    if not token:
        _LOGGER.warning("Geen Supervisor token — ESPHome install overgeslagen")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # ESPHome add-on interne API: compile + install
            url = "http://supervisor/addons/a0d7b954_esphome/api/compile"
            payload = {"configuration": f"{device_name}.yaml"}

            async with session.post(
                url, json=payload, headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    _LOGGER.info("ESPHome compile gestart voor %s", device_name)
                    return True
                else:
                    body = await resp.text()
                    _LOGGER.warning("ESPHome install trigger mislukt: %s %s", resp.status, body)
                    return False

    except Exception as err:
        _LOGGER.warning("ESPHome install trigger fout: %s", err)
        return False
