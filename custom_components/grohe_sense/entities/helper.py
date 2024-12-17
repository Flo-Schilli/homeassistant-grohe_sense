import logging
from typing import List

from homeassistant.components.valve import ValveEntityFeature
from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfVolume, UnitOfVolumeFlowRate, UnitOfPressure, \
    UnitOfTime

_LOGGER = logging.getLogger(__name__)

class Helper:
    @staticmethod
    def get_ha_units(unit: str) -> str:
        if unit == 'Celsius':
            return UnitOfTemperature.CELSIUS
        elif unit == 'Percentage':
            return PERCENTAGE
        elif unit == 'Liters':
            return UnitOfVolume.LITERS
        elif unit == 'Cubic meters':
            return UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        elif unit == 'Bar':
            return UnitOfPressure.BAR
        elif unit == 'Minutes':
            return UnitOfTime.MINUTES
        else:
            return unit

    @staticmethod
    def get_valve_features(features: List[str]) -> int:
        parsed_features: List[ValveEntityFeature] = []
        for feature in features:
            try:
                parsed = ValveEntityFeature[feature.upper()]
                parsed_features.append(parsed)
            except ValueError:
                _LOGGER.error(f'Provided feature {feature} is not a valid ValveEntityFeature from HA')

        bit_features = 0
        for parsed_feature in parsed_features:
            bit_features |= parsed_feature.value

        return bit_features