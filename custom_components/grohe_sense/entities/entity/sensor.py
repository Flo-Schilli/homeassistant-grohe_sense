import logging
from datetime import datetime

from benedict import benedict
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinator.sense_coordinator import SenseCoordinator
from ...dto.grohe_device import GroheDevice
from ...dto.config_dtos import SensorDto

_LOGGER = logging.getLogger(__name__)


class Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, domain: str, coordinator: SenseCoordinator, device: GroheDevice, sensor: SensorDto):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._sensor = sensor
        self._domain = domain
        self._value: float | str | None = None

        # Needed for Sensor Entity
        self._attr_name = f'{self._device.name} {self._sensor.name}'

        if self._sensor.device_class is not None:
            self._attr_device_class = SensorDeviceClass(self._sensor.device_class.lower())

        if self._sensor.unit is not None:
            self._attr_native_unit_of_measurement = self._sensor.unit

        if self._sensor.category is not None:
            self._attr_entity_category = EntityCategory(self._sensor.category.lower())

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(identifiers={(self._domain, self._device.appliance_id)},
                          name=self._device.name,
                          manufacturer='Grohe',
                          model=self._device.device_name,
                          sw_version=self._device.sw_version)

    @property
    def unique_id(self):
        return f'{self._device.appliance_id}_{self._sensor.name}'

    @property
    def native_value(self):
        return self._value

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._coordinator is not None and self._coordinator.data is not None and self._sensor.keypath is not None:
            # We do have some data here, so let's extract it
            data = benedict(self._coordinator.data)

            try:
                value = data.get(self._sensor.keypath)
                self._value = value
                self.async_write_ha_state()
            except KeyError:
                _LOGGER.error(f'Device: {self._device.name} ({self._device.appliance_id}) with sensor: {self._sensor.name} has no value on keypath: {self._sensor.keypath}')
