# Lights App Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

This integration allows you to control Bluetooth Low Energy (BLE) light strings typically managed via the mobile "Lights App". This version is specifically optimized for stability, non-blocking startup, and a modern Home Assistant user experience.

## 🌟 Key Features

* **Light Entities instead of Switches:** All operational modes (Wave, Phasing, etc.) are created as native `light` entities. This allows for clean dashboard integration using light cards, groups, and native brightness sliders.
* **Non-Blocking Startup:** Home Assistant's boot process is never delayed. The connection to the hardware is established asynchronously in the background.
* **Self-Healing Engine:** Features a built-in **Watchdog Timer** that checks the connection status every 5 minutes and automatically triggers a reconnect if the device is offline.
* **Stability Optimized:** Uses the `bleak-retry-connector`, disables fragile service caching, and aggressively cleans up "zombie connections" to preserve your system's Bluetooth slots.
* **RSSI Monitoring:** Monitors signal strength and provides helpful debug information in the logs.

## 🛠 Installation

### Manual Installation
1. Download this repository.
2. Copy the `custom_components/lights_app` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

### Configuration
1. Navigate to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **Lights App**.
3. Enter the MAC address of your Bluetooth device.

## 💡 Supported Functions

* **Main Light:** Turn On/Off & Brightness control.
* **Effect Modes:** Each mode can be toggled as an individual light:
    * Stay on
    * Fast twinkling
    * Fade away
    * Twinkling in phase
    * Fade away in phase
    * Phasing
    * Wave



## ⚠️ Troubleshooting & Performance

### Signal Strength (RSSI)
Bluetooth Low Energy is sensitive to interference. For reliable operation, the RSSI value should be better than **-75 dBm**.
* **Tip:** USB 3.0 ports often cause significant interference. Use a **USB extension cable** for your Bluetooth dongle to drastically improve reception.
* **Tip:** If you experience range issues, using an **ESP32 Bluetooth Proxy** (via ESPHome) is highly recommended.



### Debug Logging
If you encounter connection issues, enable debug logging in your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.lights_app: debug


