# Lights App Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![Maintainer](https://img.shields.io/badge/maintainer-YourName-blue.svg)

Diese Integration ermöglicht die Steuerung von Bluetooth-Lichterketten (BLE), die normalerweise über die mobile "Lights App" gesteuert werden. Diese Version ist speziell auf Stabilität und eine moderne Home Assistant Nutzererfahrung optimiert.

## 🌟 Besonderheiten dieser Version

* **Licht-Entitäten statt Schalter:** Alle Modi (Wave, Phasing, etc.) werden als echte `light`-Entitäten angelegt. Das ermöglicht die Nutzung von Licht-Karten, Gruppen und nativen Helligkeitsreglern im Dashboard.
* **Non-Blocking Startup:** Der Start von Home Assistant wird nicht verzögert. Die Verbindung zur Hardware wird asynchron im Hintergrund aufgebaut.
* **Stabilitäts-Engine:** Nutzt den `bleak-retry-connector`, deaktiviert fehleranfälliges Caching und bereinigt "Zombie-Verbindungen", um die Bluetooth-Slots deines Systems zu schonen.
* **RSSI Monitoring:** Überwacht die Signalstärke und gibt hilfreiche Debug-Informationen bei Verbindungsstörungen aus.

## 🛠 Installation

### Manuell
1. Lade dieses Repository herunter.
2. Kopiere den Ordner `custom_components/lights_app` in dein Home Assistant `custom_components` Verzeichnis.
3. Starte Home Assistant neu.

### Einrichtung
1. Gehe zu **Einstellungen > Geräte & Dienste**.
2. Klicke auf **Integration hinzufügen** und suche nach **Lights App**.
3. Gib die MAC-Adresse deines Bluetooth-Geräts ein.

## 💡 Unterstützte Funktionen

* **Hauptlicht:** An/Aus & Helligkeit.
* **Effekt-Modi:** Jeder Modus kann als eigenes Licht aktiviert werden:
    * Stay on
    * Fast twinkling
    * Fade away
    * Twinkling in phase
    * Fade away in phase
    * Phasing
    * Wave



## ⚠️ Fehlerbehebung & Performance

### Signalstärke (RSSI)
Bluetooth Low Energy ist anfällig für Störungen. Für einen reibungslosen Betrieb sollte der RSSI-Wert besser als **-75 dBm** sein.
* **Tipp:** USB 3.0 Ports verursachen oft Interferenzen. Nutze ein **USB-Verlängerungskabel** für deinen Bluetooth-Dongle, um den Empfang drastisch zu verbessern.
* **Tipp:** Bei Reichweitenproblemen wird ein **ESP32 Bluetooth Proxy** empfohlen.



### Debug-Logging
Wenn du Probleme mit der Verbindung hast, aktiviere das Debug-Logging in deiner `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.lights_app: debug

