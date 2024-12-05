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
from custom_components.grohe_sense.enum.ondus_types import GroheTypes

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
        dashboard = await api.get_dashboard()
        return dashboard.to_dict()

    async def handle_get_appliance_data(call: ServiceCall) -> ServiceResponse:
        _LOGGER.debug('Get data for params: %s', call.data)
        device = find_device_by_name(devices, call.data['device_name'])

        if device:
            appliance_data = await api.get_appliance_data(device.location_id, device.room_id, device.appliance_id,
                                                          datetime.now().astimezone() - timedelta(hours=1),
                                                          None, None, False)
            return appliance_data.to_dict()
        else:
            return {}


    hass.services.async_register(DOMAIN, 'get_dashboard', handle_dashboard_export, schema=None, supports_response=SupportsResponse.ONLY)
    hass.services.async_register(
        DOMAIN,
        'get_appliance_data',
        handle_get_appliance_data,
        schema=voluptuous.Schema({
            voluptuous.Required('device_name'): str
        }),
        supports_response=SupportsResponse.ONLY)

    return True
