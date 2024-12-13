from typing import List, Dict
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (DOMAIN)
from .dto.config_dtos import ConfigDto
from .dto.grohe_device import GroheDevice
from .entities.entity_helper import EntityHelper
from .entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding sensor entities from config entry {entry}')

    devices: List[GroheDevice] = hass.data[DOMAIN]['devices']
    config: ConfigDto = hass.data[DOMAIN]['config']
    coordinators: Dict[str, CoordinatorInterface] = hass.data[DOMAIN]['coordinator']
    helper: EntityHelper = EntityHelper(config, DOMAIN)

    for device in devices:
        coordinator = coordinators.get(device.appliance_id, None)
        if coordinator is not None:
            await helper.add_sensor_entities(coordinator, device, async_add_entities)
