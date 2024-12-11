import logging
from typing import List

from custom_components.grohe_sense.dto.config_dtos import ConfigDto
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.entities.coordinator.sense_coordinator import SenseCoordinator
from custom_components.grohe_sense.entities.entity.sensor import Sensor

_LOGGER = logging.getLogger(__name__)


class Helper:
    def __init__(self, config: ConfigDto, domain: str):
        self._config = config
        self._domain = domain


    def add_entities(self, coordinator, device: GroheDevice, async_add_entities):

        config_name: str = ''
        if isinstance(coordinator, SenseCoordinator):
            config_name = 'GroheSense'

        if config_name:
            entities: List = []
            if self._config.get_device_config(config_name) is not None:
                for sensor in self._config.get_device_config(config_name).sensors:
                    _LOGGER.debug(f'Adding sensor {sensor.name} for device {device.name}')
                    entities.append(Sensor(self._domain, coordinator, device, sensor))
            if entities:
                async_add_entities(entities, update_before_add=True)

