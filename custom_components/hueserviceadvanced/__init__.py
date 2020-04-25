"""Support for the Philips Hue system."""
import logging
from datetime import timedelta

from typing import List
import voluptuous as vol

from homeassistant.components.hue.bridge import HueBridge
from homeassistant.const import ATTR_ENTITY_ID, CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv
from homeassistant.components.hue import DOMAIN as HUE_DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT

DOMAIN = "hueserviceadvanced"
SERVICE_HUE_CONFIG = "set_motion_sensor"
CURRENT_SENSORS = "{}_current_sensors"
SCAN_INTERVAL = timedelta(seconds=0.6)

ATTR_ON = "on"
ATTR_SENSITIVITY = "sensitivity"
ATTR_THOLDOFFSET = "tholdoffset"
ATTR_THOLDDARK = "tholddark"
ATTR_SUNRISEOFFSET = "sunriseoffset"
ATTR_SUNSETOFFSET = "sunsetoffset"
ATTR_LONG = "long"
ATTR_LAT = "lat"

OLD_SETS = {}

MOTION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.comp_entity_ids,
        vol.Optional(ATTR_ON): cv.boolean,
        vol.Optional(ATTR_SENSITIVITY): cv.positive_int,
        vol.Optional(ATTR_THOLDOFFSET): cv.positive_int,
        vol.Optional(ATTR_THOLDDARK): cv.positive_int,
        vol.Optional(ATTR_SUNRISEOFFSET): vol.All(
            vol.Coerce(int), vol.Range(min=-120, max=120)
        ),
        vol.Optional(ATTR_SUNSETOFFSET): vol.All(
            vol.Coerce(int), vol.Range(min=-120, max=120)
        ),
        vol.Optional(ATTR_LONG): cv.longitude,
        vol.Optional(ATTR_LAT): cv.latitude,
    }
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Load configuration for component."""
    hass.data.setdefault(DOMAIN, {})

    if hass.config_entries.async_entries(DOMAIN) or DOMAIN not in config:
        return True
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
        )
    )

    return True


async def async_setup_entry(hass, config_entry):
    """Set up the Hue service."""
    if not config_entry.options:
        hass.config_entries.async_update_entry(
            config_entry,
            options={
                "scan_interval": config_entry.data[CONF_SCAN_INTERVAL],
            },
        )

    await async_set_interval(hass, timedelta(seconds=config_entry.options[CONF_SCAN_INTERVAL]))

    async def hue_config_sensor(service):
        """Service to call  into bridge to set config."""
        entity_registry = await hass.helpers.entity_registry.async_get_registry()
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        entities = []
        for entity in entity_ids:
            unique_id = entity_registry.async_get(entity).unique_id
            if unique_id[0:4] == "SML_":
                unique_id = unique_id.replace("SML_", "") + "-0406"
            entities.append(unique_id)

        data_dict = {k: v for k, v in service.data.items() if ATTR_ENTITY_ID not in k}
        current_sensors = await async_get_motions(hass)
        for entry in current_sensors.values():
            if entry.uniqueid in entities:
                await entry.set_config(**data_dict)
        return True

    hass.services.async_register(
        DOMAIN, SERVICE_HUE_CONFIG, hue_config_sensor, schema=MOTION_SCHEMA
    )

    hass.data[DOMAIN]["unsub_listener"] = config_entry.add_update_listener(update_listener)

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await async_set_interval(hass)
    hass.services.async_remove(DOMAIN, SERVICE_HUE_CONFIG)
    hass.data[DOMAIN]["unsub_listener"]()
    return True


async def update_listener(hass, config_entry):
    """Reload device tracker if change option."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_set_interval(hass, scan_interval=None):
    """.Set update interval."""
    bridges = await async_get_bridges(hass)
    for bridge in bridges:
        if scan_interval is None and bridge in OLD_SETS:
            scan_interval = OLD_SETS.get(bridge)
        OLD_SETS.update({bridge: bridge.sensor_manager.coordinator.update_interval})
        _LOGGER.debug("Set update interval %s", scan_interval)
        bridge.sensor_manager.coordinator.update_interval = scan_interval


async def async_get_bridges(hass) -> List[HueBridge]:
    """Get Hue bridges."""
    return [
        entry
        for entry in hass.data[HUE_DOMAIN].values()
        if isinstance(entry, HueBridge) and entry.api
    ]


async def async_get_motions(hass):
    """Get motion sensors."""
    data_dict = {}  # The list of sensors, referenced by their hue_id.
    bridges = await async_get_bridges(hass)
    for bridge in bridges:
        for sensor in bridge.api.sensors.values():
            if sensor.type == "ZLLPresence" or sensor.type == "ZLLLightLevel":
                data_dict[sensor.uniqueid] = sensor
    return data_dict
