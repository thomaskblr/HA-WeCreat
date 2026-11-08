"""Configure a networked WeCreat laser."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import DOMAIN
from .api import StatusError, normalize_host, read_status


class WeCreatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._configure("user", user_input, {})

    async def async_step_reconfigure(self, user_input=None):
        return await self._configure("reconfigure", user_input, self._get_reconfigure_entry().data)

    async def _configure(self, step, user_input, defaults):
        errors = {}
        if user_input is not None:
            defaults = dict(user_input)
            try:
                host = normalize_host(user_input[CONF_HOST])
                port = user_input[CONF_PORT]
                await read_status(async_get_clientsession(self.hass), host, port)
            except ValueError:
                errors[CONF_HOST] = "invalid_host"
            except StatusError:
                errors["base"] = "cannot_connect"
            else:
                data = {CONF_HOST: host, CONF_PORT: port}
                current = self._get_reconfigure_entry() if step == "reconfigure" else None
                if any(e != current and dict(e.data) == data for e in self._async_current_entries()):
                    return self.async_abort(reason="already_configured")
                if current:
                    return self.async_update_reload_and_abort(current, data_updates=data,
                        title=f"WeCreat ({host})")
                return self.async_create_entry(title=f"WeCreat ({host})", data=data)
        schema = vol.Schema({
            vol.Required(CONF_HOST, description={"suggested_value": defaults.get(CONF_HOST, "")}): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, 8080)):
                vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        })
        return self.async_show_form(step_id=step, data_schema=schema, errors=errors)
