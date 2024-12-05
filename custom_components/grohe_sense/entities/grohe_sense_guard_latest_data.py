from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configuration.grohe_entity_configuration import SensorTypes, SENSOR_CONFIGURATION
from .grohe_blue_update_coordinator import GroheBlueUpdateCoordinator
from .grohe_sense_update_coordinator import GroheSenseUpdateCoordinator
from ..dto.grohe_device import GroheDevice


class GroheSenseGuardLatestData(CoordinatorEntity, SensorEntity):
    def __init__(self, domain: str, coordinator: GroheSenseUpdateCoordinator,
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
        if self._coordinator and  self._coordinator.data and self._coordinator.data.latest_data is not None:
            if self._sensor_type.value == SensorTypes.LATEST_WATER_CONSUMPTION.value:
                self._value = self._coordinator.data.latest_data.withdrawals.waterconsumption
            elif self._sensor_type.value == SensorTypes.LATEST_FLOW_RATE.value:
                self._value = self._coordinator.data.latest_data.withdrawals.maxflowrate
            elif self._sensor_type.value == SensorTypes.AVERAGE_MONTHLY_CONSUMPTION.value:
                self._value = self._coordinator.data.latest_data.average_monthly_consumption
            elif self._sensor_type.value == SensorTypes.AVERAGE_DAILY_CONSUMPTION.value:
                self._value = self._coordinator.data.latest_data.average_daily_consumption
            elif self._sensor_type.value == SensorTypes.DAILY_CONSUMPTION.value:
                self._value = self._coordinator.data.latest_data.daily_consumption

            self.async_write_ha_state()

