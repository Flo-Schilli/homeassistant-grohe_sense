import logging
from datetime import timedelta
from typing import List, Dict
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.dto.ondus_dtos import Notification
from custom_components.grohe_sense.entities.interface.coordinator_interface import CoordinatorInterface

_LOGGER = logging.getLogger(__name__)


class BlueProfCoordinator(DataUpdateCoordinator, CoordinatorInterface):
    def __init__(self, hass: HomeAssistant, domain: str, device: GroheDevice, api: OndusApi, polling: int = 300) -> None:
        super().__init__(hass, _LOGGER, name='Grohe Sense', update_interval=timedelta(seconds=polling), always_update=True)
        self._api = api
        self._domain = domain
        self._device = device
        self._timezone = datetime.now().astimezone().tzinfo
        self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
        self._notifications: List[Notification] = []

    async def _get_data(self) -> Dict[str, any]:
        # Before each call, get the new current measurement
        await self._api.set_appliance_command_raw(
            self._device.location_id,
            self._device.room_id,
            self._device.appliance_id,
            self._device.type,
            {'command': {'get_current_measurement': True}})

        api_data = await self._api.get_appliance_details_raw(
            self._device.location_id,
            self._device.room_id,
            self._device.appliance_id)

        try:
            status = { val['type']: val['value'] for val in api_data['status'] }
        except AttributeError as e:
            _LOGGER.debug(f'Status could not be mapped: {e}')
            status = None

        data = {'details': api_data, 'status': status}
        return data

    async def _async_update_data(self) -> dict:
        try:
            _LOGGER.debug(f'Updating device data for device {self._device.type} with name {self._device.name} (appliance = {self._device.appliance_id})')
            data = await self._get_data()

            self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
            return data

        except Exception as e:
            _LOGGER.error("Error updating Grohe Blue Professional data: %s", str(e))

    async def get_initial_value(self) -> Dict[str, any]:
        return await self._get_data()

    def set_polling_interval(self, polling: int) -> None:
        self.update_interval = timedelta(seconds=polling)
        self.async_update_listeners()