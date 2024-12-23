from enum import Enum


class OndusGroupByTypes(Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class GroheTypes(Enum):
    GROHE_SENSE = 101  # Type identifier for the battery powered water detector
    GROHE_SENSE_PLUS = 102
    GROHE_SENSE_GUARD = 103  # Type identifier for sense guard, the water guard installed on your water pipe
    GROHE_BLUE_HOME = 104
    GROHE_BLUE_PROFESSIONAL = 105


class PressureMeasurementState(Enum):
    SUCCESS = 'SUCCESS'
    START = 'START'
    START_FAILED = 'START_FAILED'
    STOP = 'STOP'

class GroheTapType(Enum):
    STILL = 1
    MEDIUM = 2
    CARBONATED = 3
