"""Config flow to configure Philips Hue."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import callback

from . import DOMAIN

DEFAULT_SCAN_INTERVAL = 2

# Data schemas
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCAN_INTERVAL, default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0)),
    },
    extra=vol.ALLOW_EXTRA,
)


_LOGGER = logging.getLogger(__name__)


class HueServiceFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Hue config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get option flow."""
        return HueServiceOptionsFlowHandler(config_entry)

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            await self.async_set_unique_id("hue_service_advanced")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Hue Service advanced", data=user_input)

        return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)


class HueServiceOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry
        self.scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        OPTIONS_SCHEMA = vol.Schema(
            {vol.Required(CONF_SCAN_INTERVAL, default=self.scan_interval): vol.All(vol.Coerce(float), vol.Range(min=0))}
        )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="user", data_schema=OPTIONS_SCHEMA)
