import asyncio
from bleak import BleakClient, BleakGATTServiceCollection
from .const import WRITE_CHARACTERISTIC, LOGGER, NOTIFY_CHARACTERISTIC

def getTurnOnCommand(): return bytearray.fromhex("01 01 01 01")
def getTurnOffCommand(): return bytearray.fromhex("01 01 01 00")
def getLightStateCommand(): return bytearray.fromhex("00 00 03 11 26 11")
def getModeStateCommand(): return bytearray.fromhex("02 00 00")

def getWriteCharacteristic(service):
    if service is None: return None
    try: return service.get_characteristic(WRITE_CHARACTERISTIC)
    except: return None

def getNotifyCharacteristic(service):
    if service is None: return None
    try: return service.get_characteristic(NOTIFY_CHARACTERISTIC)
    except: return None

def getBrightnessCommand(brightness):
    clamped = max(10, min(99, brightness))
    return bytearray.fromhex(f"03 01 01 {clamped:02x}")

def getModeCommand(mode):
    hex_string = transformModeToHex(mode).hex()
    return bytearray.fromhex("05 01 02 03 " + hex_string)

def transformModeToHex(currentMode):
    binaryStr = ""
    keys = ["stay_on", "fast_twinkling", "fade_away", "twinkling_in_phase", 
            "fade_away_in_phase", "phasing", "wave"]
    for key in keys:
        binaryStr += "1" if currentMode.get(key, False) else "0"
    binaryStr += "0" 
    return bytearray([int(binaryStr, 2)])

def transformModeFromHex(hexByte):
    binary = bin(hexByte)[2:].zfill(8)
    return {
        "stay_on": binary[0] == "1",
        "fast_twinkling": binary[1] == "1",
        "fade_away": binary[2] == "1",
        "twinkling_in_phase": binary[3] == "1",
        "fade_away_in_phase": binary[4] == "1",
        "phasing": binary[5] == "1",
        "wave": binary[6] == "1",
    }

def convert_device_brightness_to_ha(b): return round((max(10, min(99, b)) - 10) / 89 * 255)
def convert_ha_brightness_to_device(b): return round(max(0, min(255, b)) / 255 * 89) + 10

async def sendCommand(entryData, client, service, command):
    if client is None or not client.is_connected:
        return
    try:
        char = getWriteCharacteristic(service)
        if char:
            async with asyncio.timeout(5.0):
                await client.write_gatt_char(char, command, True)
    except Exception as err:
        LOGGER.debug(f"Command failed: {err}")

def disconnect_handler(entryData):
    def handle(client):
        LOGGER.warning("Bluetooth connection lost for %s", entryData.get("address"))
        entryData["connection"]["connected"] = False
        entryData["connection"]["client"] = None
        entryData["connection"]["service"] = None
        for e in entryData.get("entities", []):
            if e.hass: e.async_write_ha_state()
    return handle

def notification_handler(entryData):
    async def handler(characteristic, data):
        if b"\x00\x00\x02" in data and len(data) == 5:
            entryData["state"] = (data[3] == 0x01)
        if data.startswith(b"\x02\x00") and len(data) == 18:
            entryData["mode"] = transformModeFromHex(data[-1])
            entryData["brightness"] = data[3]
        for e in entryData.get("entities", []):
            if e.hass: e.async_write_ha_state()
    return handler
