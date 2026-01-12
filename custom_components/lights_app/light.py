from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode
from .entities import LightsAppLightEntity
from .const import DOMAIN
from .utils import (
    convert_device_brightness_to_ha,
    convert_ha_brightness_to_device,
    getBrightnessCommand,
    getTurnOnCommand,
    getTurnOffCommand,
    getModeCommand,
    sendCommand,
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    entities = [LightsAppTurnOnOff(hass, config_entry, entry_data)]
    
    modes = [
        ("Stay on", "stay_on"), ("Fast twinkling", "fast_twinkling"),
        ("Fade away", "fade_away"), ("Twinkling in phase", "twinkling_in_phase"),
        ("Fade away in phase", "fade_away_in_phase"), ("Phasing", "phasing"), ("Wave", "wave")
    ]
    
    for name, mode_id in modes:
        entities.append(LightsAppModeLight(hass, config_entry, entry_data, name, mode_id))
    
    for entity in entities:
        entry_data["entities"].append(entity)
        
    async_add_entities(entities)

class LightsAppTurnOnOff(LightsAppLightEntity):
    def __init__(self, hass, config_entry, entryData):
        super().__init__(hass, config_entry, entryData, "Light")
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def is_on(self):
        return self._entryData.get("state")

    @property
    def brightness(self):
        val = self._entryData.get("brightness")
        return convert_device_brightness_to_ha(val) if val else None

    async def async_turn_on(self, **kwargs):
        if ATTR_BRIGHTNESS in kwargs:
            br = convert_ha_brightness_to_device(kwargs[ATTR_BRIGHTNESS])
            await sendCommand(self._entryData, self._client, self._service, getBrightnessCommand(br))
        await sendCommand(self._entryData, self._client, self._service, getTurnOnCommand())

    async def async_turn_off(self, **kwargs):
        await sendCommand(self._entryData, self._client, self._service, getTurnOffCommand())

class LightsAppModeLight(LightsAppLightEntity):
    def __init__(self, hass, config_entry, entryData, name, mode_id):
        self._mode_id = mode_id
        super().__init__(hass, config_entry, entryData, name)
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF

    @property
    def is_on(self):
        modes = self._entryData.get("mode")
        return modes.get(self._mode_id, False) if isinstance(modes, dict) else False

    async def async_turn_on(self, **kwargs):
        if not isinstance(self._entryData.get("mode"), dict): self._entryData["mode"] = {}
        self._entryData["mode"][self._mode_id] = True
        await sendCommand(self._entryData, self._client, self._service, getModeCommand(self._entryData["mode"]))

    async def async_turn_off(self, **kwargs):
        if isinstance(self._entryData.get("mode"), dict):
            self._entryData["mode"][self._mode_id] = False
            await sendCommand(self._entryData, self._client, self._service, getModeCommand(self._entryData["mode"]))
