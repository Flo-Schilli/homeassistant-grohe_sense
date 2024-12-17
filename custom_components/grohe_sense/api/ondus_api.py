import logging
import string
import urllib.parse
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from typing import List, Optional, Tuple, Dict, Any

import aiohttp
import jwt
from aiohttp import ClientSession
from lxml import html

from custom_components.grohe_sense.dto.ondus_dtos import Locations, Location, Room, Appliance, \
    ApplianceCommand, OndusToken, PressureMeasurementStart
from custom_components.grohe_sense.enum.ondus_types import OndusGroupByTypes, GroheTypes

_LOGGER = logging.getLogger(__name__)


def is_iteratable(obj: Any) -> bool:
    """
    Check if an object is iterable.

    :param obj: The object to be checked.
    :return: True if the object is iterable, False otherwise.
    """
    try:
        iter(obj)
        return True
    except TypeError:
        return False


class OndusApi:
    __base_url: str = 'https://idp2-apigw.cloud.grohe.com'
    __api_url: str = __base_url + '/v3/iot'
    __tokens: OndusToken = None
    __token_update_time: datetime = None

    __update_token_before_expiration: timedelta = timedelta(seconds=300)
    __access_token_expires: datetime = None
    __refresh_token_expires: datetime = None
    __username: str = None
    __password: str = None
    __user_id: str = None

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    def __set_token(self, token: OndusToken) -> None:
        """
        Set the token and update the last update

        :param token: The token to be set.
        :return: None
        """
        self.__tokens = token
        access_token_data = jwt.decode(token.access_token, options={'verify_signature': False})
        self.__access_token_expires = datetime.fromtimestamp(int(access_token_data['exp']))
        self.__user_id = access_token_data['sub']

        refresh_token_data = jwt.decode(token.refresh_token, options={'verify_signature': False})
        self.__refresh_token_expires = datetime.fromtimestamp(int(refresh_token_data['exp']))

        self.__token_update_time = datetime.now()

    async def __get_oidc_action(self) -> Tuple[SimpleCookie, str]:
        """
        Get the cookie and action from the OIDC login endpoint.

        :return: A tuple containing the cookie and action URL.
        :rtype: Tuple[SimpleCookie, str]
        """
        try:
            response = await self._session.get(f'{self.__api_url}/oidc/login')
        except aiohttp.ClientError as e:
            _LOGGER.error('Could not access url /oidc/login %s', str(e))
        else:
            cookie = response.cookies
            tree = html.fromstring(await response.text())

            name = tree.xpath("//html/body/div/div/div/div/div/div/div/form")
            action = name[0].action

            return cookie, action

    async def __login(self, url: str, username: str, password: str, cookies: SimpleCookie) -> str:
        """
        Login to the specified URL with the provided username, password, and cookies.

        :param url: The URL to log in to.
        :type url: str
        :param username: The username for authentication.
        :type username: str
        :param password: The password for authentication.
        :type password: str
        :param cookies: The cookies to include in the request.
        :type cookies: SimpleCookie
        :return: The token URL if login is successful, otherwise returns None.
        :rtype: str
        """
        payload = {
            'username': username,
            'password': password
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'origin': self.__api_url,
            'referer': self.__api_url + '/oidc/login',
            'X-Requested-With': 'XMLHttpRequest',
        }

        try:
            response = await self._session.post(url=url, data=payload, headers=headers, cookies=cookies,
                                                allow_redirects=False)

        except aiohttp.ClientError as e:
            _LOGGER.error('Get Refresh Token Action Exception %s', str(e))
        else:
            if response.status == 302:
                token_url = response.headers['Location'].replace('ondus', 'https')
                return token_url
            else:
                _LOGGER.error('Login failed (and we got no redirect) with status code %s', response.status)

    async def __get_tokens(self, url: str, cookies: SimpleCookie) -> OndusToken:
        """
        Retrieve OndusToken from the provided URL after log in with username and password.

        :param url: The URL to send the request to.
        :type url: str
        :param cookies: The cookies to include in the request.
        :type cookies: SimpleCookie
        :return: The OndusToken object obtained from the response.
        :rtype: OndusToken
        """
        try:
            response = await self._session.get(url=url, cookies=cookies)
        except Exception as e:
            _LOGGER.error('Get Refresh Token response exception %s', str(e))
        else:
            return OndusToken.from_dict(await response.json())

    async def __refresh_tokens(self, refresh_token: str) -> OndusToken:
        """
        Refreshes the tokens using the provided refresh token.

        :param refresh_token: The refresh token to use for refreshing the tokens.
        :type refresh_token: str
        :return: The new OndusToken generated after refreshing the tokens.
        :rtype: OndusToken
        """
        _LOGGER.debug('Refresh tokens as access token expired.')
        response = await self._session.post(url=f'{self.__api_url}/oidc/refresh', json={
            'refresh_token': refresh_token
        })

        return OndusToken.from_dict(await response.json())

    def __is_access_token_valid(self) -> bool:
        """
        Check if the access token is still valid.

        :return: True if the token is valid, False otherwise.
        :rtype: bool
        """
        if (self.__tokens is not None and
                self.__access_token_expires is not None and
                self.__access_token_expires - self.__update_token_before_expiration > datetime.now()):
            return True
        else:
            return False

    def __is_refresh_token_valid(self) -> bool:
        """
        Check if the refresh token is valid.

        :return: True if the refresh token is still valid, False otherwise.
        :rtype: bool
        """
        if (self.__tokens is not None and
                self.__refresh_token_expires is not None and
                self.__refresh_token_expires - self.__update_token_before_expiration > datetime.now()):
            return True
        else:
            return False

    async def __update_invalid_token(self):
        """
        Update the invalid token with a new token if possible, otherwise raise an error.

        :return: None
        """
        if not self.__is_access_token_valid() and self.__is_refresh_token_valid():
            self.__set_token(await self.__refresh_tokens(self.__tokens.refresh_token))
        elif not self.__is_access_token_valid() and not self.__is_refresh_token_valid():
            _LOGGER.error('Both access token and refresh token are invalid. Please login again.')
            raise ValueError('Both access token and refresh token are invalid. Please login again.')

    async def __get(self, url: str) -> Dict[str, Any] | None:
        """
        Retrieve data from the specified URL using a GET request.

        :param url: The URL to retrieve data from.
        :type url: str
        :return: A dictionary containing the retrieved data.
        :rtype: Dict[str, Any]
        """
        await self.__update_invalid_token()
        response = await self._session.get(url=url, headers={
            'Authorization': f'Bearer {self.__tokens.access_token}'
        })

        if response.status in (200, 201):
            return await response.json()
        else:
            _LOGGER.warning(f'URL {url} returned status code {response.status}')
            return None

    async def __post(self, url: str, data: Dict[str, Any] | None) -> Dict[str, Any]:
        """
        Send a POST request to the specified URL with the given data.

        :param url: The URL to send the request to.
        :type url: str
        :param data: The data to include in the request body.
        :type data: Dict[str, Any]
        :return: A dictionary representing the response JSON.
        :rtype: Dict[str, Any]
        """
        await self.__update_invalid_token()
        response = await self._session.post(url=url, json=data, headers={
            'Authorization': f'Bearer {self.__tokens.access_token}'
        })

        if response.status == 201:
            return await response.json()

    async def __put(self, url: str, data: Dict[str, Any] | None) -> Dict[str, Any] | None:
        """
        Send a PUT request to the specified URL with the given data.

        :param url: The URL to send the request to.
        :type url: str
        :param data: The data to include in the request body.
        :type data: Dict[str, Any]
        :return: A dictionary representing the response JSON.
        :rtype: Dict[str, Any]
        """
        await self.__update_invalid_token()
        response = await self._session.put(url=url, json=data, headers={
            'Authorization': f'Bearer {self.__tokens.access_token}'
        })

        if response.status == 201:
            return await response.json()
        elif response.status == 200:
            return None
        else:
            _LOGGER.warning(f'URL {url} returned status code {response.status} for PUT request')

    async def login(self, username: Optional[str] = None, password: Optional[str] = None,
                    refresh_token: Optional[str] = None) -> bool:
        """
        Logs a user into the system.

        Note: Whether username and password or a refresh token is required.

        :param username: The username of the user.
        :type username: str
        :param password: The password of the user.
        :type password: str
        :param refresh_token: A valid refresh token
        :type refresh_token: Optional[str]
        :return: None
        """
        _LOGGER.info('Login to Ondus API')

        if refresh_token is not None:
            _LOGGER.debug('Login with refresh token')
            self.__set_token(await self.__refresh_tokens(refresh_token))

        elif username is not None and password is not None:
            _LOGGER.debug('Login with username/password')
            cookie, action = await self.__get_oidc_action()
            token_url = await self.__login(action, username, password, cookie)
            self.__set_token(await self.__get_tokens(token_url, cookie))

        else:
            _LOGGER.error('Login required.')
            raise ValueError('Invalid login parameters.')

        if self.__is_access_token_valid():
            return True
        else:
            return False

    def get_user_claim(self) -> str:
        return self.__user_id

    async def get_dashboard_raw(self) -> Dict[str, any]:
        """
        Get the dashboard information.
        These dashboard information include most of the data which can also be queried by the appliance itself

        :return: The locations information obtained from the dashboard.
        :rtype: Dict[str, any]
        """
        _LOGGER.debug('Get dashboard information')
        url = f'{self.__api_url}/dashboard'
        return await self.__get(url)


    async def get_locations(self) -> List[Location]:
        """
        Get a list of locations.

        :return: A list of Location objects.
        :rtype: List[Location]
        """
        _LOGGER.debug('Get locations')
        url = f'{self.__api_url}/locations'
        data = await self.__get(url)
        if data is None or not is_iteratable(data):
            return []
        else:
            return [Location.from_dict(location) for location in data]

    async def get_rooms(self, location_id: string) -> List[Room]:
        """
        Get the rooms for a given location.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :return: A list of Room objects representing the rooms.
        :rtype: List[Room]
        """
        _LOGGER.debug('Get rooms for location %s', location_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms'
        data = await self.__get(url)
        if data is None or not is_iteratable(data):
            return []
        else:
            return [Room.from_dict(room) for room in data]

    async def get_appliances(self, location_id: string, room_id: string) -> List[Appliance]:
        """
        Get a list of appliances for a given location and room.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :param room_id: ID of the room containing the appliance.
        :type room_id: str
        :return: A list of Appliance objects representing the appliances in the specified location and room.
        :rtype: List[Appliance]
        """
        _LOGGER.debug('Get appliances for location %s and room %s', location_id, room_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances'
        data = await self.__get(url)
        if data is None or not is_iteratable(data):
            return []
        else:
            appliances: List[Appliance] = []
            for appliance in data:
                try:
                    new_appliance = Appliance.from_dict(appliance)
                    appliances.append(new_appliance)
                except Exception as e:
                    _LOGGER.warning(f'Failed to get appliance information: {e}')

            return appliances


    async def get_appliance_info_raw(self, location_id: string, room_id: string, appliance_id: string) -> Dict[str, any]:
        """
        Get information about an appliance.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :param room_id: ID of the room containing the appliance.
        :type room_id: str
        :param appliance_id: ID of the appliance to get details for.
        :type appliance_id: str
        :return: The information of the appliance.
        :rtype: Dict[str, any]
        """
        _LOGGER.debug('Get appliance information for appliance %s', appliance_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}'
        return await self.__get(url)


    async def get_appliance_details_raw(self, location_id: string, room_id: string, appliance_id: string) -> Dict[str, any]:
        """
        Get information about an appliance without parsing it to a struct.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :param room_id: ID of the room containing the appliance.
        :type room_id: str
        :param appliance_id: ID of the appliance to get details for.
        :type appliance_id: str
        :return: The information of the appliance.
        :rtype: Dict[str, any]
        """
        _LOGGER.debug('Get appliance details for appliance (type insensitive) %s', appliance_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/details'
        return await self.__get(url)


    async def get_appliance_status_raw(self, location_id: string, room_id: string, appliance_id: string) -> Dict[str, any]:
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/status'
        return await self.__get(url)

    async def get_appliance_command_raw(self, location_id: string, room_id: string, appliance_id: string) -> Dict[str, any]:
        """
        Get possible commands for an appliance.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :param room_id: ID of the room containing the appliance.
        :type room_id: str
        :param appliance_id: ID of the appliance to get details for.
        :type appliance_id: str
        :return: The command for the specified appliance.
        :rtype: Dict[str, any]
        """
        _LOGGER.debug('Get appliance command for appliance %s', appliance_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/command'
        return await self.__get(url)


    async def get_appliance_notifications_raw(self, location_id: string, room_id: string,
                                              appliance_id: string, limit: Optional[int] = None) -> Dict[str, any]:

        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/notifications'

        params = dict()

        if limit is not None:
            params.update({'pageSize': limit})

        if params:
            url += '?' + urllib.parse.urlencode(params)

        data = await self.__get(url)
        return data

    async def get_appliance_data_raw(self, location_id: string, room_id: string, appliance_id: string,
                                 from_date: Optional[datetime] = None, to_date: Optional[datetime] = None,
                                 group_by: Optional[OndusGroupByTypes] = None,
                                 date_as_full_day: Optional[bool] = None) -> Dict[str, any]:

        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/data/aggregated'
        params = dict()

        if from_date is not None:
            if date_as_full_day:
                params.update({'from': from_date.date()})
            else:
                params.update({'from': from_date.strftime('%Y-%m-%dT%H:%M:%S%z')})
        if to_date is not None:
            if date_as_full_day:
                params.update({'to': to_date.date()})
            else:
                params.update({'to': to_date.strftime('%Y-%m-%dT%H:%M:%S%z')})
        if group_by is not None:
            params.update({'groupBy': group_by.value})

        if params:
            url += '?' + urllib.parse.urlencode(params)

        return await self.__get(url)


    async def set_appliance_command_raw(self, location_id: string, room_id: string, appliance_id: string, device_type: GroheTypes, data: Dict[str, any]) -> Dict[str, any]:
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/command'
        data['type'] = device_type.value
        return await self.__post(url, data)


    async def start_pressure_measurement(self, location_id: string, room_id: string,
                                         appliance_id: string) -> PressureMeasurementStart | None:
        """
        This method sets the command for a specific appliance. It takes the location ID, room ID, appliance ID,
        command, and value as parameters.

        :param location_id: ID of the location containing the appliance.
        :type location_id: str
        :param room_id: ID of the room containing the appliance.
        :type room_id: str
        :param appliance_id: ID of the appliance to get details for.
        :type appliance_id: str
        :return: None
        """
        _LOGGER.debug('Start pressure measurement for appliance %s',appliance_id)
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/pressuremeasurement'

        response = await self.__post(url, None)

        if response is not None:
            return PressureMeasurementStart.from_dict(response)
        else:
            return None

    async def get_appliance_pressure_measurement_raw(self, location_id: string, room_id: string,
                                                     appliance_id: string) -> Dict[str, any]:
        url = f'{self.__api_url}/locations/{location_id}/rooms/{room_id}/appliances/{appliance_id}/pressuremeasurement'
        data = await self.__get(url)
        return data


    async def get_profile_notifications_raw(self, page_size: int = 50) -> Dict[str, any]:
        url = f'{self.__api_url}/profile/notifications?pageSize={page_size}'
        data = await self.__get(url)
        return data


    async def update_profile_notification_state(self, notification_id: str, state: bool) -> None:
        """
            Get profile notifications.

            :param notification_id: The unique ID of the notification to update.
            :param state: Sets the state of the notification
            :return: None.
        """
        _LOGGER.debug('Set state of notification %s to %s', notification_id, state)
        url = f'{self.__api_url}/profile/notifications/{notification_id}'
        data = {'is_read': state}
        ret_val = await self.__put(url, data)
        _LOGGER.debug(f'Notification {notification_id} updated. Return value: {ret_val}')

        return None
