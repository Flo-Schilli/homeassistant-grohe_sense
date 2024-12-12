from homeassistant.const import UnitOfTemperature, PERCENTAGE, UnitOfVolume, UnitOfVolumeFlowRate, UnitOfPressure, \
    UnitOfTime


class GetHaUnits:
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