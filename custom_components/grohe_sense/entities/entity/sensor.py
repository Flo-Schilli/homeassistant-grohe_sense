import logging
from typing import Dict

from benedict import benedict
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from ..coordinator.sense_coordinator import SenseCoordinator
from ..helper import Helper
from ...dto.grohe_device import GroheDevice
from ...dto.config_dtos import SensorDto

_LOGGER = logging.getLogger(__name__)


class Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, domain: str, coordinator: DataUpdateCoordinator, device: GroheDevice, sensor: SensorDto,
                 initial_value: Dict[str, any] = None):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._sensor = sensor
        self._domain = domain
        self._value: float | str | int | None = self._get_value(initial_value)

        # Needed for Sensor Entity
        self._attr_name = f'{self._device.name} {self._sensor.name}'

        self._attr_entity_registry_enabled_default = self._sensor.enabled

        if self._sensor.device_class is not None:
            self._attr_device_class = SensorDeviceClass(self._sensor.device_class.lower())

        if self._sensor.unit is not None:
            self._attr_native_unit_of_measurement = Helper.get_ha_units(self._sensor.unit)

        if self._sensor.category is not None:
            self._attr_entity_category = EntityCategory(self._sensor.category.lower())

        if self._sensor.state_class is not None:
            self._attr_state_class = SensorStateClass(self._sensor.state_class.lower().replace(" ", "_"))

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(identifiers={(self._domain, self._device.appliance_id)},
                          name=self._device.name,
                          manufacturer='Grohe',
                          model=self._device.device_name,
                          sw_version=self._device.sw_version)

    @property
    def unique_id(self):
        return f'{self._device.appliance_id}_{self._sensor.name.lower().replace(" ", "_")}'

    @property
    def native_value(self):
        return self._value

    def _get_value(self, full_data: Dict[str, any]) -> float | int | str | None:
        if self._sensor.keypath is not None:
            # We do have some data here, so let's extract it
            data = benedict(full_data)
            value: float | int | str | None = None
            try:
                value = data.get(self._sensor.keypath)

            except KeyError:
                _LOGGER.error(f'Device: {self._device.name} ({self._device.appliance_id}) with sensor: {self._sensor.name} has no value on keypath: {self._sensor.keypath}')

            return value

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._coordinator is not None and self._coordinator.data is not None and self._sensor.keypath is not None:
            # We do have some data here, so let's extract it
            value = self._get_value(self._coordinator.data)
            _LOGGER.debug(
                f'Device: {self._device.name} ({self._device.appliance_id}) with sensor: {self._sensor.name} has the following value on keypath {self._sensor.keypath}: {value}')
            self._value = value
            self.async_write_ha_state()
