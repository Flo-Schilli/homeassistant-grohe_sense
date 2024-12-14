import logging
from typing import Dict, List

from benedict import benedict
from homeassistant.components.todo import TodoListEntity, TodoListEntityFeature, TodoItem, TodoItemStatus
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from ..interface.coordinator_interface import CoordinatorInterface
from ...dto.config_dtos import TodoDto, NotificationDto, NotificationsDto
from ...dto.grohe_device import GroheDevice


_LOGGER = logging.getLogger(__name__)


class Todo(CoordinatorEntity, TodoListEntity):
    def __init__(self, domain: str, coordinator: CoordinatorInterface, user_id: str, todo: TodoDto,
                 notification_config: NotificationsDto, initial_value: Dict[str, any] = None):
        super().__init__(coordinator)

        self._coordinator = coordinator
        self._todo = todo
        self._domain = domain
        self._user_id = user_id
        self._notification_config = notification_config
        self._list: List[TodoItem] = []
        # self.entity_id = f'{self._user_id}_{self._todo.name.lower().replace(" ", "_")}'

        # Needed for TodoEntity
        self._attr_name = f'Profile {self._todo.name}'
        self._attr_todo_items = []
        self._attr_supported_features = TodoListEntityFeature.UPDATE_TODO_ITEM | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(identifiers={(self._domain, self._user_id)},
                          name='User related data',
                          manufacturer='Grohe')

    @property
    def unique_id(self):
        return f'{self._user_id}_{self._todo.name.lower().replace(" ", "_")}'


    async def async_update(self) -> None:
        await self._coordinator.async_request_refresh()
        self._update_data()

    def _update_data(self):
        if self._todo.keypath is not None:
            _LOGGER.debug(f'Adding todo items for {self._todo.name}')
            data = benedict(self._coordinator.get_data())

            notifications = data.get(self._todo.keypath)
            todo_items: List[TodoItem] = []
            if isinstance(notifications, list):
                for notification in notifications:
                    description = (f'Notification for: {notification.get("appliance_name")} \r\n\r\n'
                                   f'Date of notification: {notification.get("timestamp")} \r\n\r\n'
                                   f'Notification category: {notification.get("category")} \r\n\r\n'
                                   f'Notification subcategory: {notification.get("notification_type")} \r\n\r\n'
                                   f'Full path: {notification.get("location_name")} - {notification.get("room_name")} - {notification.get("appliance_name")}')
                    todo_item = TodoItem(
                        self._notification_config.get_notification(notification.get('category'), notification.get('notification_type')),
                        notification.get('notification_id'),
                        TodoItemStatus.NEEDS_ACTION if notification.get('is_read') == False else TodoItemStatus.COMPLETED,
                        None,
                        description
                    )
                    todo_items.append(todo_item)

            if todo_items:
                _LOGGER.debug('Writing ToDo - Items')
                self._list = todo_items
                self._attr_todo_items = todo_items


    async def async_update_todo_item(self, item: TodoItem) -> None:
        _LOGGER.debug(f'Updating item {item.uid}')

        item_in_list =  next((search for search in self._attr_todo_items if search.uid == item.uid), None)

        if item_in_list is not None:
            item_in_list.status = item.status
            status = True if item.status == TodoItemStatus.COMPLETED else False
            await self._coordinator.update_notification(item.uid, status)
            await self._coordinator.async_request_refresh()
            self._update_data()


