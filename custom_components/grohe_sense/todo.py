from typing import List, Dict
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api.ondus_api import OndusApi
from .const import (DOMAIN)
from .dto.config_dtos import ConfigDto, NotificationDto, NotificationsDto
from .dto.grohe_device import GroheDevice
from .entities.entity_helper import EntityHelper
from .entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding todo entities from config entry {entry}')

    api: OndusApi = hass.data[DOMAIN]['session']
    config: ConfigDto = hass.data[DOMAIN]['config']
    coordinators: Dict[str, CoordinatorInterface] = hass.data[DOMAIN]['coordinator']
    notification_config: NotificationsDto = hass.data[DOMAIN]['notifications']
    helper: EntityHelper = EntityHelper(config, DOMAIN)

    if coordinators.get(api.get_user_claim(), None) is not None:
        await helper.add_todo_entities(coordinators.get(api.get_user_claim(), None), api.get_user_claim(),
                                       notification_config, async_add_entities)

