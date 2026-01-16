import asyncio
from datetime import timedelta
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SERVICE, LOGGER
from .utils import (
    notification_handler,
    getNotifyCharacteristic,
    sendCommand,
    getLightStateCommand,
    disconnect_handler,
    getModeStateCommand,
)

async def setupConnection(hass: HomeAssistant, address: str, config_entry: ConfigEntry):
    entry_id = config_entry.entry_id
    if entry_id not in hass.data[DOMAIN]:
        return

    data = hass.data[DOMAIN][entry_id]
    conn_state = data["connection"]

    if conn_state["connecting"]:
        return

    try:
        conn_state["connecting"] = True
        
    
        if conn_state.get("client"):
            LOGGER.debug("Bereinige alten Client vor Neuverbindung...")
            try:
                await conn_state["client"].disconnect()
            except Exception:
                pass
            conn_state["client"] = None

        LOGGER.debug("Hintergrund-Verbindung zu %s (Neu-Initialisierung)", address)
        
        async with asyncio.timeout(15.0):
            ble_device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)

        if ble_device:
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                name=address,
                disconnected_callback=disconnect_handler(data),
                use_services_cache=False, 
                max_attempts=2,
            )
            
            data["connection"]["client"] = client
            service = client.services.get_service(SERVICE)
            data["connection"]["service"] = service
            data["connection"]["connected"] = True

            if service:
                notify_char = getNotifyCharacteristic(service)
                if notify_char:
                    await client.start_notify(notify_char, notification_handler(data))

                await sendCommand(data, client, service, getLightStateCommand())
                await sendCommand(data, client, service, getModeStateCommand())

            rssi_value = getattr(ble_device, "rssi", "unbekannt")
            LOGGER.info("Erfolgreich verbunden mit %s (RSSI: %s)", address, rssi_value)
        else:
            LOGGER.debug("Gerät %s nicht gefunden", address)
            
    except Exception as err:
        LOGGER.error("Verbindungsfehler für %s: %s", address, err)
        data["connection"]["connected"] = False
    finally:
        conn_state["connecting"] = False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup der Integration ohne Blockieren des Startvorgangs."""
    address = entry.data.get(CONF_ADDRESS)
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "address": address,
        "entities": [],
        "state": None,
        "mode": {},
        "brightness": None,
        "connection": {"connected": False, "connecting": False, "client": None, "service": None},
    }

    hass.async_create_task(setupConnection(hass, address, entry))

    async def async_update_data():
        """Regelmäßiges Update über den Coordinator."""
        data = hass.data[DOMAIN][entry.entry_id]
        if not data["connection"]["connected"]:
            hass.async_create_task(setupConnection(hass, address, entry))
            return
        
        client = data["connection"]["client"]
        if client and client.is_connected:
            await sendCommand(data, client, data["connection"]["service"], getLightStateCommand())

    coordinator = DataUpdateCoordinator(
        hass, LOGGER, name=f"Lights App {address}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5)
    )
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["light", "switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Sauberes Entladen der Integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["light", "switch"])
    if unload_ok:
        data = hass.data[DOMAIN].get(entry.entry_id)
        if data and data["connection"].get("client"):
            try:
                await data["connection"]["client"].disconnect()
            except Exception:
                pass
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
