import os

import yaml

from custom_components.grohe_sense.dto.config_dtos import NotificationsConfig, Config


class ConfigLoader:
    notification_name = 'notifications.yaml'
    config_name = 'config.yaml'

    def __init__(self, path: str):
        self.path = path

    def load_notifications(self) -> NotificationsConfig:
        with open(os.path.join(self.path, self.notification_name), 'r') as file:
            yaml_data = yaml.safe_load(file)
            return NotificationsConfig.from_dict(yaml_data)

    def load_config(self) -> Config:
        with open(os.path.join(self.path, self.config_name), 'r') as file:
            yaml_data = yaml.safe_load(file)
            return Config.from_dict(yaml_data)