import datetime
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from typing import List, Optional, Union

from homeassistant.components.persistent_notification import Notification


@dataclass_json
@dataclass
class Address:
    street: str
    city: str
    zipcode: str
    housenumber: str
    country: str
    country_code: str
    additionalInfo: str
    state: str


@dataclass_json
@dataclass
class Threshold:
    type: str
    value: int
    enabled: bool
    quantity: str


@dataclass_json
@dataclass
class Status:
    type: str
    value: int


@dataclass_json
@dataclass
class MeasurementDto:
    timestamp: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[int] = None
    flow_rate: Optional[float] = None
    pressure: Optional[float] = None
    temperature_guard: Optional[float] = None
    battery: Optional[int] = None
    # The following is for the Grohe Blue
    cleaning_count: Optional[int] = None
    date_of_cleaning: Optional[str] = None
    date_of_co2_replacement: Optional[str] = None
    date_of_filter_replacement: Optional[str] = None
    filter_change_count: Optional[int] = None
    max_idle_time: Optional[int] = None
    open_close_cycles_carbonated: Optional[int] = None
    open_close_cycles_still: Optional[int] = None
    operating_time: Optional[int] = None
    power_cut_count: Optional[int] = None
    pump_count: Optional[int] = None
    pump_running_time: Optional[int] = None
    remaining_co2: Optional[int] = None
    remaining_filter: Optional[int] = None
    time_since_last_withdrawal: Optional[int] = None
    time_since_restart: Optional[int] = None
    time_offset: Optional[int] = field(default=None, metadata=config(field_name='timeoffset'))
    water_running_time_carbonated: Optional[int] = None
    water_running_time_medium: Optional[int] = None
    water_running_time_still: Optional[int] = None
    remaining_filter_liters: Optional[int] = None
    remaining_co2_liters: Optional[int] = None

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)


@dataclass_json
@dataclass
class AverageMeasurements:
    temperature: int
    humidity: int


@dataclass_json
@dataclass
class LastWithdrawalDto:
    starttime: str
    stoptime: str
    waterconsumption: float
    maxflowrate: float


@dataclass_json
@dataclass
class DataLatest:
    measurement: MeasurementDto
    withdrawals: Optional[LastWithdrawalDto] = None
    average_monthly_consumption: Optional[float] = None
    daily_cost: Optional[float] = None
    average_daily_consumption: Optional[float] = None
    daily_consumption: Optional[float] = None


@dataclass_json
@dataclass
class PressureCurve:
    fr: float
    pr: float
    tp: int


@dataclass_json
@dataclass
class LastPressureMeasurement:
    id: str
    status: str
    estimated_time_of_completion: str
    start_time: str
    error_message: str
    leakage: Optional[bool] = None
    level: Optional[int] = None
    total_duration: Optional[int] = None
    drop_of_pressure: Optional[float] = None
    pressure_curve: Optional[List[PressureCurve]] = None

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass_json
@dataclass
class Installer:
    name: str
    email: str
    phone: str


@dataclass_json
@dataclass
class Command:
    temp_user_unlock_on: bool
    reason_for_change: int
    pressure_measurement_running: bool
    buzzer_on: bool
    buzzer_sound_profile: int
    valve_open: bool
    measure_now: bool


@dataclass_json
@dataclass
class ApplianceCommand:
    appliance_id: str
    type: int
    command: Command
    timestamp: Optional[str] = None
    commandb64: Optional[str] = None


@dataclass_json
@dataclass
class Config:
    thresholds: Optional[List[Threshold]] = None
    measurement_period: Optional[int] = None
    action_on_major_leakage: Optional[int] = None
    action_on_minor_leakage: Optional[int] = None
    action_on_micro_leakage: Optional[int] = None
    monitor_frost_alert: Optional[bool] = None
    monitor_lower_flow_limit: Optional[bool] = None
    monitor_upper_flow_limit: Optional[bool] = None
    monitor_lower_pressure_limit: Optional[bool] = None
    monitor_upper_pressure_limit: Optional[bool] = None
    monitor_lower_temperature_limit: Optional[bool] = None
    monitor_upper_temperature_limit: Optional[bool] = None
    monitor_major_leakage: Optional[bool] = None
    monitor_minor_leakage: Optional[bool] = None
    monitor_micro_leakage: Optional[bool] = None
    monitor_system_error: Optional[bool] = None
    monitor_btw_0_1_and_0_8_leakage: Optional[bool] = None
    monitor_withdrawel_amount_limit_breach: Optional[bool] = None
    detection_interval: Optional[int] = None
    impulse_ignore: Optional[int] = None
    time_ignore: Optional[int] = None
    pressure_tolerance_band: Optional[int] = None
    pressure_drop: Optional[int] = None
    detection_time: Optional[int] = None
    action_on_btw_0_1_and_0_8_leakage: Optional[int] = None
    action_on_withdrawel_amount_limit_breach: Optional[int] = None
    withdrawel_amount_limit: Optional[int] = None
    sprinkler_mode_active_monday: Optional[bool] = None
    sprinkler_mode_active_tuesday: Optional[bool] = None
    sprinkler_mode_active_wednesday: Optional[bool] = None
    sprinkler_mode_active_thursday: Optional[bool] = None
    sprinkler_mode_active_friday: Optional[bool] = None
    sprinkler_mode_active_saturday: Optional[bool] = None
    sprinkler_mode_active_sunday: Optional[bool] = None
    sprinkler_mode_start_time: Optional[int] = None
    sprinkler_mode_stop_time: Optional[int] = None
    measurement_transmission_intervall: Optional[int] = None
    measurement_transmission_intervall_offset: Optional[int] = None
    co2_type: Optional[int] = None
    hose_length: Optional[int] = None
    co2_consumption_medium: Optional[int] = None
    co2_consumption_carbonated: Optional[int] = None
    guest_mode_active: Optional[bool] = None
    auto_flush_active: Optional[bool] = None
    flush_confirmed: Optional[bool] = None
    f_parameter: Optional[int] = None
    l_parameter: Optional[int] = None
    flow_rate_still: Optional[int] = None
    flow_rate_medium: Optional[int] = None
    flow_rate_carbonated: Optional[int] = None


@dataclass_json
@dataclass
class Params:
    water_hardness: int
    carbon_hardness: int
    filter_type: int
    variant: int
    auto_flush_reminder_notif: bool
    consumables_low_notif: bool
    product_information_notif: bool


@dataclass_json
@dataclass
class Errors:
    errors_1: bool
    errors_2: bool
    errors_3: bool
    errors_4: bool
    errors_5: bool
    errors_6: bool
    errors_7: bool
    errors_8: bool
    errors_9: bool
    errors_10: bool
    errors_11: bool
    errors_12: bool
    errors_13: bool
    errors_14: bool
    errors_15: bool
    errors_16: bool
    error1_counter: int
    error2_counter: int
    error3_counter: int
    error4_counter: int
    error5_counter: int
    error6_counter: int
    error7_counter: int
    error8_counter: int
    error9_counter: int
    error10_counter: int
    error11_counter: int
    error12_counter: int
    error13_counter: int
    error14_counter: int
    error15_counter: int
    error16_counter: int


@dataclass_json
@dataclass
class State:
    start_time: int
    APPLIANCE_SUCCESSFUL_CONFIGURED: bool
    co2_empty: bool
    co2_20l_reached: bool
    filter_empty: bool
    filter_20l_reached: bool
    cleaning_mode_active: bool
    cleaning_needed: bool
    flush_confirmation_required: bool
    System_error_bitfield: int


@dataclass_json
@dataclass
class Appliance:
    id: str = field(metadata=config(field_name='appliance_id'))
    installation_date: str
    name: str
    serial_number: str
    type: int
    version: str
    tdt: str
    timezone: int
    config: Config
    role: str
    registration_complete: bool
    presharedkey: Optional[str] = None
    params: Optional[Params] = None
    error: Optional[Errors] = None
    state: Optional[State] = None
    calculate_average_since: Optional[str] = None
    pressure_notification: Optional[bool] = None
    snooze_status: Optional[str] = None
    last_pressure_measurement: Optional[LastPressureMeasurement] = None
    installer: Optional[Installer] = None
    command: Optional[Command] = None
    notifications: Optional[List[Notification]] = None
    status: Optional[List[Status]] = None
    data_latest: Optional[DataLatest] = None


@dataclass_json
@dataclass
class Room:
    id: int
    name: str
    type: int
    room_type: int
    role: str
    appliances: Optional[List[Appliance]] = None


@dataclass_json
@dataclass
class Location:
    id: int
    name: str
    type: int
    role: str
    timezone: str
    water_cost: float
    energy_cost: float
    heating_type: int
    currency: str
    default_water_cost: float
    default_energy_cost: float
    default_heating_type: int
    emergency_shutdown_enable: bool
    address: Address
    rooms: Optional[List[Room]] = None


@dataclass_json
@dataclass
class Locations:
    locations: List[Location]


@dataclass_json
@dataclass
class Notification:
    appliance_id: str
    id: str
    category: int
    is_read: bool
    timestamp: str
    type: int
    threshold_quantity: str
    threshold_type: str
    notification_text: Optional[str] = None
    notification_type: Optional[str] = None


@dataclass_json
@dataclass
class ProfileNotification:
    appliance_name: str
    room_name: str
    location_name: str
    appliance_id: str
    location_id: int
    room_id: int
    notification_id: str
    category: int
    is_read: bool
    timestamp: int
    notification_type: int


@dataclass_json
@dataclass
class ProfileNotifications:
    continuation_token: str
    remaining_notifications: int
    notifications: List[ProfileNotification]


@dataclass_json
@dataclass
class MeasurementSenseDto:
    date: str
    flow_rate: Optional[float] = field(default=None, metadata=config(field_name='flowrate'))
    pressure: Optional[float] = None
    temperature_guard: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None


@dataclass_json
@dataclass
class Withdrawal:
    date: Union[datetime, str]
    waterconsumption: float
    hotwater_share: float
    water_cost: float
    energy_cost: float


@dataclass_json
@dataclass
class Data:
    group_by: str
    measurement: Optional[List[MeasurementSenseDto]] = None
    withdrawals: Optional[List[Withdrawal]] = None


@dataclass_json
@dataclass
class MeasurementData:
    appliance_id: str
    type: int
    data: Data


@dataclass_json
@dataclass
class OndusToken:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    id_token: str
    session_state: str
    scope: str
    not_before_policy: int = field(metadata=config(field_name='not-before-policy'))
    partialLogin: Optional[bool] = None


@dataclass_json
@dataclass
class PressureMeasurementId:
    id: str


@dataclass_json
@dataclass
class PressureMeasurementStart:
    code: int
    message: str
    fields: Optional[List[PressureMeasurementId]] = None
