import asyncio
from datetime import timedelta
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.components import bluetooth
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, SERVICE, LOGGER
from .utils import (
    notification_handler,
    getNotifyCharacteristic,
    sendCommand,
    getLightStateCommand,
    disconnect_handler,
    getModeStateCommand,
)

async def setupConnection(hass: HomeAssistant, entry_id: str):
    if entry_id not in hass.data[DOMAIN]:
        return

    data = hass.data[DOMAIN][entry_id]
    address = data["address"]
    conn_state = data["connection"]

    if conn_state["connecting"]:
        return

    try:
        conn_state["connecting"] = True
        
        if conn_state.get("client"):
            LOGGER.debug("Cleaning up old client before reconnection...")
            try:
                await conn_state["client"].disconnect()
            except Exception:
                pass
            conn_state["client"] = None

        LOGGER.info("Connection attempt for %s (Watchdog)...", address)
        
        async with asyncio.timeout(20.0):
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

            rssi_value = getattr(ble_device, "rssi", "unknown")
            LOGGER.info("Successfully connected to %s (RSSI: %s)", address, rssi_value)
        else:
            LOGGER.warning("Device %s not found", address)
            
    except Exception as err:
        LOGGER.error("Connection error for %s: %s", address, err)
        data["connection"]["connected"] = False
    finally:
        conn_state["connecting"] = False

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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

    async def _check_connection(_=None):
        data = hass.data[DOMAIN][entry.entry_id]
        if not data["connection"]["connected"] and not data["connection"]["connecting"]:
            hass.async_create_task(setupConnection(hass, entry.entry_id))

    hass.async_create_task(setupConnection(hass, entry.entry_id))

    entry.async_on_unload(
        async_track_time_interval(hass, _check_connection, timedelta(minutes=5))
    )

    async def async_update_data():
        data = hass.data[DOMAIN][entry.entry_id]
        if data["connection"]["connected"]:
            client = data["connection"]["client"]
            if client and client.is_connected:
                await sendCommand(data, client, data["connection"]["service"], getLightStateCommand())
        return True

    coordinator = DataUpdateCoordinator(
        hass, LOGGER, name=f"Lights App {address}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=5)
    )
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["light", "switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
