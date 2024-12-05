import json
import logging
from datetime import timedelta
from typing import List
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.dto.grohe_coordinator_dtos import MeasurementSenseDto, CoordinatorDto, \
    LastPressureMeasurement
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.dto.ondus_dtos import Notification, DataLatest
from custom_components.grohe_sense.enum.ondus_types import GroheTypes, OndusGroupByTypes

_LOGGER = logging.getLogger(__name__)


class GroheSenseUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, device: GroheDevice, api: OndusApi) -> None:
        super().__init__(hass, _LOGGER, name='Grohe Sense', update_interval=timedelta(seconds=300), always_update=True)
        self._api = api
        self._device = device
        self._timezone = datetime.now().astimezone().tzinfo
        self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
        self._notifications: List[Notification] = []

    async def _get_notification(self) -> str:
        """
        Get the latest notification for the device.

        :return: The latest notification text. If no notifications are found, returns 'No notifications'.
        :rtype: str
        """
        _LOGGER.debug('Get notification')
        notifications = await self._api.get_appliance_notifications(self._device.location_id, self._device.room_id,
                                                                    self._device.appliance_id)
        notifications.sort(key=lambda n: n.timestamp, reverse=True)
        notifications = [notification for notification in notifications if notification.is_read is False]

        if len(notifications) > 0:
            return f'{notifications[0].notification_text}'
        else:
            return 'No notifications'

    async def _get_actual_measurement(self) -> MeasurementSenseDto:
        """
        Get the actual measurement data of the device.

        :return: MeasurementSenseDto object with the following attributes:
                 - pressure (float): The pressure measurement of the device.
                 - flow_rate (float): The flow rate measurement of the device.
                 - humidity (float): The humidity measurement of the device.
                 - temperature (float): The temperature measurement of the device.
        """
        group_by = OndusGroupByTypes.DAY if self._device.type == GroheTypes.GROHE_SENSE else OndusGroupByTypes.HOUR

        _LOGGER.debug('Get actual measurement')
        measurements_response = await self._api.get_appliance_data(self._device.location_id, self._device.room_id,
                                                                   self._device.appliance_id,
                                                                   self._last_update - timedelta(hours=1), None,
                                                                   group_by, False)

        measurement_data = MeasurementSenseDto()
        if measurements_response and measurements_response.data and measurements_response.data.measurement and len(measurements_response.data.measurement) > 0:
            """Get the first measurement of the device. This is also the latest measurement"""
            measurements_response.data.measurement.sort(key=lambda m: m.date, reverse=True)
            measure = measurements_response.data.measurement[0]

            measurement_data.pressure = measure.pressure
            measurement_data.flow_rate = measure.flow_rate
            measurement_data.humidity = measure.humidity

            if self._device.type == GroheTypes.GROHE_SENSE:
                measurement_data.temperature = measure.temperature
            elif self._device.type == GroheTypes.GROHE_SENSE_GUARD:
                measurement_data.temperature = measure.temperature_guard

        return measurement_data

    async def _get_last_pressure_measurement(self) -> LastPressureMeasurement | None:
        _LOGGER.debug(f'Get last pressure measurement for appliance {self._device.appliance_id}')

        _LOGGER.debug('Get last pressure measurement')
        appliance_details = await self._api.get_appliance_details(self._device.location_id, self._device.room_id,
                                                                  self._device.appliance_id)

        measurement: LastPressureMeasurement | None = None
        if appliance_details and appliance_details.last_pressure_measurement is not None:
            measurement = LastPressureMeasurement.from_dict(appliance_details.last_pressure_measurement.to_dict())
            _LOGGER.debug(f'PRESSURE MEASUREMENT -> Received the following pressure measurement for '
                          f'appliance {self._device.appliance_id}: {measurement}')
            if appliance_details.last_pressure_measurement.pressure_curve is not None:
                curve = appliance_details.last_pressure_measurement.pressure_curve
                flow_rates = [flow.fr for flow in curve]
                flow_rates.sort(reverse=True)
                measurement.max_flow_rate = flow_rates[0] if len(flow_rates) > 0 else None
        elif appliance_details is not None:
            _LOGGER.debug(f'PRESSURE MEASUREMENT -> Did a pressure measurement for appliance'
                          f' {self._device.appliance_id} but only received the following data: {appliance_details}')
        return measurement


    async def _get_withdrawal(self) -> float | None:
        """
        This method retrieves the latest withdrawals for a given device.

        :param self: The current object instance.
        :return: The latest withdrawal value
                 (float). If no withdrawal data is available, the corresponding values will be None.
        :rtype: float | None
        """
        _LOGGER.debug('Get latest withdrawal')
        measurements_response = await self._api.get_appliance_data(self._device.location_id, self._device.room_id,
                                                                   self._device.appliance_id,
                                                                   self._last_update, None, None, True)

        withdrawal: float | None = None
        if measurements_response is not None:
            if measurements_response.data is not None:
                if (measurements_response.data.withdrawals is not None
                        and len(measurements_response.data.withdrawals) > 0):
                    withdrawals = measurements_response.data.withdrawals
                    withdrawals.sort(key=lambda m: m.date, reverse=True)
                    withdrawal = withdrawals[0].waterconsumption if withdrawals else None
                else:
                    withdrawal = 0

        return withdrawal

    async def _get_latest_data(self) -> DataLatest | None:
        """
        Fetches the latest data for a specified appliance. If the appliance has current data available,
        it returns the latest data; otherwise, it returns None.

        :return: The latest data of the appliance if available; otherwise, None
        :rtype: DataLatest | None
        """
        _LOGGER.debug('Get latest data')
        appliance_details = await self._api.get_appliance_details(self._device.location_id, self._device.room_id,
                                                                  self._device.appliance_id)

        if appliance_details is not None and appliance_details.data_latest is not None:
            latest_data = appliance_details.data_latest
        else:
            latest_data = None

        return latest_data

    async def _async_update_data(self) -> CoordinatorDto:
        try:
            _LOGGER.debug(f'Updating {self._device.type} (appliance = {self._device.appliance_id}) data')
            data = CoordinatorDto()
            data.withdrawal = await self._get_withdrawal()
            data.measurement = await self._get_actual_measurement()
            data.notification = await self._get_notification()


            if self._device.type == GroheTypes.GROHE_SENSE_GUARD:
                data.last_pressure_measurement = await self._get_last_pressure_measurement()
                data.latest_data = await self._get_latest_data()

            self._last_update = datetime.now().astimezone().replace(tzinfo=self._timezone)
            return data

        except Exception as e:
            _LOGGER.error("Error updating Grohe Sense data: %s", str(e))
