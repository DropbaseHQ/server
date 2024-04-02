from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, root_validator

from dropbase.models.category import PropertyCategory


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]


class ColumnDisplayProperties(BaseModel):
    visible: Optional[bool]


class PageDisplayProperties(BaseModel):
    message: Optional[str]
    message_type: Optional[str]


class CurrencyType(BaseModel):
    config_type: Annotated[Literal["currency"], PropertyCategory.internal] = "currency"
    symbol: Optional[str]
    # precision: Optional[int]


class SelectType(BaseModel):
    config_type: Annotated[Literal["select"], PropertyCategory.internal] = "select"
    options: Optional[list]
    multiple: Optional[bool]


class ArrayType(BaseModel):
    config_type: Annotated[Literal["array"], PropertyCategory.internal] = "array"
    display_as: Optional[Literal["tags", "area", "bar"]] = "tags"


class DisplayTypeConfigurations(BaseModel):
    currency: Optional[CurrencyType]
    select: Optional[SelectType]
    array: Optional[ArrayType]


class DisplayType(str, Enum):
    text = "text"
    integer = "integer"
    float = "float"
    boolean = "boolean"
    datetime = "datetime"
    date = "date"
    time = "time"
    currency = "currency"
    select = "select"
    array = "array"


class ColumnTypeEnum(str, Enum):
    PG = "postgres"
    MYSQL = "mysql"
    SNOWFLAKE = "snowflake"
    SQLITE = "sqlite"
    PY = "python"
    BUTTON = "button"


class BaseColumnDefinedProperty(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    data_type: Annotated[Optional[str], PropertyCategory.default]
    display_type: Annotated[Optional[DisplayType], PropertyCategory.default]
    configurations: Annotated[
        Optional[Union[ArrayType, CurrencyType, SelectType]], PropertyCategory.default
    ]

    @root_validator
    def check_configurations(cls, values):
        display_type, configurations = values.get("display_type"), values.get("configurations")
        if display_type == DisplayType.currency and not isinstance(configurations, CurrencyType):
            raise ValueError("Configurations for 'currency' must be a CurrencyType instance")
        if display_type == DisplayType.select and not isinstance(configurations, SelectType):
            raise ValueError("configurations for 'datetime' must be a DatetimeType instance")
        return values


class OnEvent(BaseModel):
    type: Literal["widget", "table", "function"] = "function"
    value: str


class BaseContext(BaseModel):
    page: PageDisplayProperties
