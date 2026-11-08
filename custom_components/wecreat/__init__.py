"""WeCreat local status integration."""
from datetime import timedelta
import logging

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import StatusError, read_status

DOMAIN = "wecreat"
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    session = async_get_clientsession(hass)

    async def update_status():
        try:
            return await read_status(session, entry.data[CONF_HOST], entry.data[CONF_PORT])
        except StatusError as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass, logging.getLogger(__name__), name=DOMAIN, config_entry=entry,
        update_method=update_status, update_interval=timedelta(seconds=5),
        always_update=False,
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
