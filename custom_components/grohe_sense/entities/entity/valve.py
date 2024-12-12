import logging
from datetime import timedelta
from typing import Dict

from benedict import benedict
from homeassistant.components.valve import ValveEntity, ValveEntityFeature, ValveDeviceClass
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.util import Throttle

from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.dto.config_dtos import ValveDto
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.entities.coordinator.sense_coordinator import SenseCoordinator
from custom_components.grohe_sense.entities.helper import Helper
from custom_components.grohe_sense.entities.interface.coordinator_interface import CoordinatorInterface
from custom_components.grohe_sense.entities.interface.coordinator_valve_interface import CoordinatorValveInterface
from custom_components.grohe_sense.enum.ondus_types import OndusCommands

_LOGGER = logging.getLogger(__name__)

VALVE_UPDATE_DELAY = timedelta(minutes=1)


class Valve(CoordinatorEntity, ValveEntity):
    def __init__(self, domain: str, coordinator: DataUpdateCoordinator, device: GroheDevice, valve: ValveDto,
                 initial_value: Dict[str, any] = None):
        super().__init__(coordinator)
        self._device = device
        self._domain = domain
        self._valve = valve
        self._coordinator = coordinator
        self._is_closed = False

        # Needed for ValveEntity
        self._attr_icon = 'mdi:water'

        self._attr_name = f'{self._device.name} {self._valve.name}'

        self._attr_supported_features = Helper.get_valve_features(self._valve.features)

        if self._valve.device_class is not None:
            self._attr_device_class = ValveDeviceClass(self._valve.device_class.lower())

    @property
    def unique_id(self):
        return f'{self._device.appliance_id}_{self._valve.name.lower().replace(" ", "_")}'

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(identifiers={(self._domain, self._device.appliance_id)},
                          name=self._device.name,
                          manufacturer='Grohe',
                          model=self._device.device_name,
                          sw_version=self._device.sw_version)

    @property
    def reports_position(self) -> bool:
        return False

    @property
    def is_closed(self) -> bool:
        return self._is_closed

    async def _get_value(self, full_data: Dict[str, any]) -> bool | None:
        if self._valve.keypath is not None:
            # We do have some data here, so let's extract it
            data = benedict(full_data)
            value: bool | None = None
            try:
                value = data.get(self._valve.keypath)

            except KeyError:
                _LOGGER.error(
                    f'Device: {self._device.name} ({self._device.appliance_id}) with valve: {self._valve.name} has no value on keypath: {self._valve.keypath}')

            return value

    @callback
    def _handle_coordinator_update(self) -> None:
        if self._coordinator is not None and self._coordinator.data is not None and self._valve.keypath is not None:
            # We do have some data here, so let's extract it
            self._is_closed = self._get_value(self._coordinator.data)

    # @Throttle(VALVE_UPDATE_DELAY)
    # async def async_update(self):
    #     if isinstance(self._coordinator, CoordinatorValveInterface):
    #         data = await self._coordinator.get_valve_value()
    #         self._is_closed = self._get_value(data)

    async def _set_state(self, state):
        if isinstance(self._coordinator, CoordinatorValveInterface) and self._valve.keypath is not None:
            data_to_set = benedict()
            data_to_set[self._valve.keypath] = state
            response_data = await self._coordinator.set_valve(data_to_set)
            self._is_closed = self._get_value(response_data)

    async def async_open_valve(self) -> None:
        _LOGGER.info('Turning on water for %s', self._device.name)
        await self._set_state(True)

    async def async_close_valve(self, **kwargs):
        _LOGGER.info('Turning off water for %s', self._device.name)
        await self._set_state(False)
