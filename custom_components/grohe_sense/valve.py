import logging
from typing import List, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import (DOMAIN)
from .api.ondus_api import OndusApi
from .dto.config_dtos import ConfigDto
from .dto.grohe_device import GroheDevice
from .entities.entity_helper import EntityHelper
from .entities.grohe_sense_guard_valve import GroheSenseGuardValve
from .entities.interface.coordinator_interface import CoordinatorInterface
from .enum.ondus_types import GroheTypes

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding valve entities from config entry {entry}')

    devices: List[GroheDevice] = hass.data[DOMAIN]['devices']
    config: ConfigDto = hass.data[DOMAIN]['config']
    coordinators: Dict[str, CoordinatorInterface] = hass.data[DOMAIN]['coordinator']
    helper: EntityHelper = EntityHelper(config, DOMAIN)

    for device in devices:
        coordinator = coordinators.get(device.appliance_id, None)
        if coordinator is not None:
            await helper.add_valve_entities(coordinator, device, async_add_entities)
