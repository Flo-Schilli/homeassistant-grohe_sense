import logging
from typing import List

from custom_components.grohe_sense.dto.config_dtos import ConfigDto, NotificationDto, NotificationsDto, SensorDto
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.entities.coordinator.blue_home_coordinator import BlueHomeCoordinator
from custom_components.grohe_sense.entities.coordinator.blue_prof_coordinator import BlueProfCoordinator
from custom_components.grohe_sense.entities.coordinator.guard_coordinator import GuardCoordinator
from custom_components.grohe_sense.entities.coordinator.sense_coordinator import SenseCoordinator
from custom_components.grohe_sense.entities.entity.sensor import Sensor
from custom_components.grohe_sense.entities.entity.todo import Todo
from custom_components.grohe_sense.entities.entity.valve import Valve
from custom_components.grohe_sense.entities.interface.coordinator_interface import CoordinatorInterface
from custom_components.grohe_sense.enum.ondus_types import GroheTypes

_LOGGER = logging.getLogger(__name__)


class EntityHelper:
    def __init__(self, config: ConfigDto, domain: str):
        self._config = config
        self._domain = domain

    def _is_valid_version(self, device: GroheDevice, sensor: SensorDto):
        if sensor.min_version is not None:
            sensor_version = tuple(map(int, sensor.min_version.split('.')[:2]))
            return device.stripped_sw_version >= sensor_version
        else:
            return True

    def _get_config_name_by_device_type(self, device: GroheDevice) -> str:
        config_name: str = ''
        if device.type == GroheTypes.GROHE_SENSE:
            config_name = 'GroheSense'
        elif device.type == GroheTypes.GROHE_SENSE_GUARD:
            config_name = 'GroheSenseGuard'
        elif device.type == GroheTypes.GROHE_BLUE_HOME:
            config_name = 'GroheBlueHome'
        elif device.type == GroheTypes.GROHE_BLUE_PROFESSIONAL:
            config_name = 'GroheBlueProf'

        return config_name


    async def add_sensor_entities(self, coordinator: CoordinatorInterface, device: GroheDevice,
                                  notification_config: NotificationsDto) -> List[Sensor]:

        config_name = self._get_config_name_by_device_type(device)

        entities: List = []
        if config_name:
            initial_value = await coordinator.get_initial_value()
            if self._config.get_device_config(config_name) is not None:
                for sensor in self._config.get_device_config(config_name).sensors:
                    if self._is_valid_version(device, sensor):
                        _LOGGER.debug(f'Adding sensor {sensor.name} for device {device.name}')
                        entities.append(Sensor(self._domain, coordinator, device, sensor, notification_config, initial_value))
        return entities


    async def add_todo_entities(self, coordinator: CoordinatorInterface, device: GroheDevice,
                                notification_config: NotificationsDto) -> List[Todo]:

        config_name = self._get_config_name_by_device_type(device)

        entities: List = []
        if (self._config.get_device_config(config_name) is not None
         and self._config.get_device_config(config_name).todos is not None):
            for todo in self._config.get_device_config(config_name).todos:
                _LOGGER.debug(f'Adding todo {todo.name} for device {device.name}')
                entities.append(Todo(self._domain, coordinator, device, todo, notification_config))

        return entities


    async def add_valve_entities(self, coordinator: CoordinatorInterface, device: GroheDevice) -> List[Valve]:

        config_name = self._get_config_name_by_device_type(device)

        entities: List[Valve] = []
        if config_name:
            if (self._config.get_device_config(config_name) is not None
                    and self._config.get_device_config(config_name).valves is not None):
                for valve in self._config.get_device_config(config_name).valves:
                    _LOGGER.debug(f'Adding valve {valve.name} for device {device.name}')
                    entities.append(Valve(self._domain, coordinator, device, valve))

        return entities


