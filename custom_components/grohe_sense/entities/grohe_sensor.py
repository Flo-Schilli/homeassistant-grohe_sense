from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configuration.grohe_entity_configuration import SensorTypes, SENSOR_CONFIGURATION
from .grohe_blue_update_coordinator import GroheBlueUpdateCoordinator
from .grohe_sense_update_coordinator import GroheSenseUpdateCoordinator
from ..dto.grohe_device import GroheDevice


class GroheSensorEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, domain: str, coordinator: GroheSenseUpdateCoordinator | GroheBlueUpdateCoordinator,
                 device: GroheDevice, sensor_type: SensorTypes):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._sensor_type = sensor_type
        self._sensor = SENSOR_CONFIGURATION.get(sensor_type)
        self._domain = domain
        self._value: float | None = None

        # Needed for Sensor Entity
        self._attr_name = f'{self._device.name} {self._sensor_type.value}'

        if self._sensor.device_class is not None:
            self._attr_device_class = self._sensor.device_class

        if self._sensor.unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = self._sensor.unit_of_measurement



    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(identifiers={(self._domain, self._device.appliance_id)},
                          name=self._device.name,
                          manufacturer='Grohe',
                          model=self._device.device_name,
                          sw_version=self._device.sw_version)

    @property
    def unique_id(self):
        return f'{self._device.appliance_id}_{self._sensor_type.value}'

    @property
    def native_value(self):
        return self._value

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._coordinator is not None:
            if self._coordinator.data is not None:
                if self._coordinator.data.measurement is not None:
                    data = self._coordinator.data.measurement[self._sensor_type.value]
                    if self._sensor.device_class == SensorDeviceClass.TIMESTAMP and isinstance(data, str):
                        self._value = datetime.fromisoformat(data)
                    else:
                        self._value = self._coordinator.data.measurement[self._sensor_type.value]
                    self.async_write_ha_state()

