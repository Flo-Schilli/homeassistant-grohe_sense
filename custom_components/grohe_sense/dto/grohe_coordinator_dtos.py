from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import dataclass_json, config

from custom_components.grohe_sense.dto.ondus_dtos import DataLatest


@dataclass_json
@dataclass
class LastPressureMeasurement:
    id: str
    status: str
    estimated_stop_time: str = field(metadata=config(field_name='estimated_time_of_completion'))
    start_time: str
    error_message: str
    leakage: Optional[bool] = None
    leakage_level: Optional[int] = field(metadata=config(field_name='level'),default=None)
    duration: Optional[int] = field(metadata=config(field_name='total_duration'),default=None)
    pressure_drop: Optional[float] = field(metadata=config(field_name='drop_of_pressure'),default=None)
    max_flow_rate: Optional[float] = None

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class MeasurementSenseDto:
    flow_rate: Optional[float] = None
    pressure: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass_json
@dataclass
class MeasurementBlueDto:
    cleaning_count: int
    date_of_cleaning: str
    date_of_co2_replacement: str
    date_of_filter_replacement: str
    filter_change_count: int
    max_idle_time: int
    open_close_cycles_carbonated: int
    open_close_cycles_still: int
    operating_time: int
    power_cut_count: int
    pump_count: int
    pump_running_time: int
    remaining_co2: int
    remaining_filter: int
    time_since_last_withdrawal: int
    time_since_restart: int
    time_offset: int = field(metadata=config(field_name='timeoffset'))
    water_running_time_carbonated: int
    water_running_time_medium: int
    water_running_time_still: int
    remaining_filter_liters: int
    remaining_co2_liters: int

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class CoordinatorDto:
    notification: Optional[str] = None
    measurement: Optional[MeasurementSenseDto] = None
    withdrawal: Optional[float] = None
    last_pressure_measurement: Optional[LastPressureMeasurement] = None
    latest_data: Optional[DataLatest] = None
