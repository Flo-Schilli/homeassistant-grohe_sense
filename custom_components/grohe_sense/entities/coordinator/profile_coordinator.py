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


class ProfileCoordinator(DataUpdateCoordinator, CoordinatorInterface):
    def __init__(self, hass: HomeAssistant, domain: str, api: OndusApi) -> None:
        super().__init__(hass, _LOGGER, name='Grohe', update_interval=timedelta(seconds=900), always_update=True)
        self._api = api
        self._domain = domain

        self._timezone = datetime.now().astimezone().tzinfo
        self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
        self._data: Dict[str, any] = {}

    async def _get_data(self) -> Dict[str, any]:
        api_data = await self._api.get_profile_notifications_raw(50)

        data = {'notifications': api_data}
        self._data = data
        return data

    def get_data(self) -> Dict[str, any]:
        return self._data

    async def _async_update_data(self) -> dict:
        try:
            _LOGGER.debug(f'Updating generic profile data for domain {self._domain}')
            data = await self._get_data()

            self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
            return data

        except Exception as e:
            _LOGGER.error("Error updating Profile data: %s", str(e))

    async def update_notification(self, notification_id: str, state: bool) -> None:
        await self._api.update_profile_notification_state(notification_id, state)

    async def get_initial_value(self) -> Dict[str, any]:
        return await self._get_data()

    def set_polling_interval(self, polling: int) -> None:
        self.update_interval = timedelta(seconds=polling)
        self.async_update_listeners()