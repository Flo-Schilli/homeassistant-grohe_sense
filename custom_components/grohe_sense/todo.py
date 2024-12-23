from typing import List, Dict
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api.ondus_api import OndusApi
from .const import (DOMAIN)
from .dto.config_dtos import ConfigDto, NotificationDto, NotificationsDto
from .dto.grohe_device import GroheDevice
from .entities.entity.todo import Todo
from .entities.entity_helper import EntityHelper
from .entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding todo entities from config entry {entry}')

    data = hass.data[DOMAIN][entry.entry_id]
    api: OndusApi = data['session']
    devices: List[GroheDevice] = data['devices']
    config: ConfigDto = data['config']
    coordinators: Dict[str, CoordinatorInterface] = data['coordinator']
    notification_config: NotificationsDto = data['notifications']
    helper: EntityHelper = EntityHelper(config, DOMAIN)

    entities: List[Todo] = []
    for device in devices:
        if coordinators.get(api.get_user_claim(), None) is not None:
            entity = await helper.add_todo_entities(coordinators.get(api.get_user_claim(), None), device,
                                           notification_config)
            entities.extend(entity)

    if entities:
        async_add_entities(entities)