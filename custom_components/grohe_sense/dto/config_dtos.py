from dataclasses import dataclass
from typing import List, Optional
from dataclasses_json import dataclass_json

#### NOTIFICATION.YAML #################################################################################################
@dataclass_json
@dataclass
class SubCategory:
    id: int
    text: str


@dataclass_json
@dataclass
class Notification:
    category: int
    type: str
    sub_category: List[SubCategory]


@dataclass_json
@dataclass
class NotificationsConfig:
    notifications: List[Notification]


#### CONFIG.YAML #######################################################################################################
@dataclass_json
@dataclass
class Sensor:
    name: str
    keypath: str
    device_class: Optional[str] = None  # Optional since `Notification` doesn't have it
    unit: Optional[str] = None  # Optional since `Notification` doesn't have it


@dataclass_json
@dataclass
class Device:
    type: str
    sensors: List[Sensor]


@dataclass_json
@dataclass
class Devices:
    device: Device


@dataclass_json
@dataclass
class Config:
    devices: Devices