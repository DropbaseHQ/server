from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, root_validator

from dropbase.models.category import PropertyCategory


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]  # used for display rules
    message: Optional[str]
    message_type: Optional[str]


class IntType(BaseModel):
    config_type: Annotated[Literal["int"], PropertyCategory.internal] = "int"


class CurrencyType(BaseModel):
    config_type: Annotated[Literal["currency"], PropertyCategory.internal] = "currency"
    symbol: Optional[str]
    # precision: Optional[int]


class WeightType(BaseModel):
    config_type: Annotated[Literal["weight"], PropertyCategory.internal] = "weight"
    unit: Optional[str]


class IntegerTypes(BaseModel):
    int: Optional[IntType]
    currency: Optional[CurrencyType]
    weight: Optional[WeightType]


class TextType(BaseModel):
    config_type: Annotated[Literal["text"], PropertyCategory.internal] = "text"


class SelectType(BaseModel):
    config_type: Annotated[Literal["select"], PropertyCategory.internal] = "select"
    options: Optional[list]
    multiple: Optional[bool]


class TextTypes(BaseModel):
    text: Optional[TextType]
    select: Optional[SelectType]


class ArrayType(BaseModel):
    config_type: Annotated[Literal["array"], PropertyCategory.internal] = "array"
    display_as: Optional[Literal["tags", "area", "bar"]] = "tags"


class ArrayTypes(BaseModel):
    array: Optional[ArrayType]


class DisplayTypeConfigurations(BaseModel):
    integer: Optional[IntegerTypes]
    text: Optional[TextTypes]
    array: Optional[ArrayTypes]


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
        Optional[Union[IntegerTypes, TextTypes, ArrayTypes]], PropertyCategory.default
    ]

    @root_validator
    def check_configurations(cls, values):
        display_type, configurations = values.get("display_type"), values.get("configurations")
        if display_type == DisplayType.currency and not isinstance(configurations, CurrencyType):
            raise ValueError("Configurations for 'currency' must be a CurrencyType instance")
        if display_type == DisplayType.select and not isinstance(configurations, SelectType):
            raise ValueError("configurations for 'datetime' must be a DatetimeType instance")
        return values
