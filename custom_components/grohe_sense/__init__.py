import logging
from datetime import datetime, timedelta
from typing import List

import voluptuous
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import aiohttp_client
from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.enum.ondus_types import GroheTypes, OndusGroupByTypes

_LOGGER = logging.getLogger(__name__)

def find_device_by_name(devices: List[GroheDevice], name: str) -> GroheDevice:
    return next((device for device in devices if device.name == name), None)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Loading Grohe Sense")

    session = aiohttp_client.async_get_clientsession(hass)

    api = OndusApi(session)
    await api.login(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])

    devices: List[GroheDevice] = await GroheDevice.get_devices(api)

    hass.data[DOMAIN] = {'session': api, 'devices': devices}

    await hass.config_entries.async_forward_entry_setups(entry, CONF_PLATFORM)


    async def handle_dashboard_export(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Export data for params: %s', call.data)
        return await api.get_dashboard(True)


    async def handle_get_appliance_data(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get data for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])
        group_by_str = call.data.get('group_by').lower() if call.data.get('group_by') else None

        if device:
            if group_by_str is None:
                group_by = OndusGroupByTypes.DAY if device.type == GroheTypes.GROHE_SENSE else OndusGroupByTypes.HOUR
            else:
                group_by = OndusGroupByTypes(group_by_str)

            return await api.get_appliance_data(device.location_id, device.room_id, device.appliance_id,
                                                datetime.now().astimezone() - timedelta(hours=1),
                                                None, group_by, False, True)
        else:
            return {}

    async def handle_get_appliance_details(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get details for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            return await api.get_appliance_details_type_insensitive(device.location_id, device.room_id, device.appliance_id)

        else:
            return {}

    async def handle_get_appliance_status(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get status for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            data = await api.get_appliance_status_type_insensitive(device.location_id, device.room_id, device.appliance_id)
            if data is None:
                return {}
            else:
                return data

        else:
            return {}

    async def handle_get_appliance_notifications(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get notifications for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            data = await api.get_appliance_notifications_type_insensitive(device.location_id, device.room_id, device.appliance_id)

            if data is None:
                return {}
            elif isinstance(data, list) and len(data) > 0:
                return {
                    'notifications': [dict(notification) for notification in data]
                }
            else:
                return {}

        else:
            return {}

    async def handle_get_appliance_pressure_measurement(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get pressure measurement for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            data = await api.get_appliance_pressure_measurement_type_insensitive(device.location_id, device.room_id, device.appliance_id)

            if data is None:
                return {}
            elif isinstance(data, list) and len(data) > 0:
                return {
                    'pressure_measurements': [dict(measurement) for measurement in data]
                }
            else:
                return data

        else:
            return {}

    async def handle_get_profile_notifications(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get profile notifications for params: %s', call.data)
        limit = call.data.get('limit')
        if limit is None:
            limit = 50

        data = await api.get_profile_notifications_type_insensitive(limit)

        if data is None:
            return {}
        elif isinstance(data, list) and len(data) > 0:
            return {
                'notifications': [dict(notification) for notification in data]
            }
        else:
            return data



    hass.services.async_register(DOMAIN, 'get_dashboard', handle_dashboard_export, schema=None, supports_response=SupportsResponse.ONLY)
    hass.services.async_register(
        DOMAIN,
        'get_appliance_data',
        handle_get_appliance_data,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
            voluptuous.Optional('group_by'): str,
        }),
        supports_response=SupportsResponse.ONLY)

    hass.services.async_register(
        DOMAIN,
        'get_appliance_details',
        handle_get_appliance_details,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
        }),
        supports_response=SupportsResponse.ONLY)

    hass.services.async_register(
        DOMAIN,
        'get_appliance_status',
        handle_get_appliance_status,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
        }),
        supports_response=SupportsResponse.ONLY)

    hass.services.async_register(
        DOMAIN,
        'get_appliance_notifications',
        handle_get_appliance_notifications,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
        }),
        supports_response=SupportsResponse.ONLY)

    hass.services.async_register(
        DOMAIN,
        'get_appliance_pressure_measurement',
        handle_get_appliance_pressure_measurement,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
        }),
        supports_response=SupportsResponse.ONLY)

    hass.services.async_register(
        DOMAIN,
        'get_profile_notifications',
        handle_get_profile_notifications,
        schema=voluptuous.Schema({
            voluptuous.Optional('limit'): int,
        }),
        supports_response=SupportsResponse.ONLY)

    return True
