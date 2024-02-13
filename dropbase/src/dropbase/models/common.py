from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, root_validator


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]  # used for display rules
    message: Optional[str]
    message_type: Optional[str]


class CurrencyType(BaseModel):
    symbol: str
    precision: int


class DatetimeType(BaseModel):
    format: str
    timezone: str


class DisplayType(str, Enum):
    text = "text"
    integer = "integer"
    float = "float"
    boolean = "boolean"
    datetime = "datetime"
    date = "date"
    time = "time"
    currency = "currency"


class BaseColumnDefinedProperty(BaseModel):
    name: str
    data_type: Optional[str]
    display_type: Optional[DisplayType]
    configurations: Optional[Union[CurrencyType, DatetimeType]]

    @root_validator
    def check_configurations(cls, values):
        display_type, configurations = values.get("display_type"), values.get("configurations")
        if display_type == DisplayType.currency and not isinstance(configurations, CurrencyType):
            raise ValueError("Configurations for 'currency' must be a CurrencyType instance")
        if display_type == DisplayType.datetime and not isinstance(configurations, DatetimeType):
            raise ValueError("configurations for 'datetime' must be a DatetimeType instance")
        return values
