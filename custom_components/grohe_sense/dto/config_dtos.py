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


#### CONFIG.YAML #######################################################################################################
@dataclass_json
@dataclass
class SensorDto:
    name: str
    keypath: str
    device_class: Optional[str] = None  # Optional since `Notification` doesn't have it
    category: Optional[str] = None
    unit: Optional[str] = None  # Optional since `Notification` doesn't have it
    enabled: Optional[bool] = True


@dataclass_json
@dataclass
class DeviceDto:
    type: str
    sensors: List[SensorDto]


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