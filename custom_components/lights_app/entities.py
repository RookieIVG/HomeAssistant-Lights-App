from homeassistant.util import slugify
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.const import CONF_ADDRESS
from homeassistant.components.light import LightEntity, ColorMode
from .const import DOMAIN

class LightsAppEntity(Entity):
    def __init__(self, hass, config_entry, entryData, name_suffix):
        self._hass = hass
        self._address = config_entry.data.get(CONF_ADDRESS)
        self._entryData = entryData
        self._config_entry = config_entry
        self._name = "Lights App"
        self._name_suffix = name_suffix
        super().__init__()

    @property
    def _client(self):
        return self._hass.data[DOMAIN][self._config_entry.entry_id]["connection"].get("client")

    @property
    def _service(self):
        return self._hass.data[DOMAIN][self._config_entry.entry_id]["connection"].get("service")

    @property
    def available(self) -> bool:
        client = self._client
        return client is not None and client.is_connected

    @property
    def name(self) -> str:
        return f"{self._name} {self._name_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, slugify(f"{self._address}_lights_app"))},
            connections={("bluetooth", self._address)},
            name=self._name,
            manufacturer="Lights App",
        )

    @property
    def unique_id(self) -> str:
        id_suffix = "".join(self._name_suffix.split()).lower()
        return f"{self._address}-{self._name}-{id_suffix}".lower()

class LightsAppLightEntity(LightEntity, LightsAppEntity):
    def __init__(self, hass, config_entry, entryData, name_suffix):
        LightsAppEntity.__init__(self, hass, config_entry, entryData, name_suffix)
