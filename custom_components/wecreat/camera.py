"""On-demand WeCreat bed photographs."""
from homeassistant.components.camera import Camera
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from . import DOMAIN
from .api import read_photo, PhotoError


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BedCamera(entry, async_get_clientsession(hass))])


class BedCamera(Camera):
    _attr_has_entity_name = True
    _attr_translation_key = "bed_camera"
    _attr_should_poll = False

    def __init__(self, entry, session):
        super().__init__()
        self._session = session
        self._host = entry.data[CONF_HOST]
        self._port = entry.data[CONF_PORT]
        self._attr_unique_id = f"{entry.entry_id}_bed_camera"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    async def async_camera_image(self, width=None, height=None):
        try:
            return await read_photo(self._session, self._host, self._port)
        except PhotoError as err:
            raise HomeAssistantError(str(err)) from err
