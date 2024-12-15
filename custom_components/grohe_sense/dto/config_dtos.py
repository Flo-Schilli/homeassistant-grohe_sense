from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import dataclass_json

#### NOTIFICATION.YAML #################################################################################################
@dataclass_json
@dataclass
class SubCategoryDto:
    id: int
    text: str


@dataclass_json
@dataclass
class NotificationDto:
    category: int
    type: str
    sub_category: List[SubCategoryDto]


@dataclass_json
@dataclass
class NotificationsDto:
    notifications: List[NotificationDto]

    def get_notification(self, category: int, subcategory: int) -> str:
        notify_category = [cat for cat in self.notifications if cat.category == category]
        if len(notify_category) == 1:
            notify_cat = notify_category[0]
            notify_subcat = [cat for cat in notify_cat.sub_category if cat.id == subcategory]
            if len(notify_subcat) == 1:
                subcat_info = notify_subcat[0]
                return subcat_info.text
        return f'Unknown Notification {category}/{subcategory}'


#### CONFIG.YAML #######################################################################################################
@dataclass_json
@dataclass
class SensorDto:
    name: str
    keypath: str
    device_class: Optional[str] = None
    category: Optional[str] = None
    state_class: Optional[str] = None
    unit: Optional[str] = None
    enabled: Optional[bool] = True
    is_notification: Optional[bool] = False

@dataclass_json
@dataclass
class TodoDto:
    name: str
    keypath: str

@dataclass_json
@dataclass
class ValveDto:
    name: str
    keypath: str
    device_class: Optional[str] = None
    features: Optional[List[str]] = None

@dataclass_json
@dataclass
class ProfileDto:
    todos: Optional[List[TodoDto]] = None

@dataclass_json
@dataclass
class DeviceDto:
    type: str
    sensors: List[SensorDto]
    profile: Optional[ProfileDto] = None
    valves: Optional[List[ValveDto]] = None

@dataclass_json
@dataclass
class DevicesDto:
    device: List[DeviceDto]

@dataclass_json
@dataclass
class ConfigDto:
    devices: DevicesDto
    
    def get_device_config(self, device_type: str) -> Optional[DeviceDto]:
        """
        Get the configuration for a specific device type.

        :param device_type: The type of device to search for.
        :return: `DeviceDto` if found, otherwise `None`.
        """
        for device in self.devices.device:
            if device.type == device_type:
                return device
        return None