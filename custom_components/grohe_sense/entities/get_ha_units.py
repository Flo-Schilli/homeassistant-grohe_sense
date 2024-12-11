from homeassistant.const import UnitOfTemperature, PERCENTAGE


class GetHaUnits:
    @staticmethod
    def get_ha_units(unit: str) -> str:
        if unit == 'Celsius':
            return UnitOfTemperature.CELSIUS
        elif unit == 'Percentage':
            return PERCENTAGE