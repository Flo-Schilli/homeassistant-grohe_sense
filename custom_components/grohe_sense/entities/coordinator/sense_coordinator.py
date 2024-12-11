import logging
from datetime import timedelta
from typing import List
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.dto.ondus_dtos import Notification

_LOGGER = logging.getLogger(__name__)


class SenseCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, domain: str, device: GroheDevice, api: OndusApi) -> None:
        super().__init__(hass, _LOGGER, name='Grohe Sense', update_interval=timedelta(seconds=300), always_update=True)
        self._api = api
        self._domain = domain
        self._device = device
        self._timezone = datetime.now().astimezone().tzinfo
        self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
        self._notifications: List[Notification] = []


    async def _async_update_data(self) -> dict:
        try:
            _LOGGER.debug(f'Updating device data for device {self._device.type} with name {self._device.name} (appliance = {self._device.appliance_id})')
            api_data = await self._api.get_appliance_details_raw(
                self._device.location_id,
                self._device.room_id,
                self._device.appliance_id)

            data = {'details': api_data}

            self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
            return data

        except Exception as e:
            _LOGGER.error("Error updating Grohe Sense data: %s", str(e))
