import logging
from typing import List

from custom_components.grohe_sense.dto.config_dtos import ConfigDto
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.entities.coordinator.blue_home_coordinator import BlueHomeCoordinator
from custom_components.grohe_sense.entities.coordinator.blue_prof_coordinator import BlueProfCoordinator
from custom_components.grohe_sense.entities.coordinator.guard_coordinator import GuardCoordinator
from custom_components.grohe_sense.entities.coordinator.sense_coordinator import SenseCoordinator
from custom_components.grohe_sense.entities.entity.sensor import Sensor
from custom_components.grohe_sense.entities.entity.valve import Valve
from custom_components.grohe_sense.entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


class EntityHelper:
    def __init__(self, config: ConfigDto, domain: str):
        self._config = config
        self._domain = domain


    async def add_sensor_entities(self, coordinator: CoordinatorInterface, device: GroheDevice, async_add_entities):

        config_name: str = ''
        if isinstance(coordinator, SenseCoordinator):
            config_name = 'GroheSense'
        elif isinstance(coordinator, GuardCoordinator):
            config_name = 'GroheSenseGuard'
        elif isinstance(coordinator, BlueHomeCoordinator):
            config_name = 'GroheBlueHome'
        elif isinstance(coordinator, BlueProfCoordinator):
            config_name = 'GroheBlueProf'

        if config_name:
            entities: List = []
            initial_value = await coordinator.get_initial_value()
            if self._config.get_device_config(config_name) is not None:
                for sensor in self._config.get_device_config(config_name).sensors:
                    _LOGGER.debug(f'Adding sensor {sensor.name} for device {device.name}')
                    entities.append(Sensor(self._domain, coordinator, device, sensor, initial_value))
            if entities:
                async_add_entities(entities, update_before_add=True)

    async def add_valve_entities(self, coordinator: CoordinatorInterface, device: GroheDevice, async_add_entities):

        config_name: str = ''
        if isinstance(coordinator, SenseCoordinator):
            config_name = 'GroheSense'
        elif isinstance(coordinator, GuardCoordinator):
            config_name = 'GroheSenseGuard'
        elif isinstance(coordinator, BlueHomeCoordinator):
            config_name = 'GroheBlueHome'
        elif isinstance(coordinator, BlueProfCoordinator):
            config_name = 'GroheBlueProf'

        if config_name:
            entities: List = []
            initial_value = await coordinator.get_initial_value()
            if (self._config.get_device_config(config_name) is not None
                    and self._config.get_device_config(config_name).valves is not None):
                for valve in self._config.get_device_config(config_name).valves:
                    _LOGGER.debug(f'Adding valve {valve.name} for device {device.name}')
                    entities.append(Valve(self._domain, coordinator, device, valve))
            if entities:
                async_add_entities(entities, update_before_add=True)

