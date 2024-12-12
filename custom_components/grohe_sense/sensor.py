from typing import List, Dict
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (DOMAIN)
from .api.ondus_api import OndusApi
from .dto.config_dtos import ConfigDto
from .dto.grohe_device import GroheDevice
from .entities.configuration.grohe_entity_configuration import GROHE_ENTITY_CONFIG, SensorTypes
from .entities.coordinator.sense_coordinator import SenseCoordinator
from .entities.entity.sensor import Sensor
from .entities.grohe_blue_update_coordinator import GroheBlueUpdateCoordinator
from .entities.grohe_sense_guard_last_pressure import GroheSenseGuardLastPressureEntity
from .entities.grohe_sense_guard_latest_data import GroheSenseGuardLatestData
from .entities.grohe_sensor import GroheSensorEntity
from .entities.grohe_sense_guard import GroheSenseGuardWithdrawalsEntity
from .entities.grohe_sense_notifications import GroheSenseNotificationEntity
from .entities.grohe_sense_update_coordinator import GroheSenseUpdateCoordinator
from .entities.entity_helper import EntityHelper
from .entities.interface.coordinator_interface import CoordinatorInterface
from .enum.ondus_types import GroheTypes

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
