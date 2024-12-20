import logging
import os.path
from datetime import datetime, timedelta
from typing import List, Dict

import voluptuous
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import aiohttp_client
from custom_components.grohe_sense.api.ondus_api import OndusApi
from custom_components.grohe_sense.const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_PLATFORM
from custom_components.grohe_sense.dto.grohe_device import GroheDevice
from custom_components.grohe_sense.entities.config_loader import ConfigLoader
from custom_components.grohe_sense.entities.coordinator.blue_home_coordinator import BlueHomeCoordinator
from custom_components.grohe_sense.entities.coordinator.blue_prof_coordinator import BlueProfCoordinator
from custom_components.grohe_sense.entities.coordinator.guard_coordinator import GuardCoordinator
from custom_components.grohe_sense.entities.coordinator.profile_coordinator import ProfileCoordinator
from custom_components.grohe_sense.entities.coordinator.sense_coordinator import SenseCoordinator
from custom_components.grohe_sense.entities.interface.coordinator_interface import CoordinatorInterface
from custom_components.grohe_sense.enum.ondus_types import GroheTypes, OndusGroupByTypes, GroheTapType

_LOGGER = logging.getLogger(__name__)

def find_device_by_name(devices: List[GroheDevice], name: str) -> GroheDevice:
    return next((device for device in devices if device.name == name), None)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.debug("Loading Grohe Sense")

    config_loader = ConfigLoader(os.path.join(os.path.dirname(__file__), 'config'))

    notifications = await hass.async_add_executor_job(config_loader.load_notifications)
    config = await hass.async_add_executor_job(config_loader.load_config)

    # Login to Grohe backend
    api = OndusApi(aiohttp_client.async_get_clientsession(hass))
    await api.login(entry.data.get('username'), entry.data.get('password'))

    # Get all devices available
    devices: List[GroheDevice] = await GroheDevice.get_devices(api)

    polling = entry.data.get('polling', 300)
    coordinators: Dict[str, CoordinatorInterface] = {}
    for device in devices:
        if device.type == GroheTypes.GROHE_SENSE:
            sense_coordinator = SenseCoordinator(hass, DOMAIN, device, api, polling)
            coordinators[device.appliance_id] = sense_coordinator
        elif device.type == GroheTypes.GROHE_SENSE_GUARD:
            guard_coordinator = GuardCoordinator(hass, DOMAIN, device, api, polling)
            coordinators[device.appliance_id] = guard_coordinator
        elif device.type == GroheTypes.GROHE_BLUE_HOME:
            blue_home_coordinator = BlueHomeCoordinator(hass, DOMAIN, device, api, polling)
            coordinators[device.appliance_id] = blue_home_coordinator
        elif device.type == GroheTypes.GROHE_BLUE_PROFESSIONAL:
            blue_prof_coordinator = BlueProfCoordinator(hass, DOMAIN, device, api, polling)
            coordinators[device.appliance_id] = blue_prof_coordinator

    # Add a generic profile coordinator so that we can use general data for the user profile as well
    profile_coordinator = ProfileCoordinator(hass, DOMAIN, api)
    coordinators[api.get_user_claim()] = profile_coordinator

    # Store devices and login information into hass object
    hass.data[DOMAIN] = {'session': api, 'devices': devices, 'coordinator': coordinators, 'notifications': notifications, 'config': config}

    await hass.config_entries.async_forward_entry_setups(entry, CONF_PLATFORM)

    ####### OPTIONS - FLOW RELOAD ######################################################################################
    async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
        _LOGGER.debug("Updating Grohe Sense options")
        for coordinator in hass.data[DOMAIN]['coordinator'].values():
            coordinator.set_polling_interval(polling)
            await coordinator.async_request_refresh()

    entry.async_on_unload(entry.add_update_listener(update_listener))

    ####### SERVICES ###################################################################################################
    async def handle_dashboard_export(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Export data for params: %s', call.data)
        return await api.get_dashboard_raw()


    async def handle_get_appliance_data(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get data for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])
        group_by_str = call.data.get('group_by').lower() if call.data.get('group_by') else None

        if device:
            if group_by_str is None:
                group_by = OndusGroupByTypes.DAY if device.type == GroheTypes.GROHE_SENSE else OndusGroupByTypes.HOUR
            else:
                group_by = OndusGroupByTypes(group_by_str)

            return await api.get_appliance_data_raw(device.location_id, device.room_id, device.appliance_id,
                                                    datetime.now().astimezone() - timedelta(hours=1),
                                                    None, group_by, False)
        else:
            return {}

    async def handle_get_appliance_details(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get details for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            return await api.get_appliance_details_raw(device.location_id, device.room_id, device.appliance_id)

        else:
            return {}

    async def handle_get_appliance_command(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get possible commands for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            data = await api.get_appliance_command_raw(device.location_id, device.room_id, device.appliance_id)
            if data is None:
                return {}
            else:
                return data
        else:
            return {}

    async def handle_set_appliance_command(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Set commands for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])
        commands = call.data.get('commands')

        data_to_send = {'command': commands}
        if device:
            data = await api.set_appliance_command_raw(device.location_id, device.room_id, device.appliance_id, device.type, data_to_send)
            if data is None:
                return {}
            else:
                return data
        else:
            return {}

    async def handle_tap_water(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Tap water for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])
        water_type = call.data.get('water_type')
        water_amount = call.data.get('amount')


        if device and (device.type == GroheTypes.GROHE_BLUE_HOME or device.type == GroheTypes.GROHE_BLUE_PROFESSIONAL):
            try:
                mapped_water_type = GroheTapType[water_type.upper()]
                data_to_send = {'command': {'tap_type': mapped_water_type.value, 'tap_amount': water_amount}}
                data = await api.set_appliance_command_raw(device.location_id, device.room_id, device.appliance_id, device.type, data_to_send)
                if data is None:
                    return {}
                else:
                    return data
            except KeyError as e:
                return {'error': f'The following error happened: {e}'}
        else:
            return {'error': 'Device is not a Grohe Blue device'}

    async def handle_get_appliance_status(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get status for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            data = await api.get_appliance_status_raw(device.location_id, device.room_id, device.appliance_id)
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
            data = await api.get_appliance_notifications_raw(device.location_id, device.room_id, device.appliance_id)

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
            data = await api.get_appliance_pressure_measurement_raw(device.location_id, device.room_id, device.appliance_id)

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

        data = await api.get_profile_notifications_raw(limit)

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
        'get_appliance_command',
        handle_get_appliance_command,
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
        'set_appliance_command',
        handle_set_appliance_command,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
            voluptuous.Required('commands'): dict,
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

    hass.services.async_register(
        DOMAIN,
        'tap_water',
        handle_tap_water(),
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str,
            voluptuous.Required('water_type'): str,
            voluptuous.Required('amount'): int,
        }),
        supports_response=SupportsResponse.ONLY)

    return True
