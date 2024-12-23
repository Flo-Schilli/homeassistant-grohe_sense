import logging
from typing import List, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import (DOMAIN)
from .dto.config_dtos import ConfigDto
from .dto.grohe_device import GroheDevice
from .entities.entity.valve import Valve
from .entities.entity_helper import EntityHelper
from .entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding valve entities from config entry {entry}')

    data = hass.data[DOMAIN][entry.entry_id]
    devices: List[GroheDevice] = data['devices']
    config: ConfigDto = data['config']
    coordinators: Dict[str, CoordinatorInterface] = data['coordinator']
    helper: EntityHelper = EntityHelper(config, DOMAIN)

    entities: List[Valve] = []
    for device in devices:
        coordinator = coordinators.get(device.appliance_id, None)
        if coordinator is not None:
            entities.extend(await helper.add_valve_entities(coordinator, device))

    if entities:
        async_add_entities(entities)