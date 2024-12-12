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
from .entities.helper import Helper
from .entities.interface.coordinator_interface import CoordinatorInterface
from .enum.ondus_types import GroheTypes

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    _LOGGER.debug(f'Adding sensor entities from config entry {entry}')

    entities: List[GroheSenseNotificationEntity | GroheSensorEntity | GroheSenseGuardWithdrawalsEntity |
                   GroheSenseGuardLastPressureEntity | GroheSenseGuardLatestData] = []
    devices: List[GroheDevice] = hass.data[DOMAIN]['devices']
    config: ConfigDto = hass.data[DOMAIN]['config']
    coordinators: Dict[str, CoordinatorInterface] = hass.data[DOMAIN]['coordinator']
    helper: Helper = Helper(config, DOMAIN)

    for device in devices:
        coordinator = coordinators.get(device.name, None)
        if coordinator is not None:
            await helper.add_entities(coordinator, device, async_add_entities)


    #     coordinator: GroheSenseUpdateCoordinator | GroheBlueUpdateCoordinator | None = None
    #
    #     if device.type == GroheTypes.GROHE_BLUE_PROFESSIONAL or device.type == GroheTypes.GROHE_BLUE_HOME:
    #         coordinator = GroheBlueUpdateCoordinator(hass, device, ondus_api)
    #     elif device.type == GroheTypes.GROHE_SENSE_GUARD or device.type == GroheTypes.GROHE_SENSE:
    #         coordinator = GroheSenseUpdateCoordinator(hass, device, ondus_api)
    #
    #     if device.type in GROHE_ENTITY_CONFIG and coordinator is not None:
    #         for sensors in GROHE_ENTITY_CONFIG.get(device.type):
    #             _LOGGER.debug(f'Attaching sensor {sensors} to device {device}')
    #             if sensors == SensorTypes.WATER_CONSUMPTION:
    #                 entities.append(GroheSenseGuardWithdrawalsEntity(DOMAIN, coordinator, device, sensors))
    #             elif sensors == SensorTypes.NOTIFICATION:
    #                 entities.append(GroheSenseNotificationEntity(DOMAIN, coordinator, device, sensors))
    #             elif sensors in [SensorTypes.LPM_DURATION, SensorTypes.LPM_LEAKAGE_LEVEL,
    #                              SensorTypes.LPM_ESTIMATED_STOP_TIME, SensorTypes.LPM_START_TIME,
    #                              SensorTypes.LPM_PRESSURE_DROP, SensorTypes.LPM_LEAKAGE, SensorTypes.LPM_STATUS,
    #                              SensorTypes.LPM_MAX_FLOW_RATE]:
    #                 if device.stripped_sw_version >= (3, 6):
    #                     entities.append(GroheSenseGuardLastPressureEntity(DOMAIN, coordinator, device, sensors))
    #             elif sensors in [SensorTypes.LATEST_WATER_CONSUMPTION, SensorTypes.LATEST_FLOW_RATE,
    #                             SensorTypes.AVERAGE_MONTHLY_CONSUMPTION, SensorTypes.AVERAGE_DAILY_CONSUMPTION,
    #                                SensorTypes.DAILY_CONSUMPTION]:
    #                 entities.append(GroheSenseGuardLatestData(DOMAIN, coordinator, device, sensors))
    #             else:
    #                 entities.append(GroheSensorEntity(DOMAIN, coordinator, device, sensors))
    #     else:
    #         _LOGGER.warning('Unrecognized appliance %s, ignoring.', device)
    #     await coordinator.async_request_refresh()
    #
    # if entities:
    #     async_add_entities(entities, update_before_add=True)
