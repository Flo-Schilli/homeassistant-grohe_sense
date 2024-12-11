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


@dataclass_json
@dataclass
class DeviceDto:
    type: str
    sensors: List[SensorDto]


@dataclass_json
@dataclass
class DevicesDto:
    device: DeviceDto


@dataclass_json
@dataclass
class ConfigDto:
    devices: DevicesDto