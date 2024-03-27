from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ValidationError, root_validator

from dropbase.models.category import PropertyCategory


class ConfigTypeEnum(str, Enum):
    INT = "int"
    CURRENCY = "currency"
    WEIGHT = "weight"
    TEXT = "text"
    SELECT = "select"
    ARRAY = "array"


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]  # used for display rules
    message: Optional[str]
    message_type: Optional[str]


class IntType(BaseModel):
    config_type: Annotated[Literal[ConfigTypeEnum.INT], PropertyCategory.internal] = ConfigTypeEnum.INT


class CurrencyType(BaseModel):
    config_type: Annotated[
        Literal[ConfigTypeEnum.CURRENCY], PropertyCategory.internal
    ] = ConfigTypeEnum.CURRENCY
    symbol: Optional[str]
    # precision: Optional[int]


class WeightType(BaseModel):
    config_type: Annotated[
        Literal[ConfigTypeEnum.WEIGHT], PropertyCategory.internal
    ] = ConfigTypeEnum.WEIGHT
    unit: Optional[str]


class IntegerTypes(BaseModel):
    integer: Optional[IntType]
    currency: Optional[CurrencyType]
    weight: Optional[WeightType]

    @root_validator
    def check_at_least_one(cls, values):
        # at least one of the fields is not None
        if not any(values.values()):
            raise ValidationError("At least one field must be provided.", IntegerTypes)
        return values


class TextType(BaseModel):
    config_type: Annotated[Literal[ConfigTypeEnum.TEXT], PropertyCategory.internal] = ConfigTypeEnum.TEXT


class SelectType(BaseModel):
    config_type: Annotated[
        Literal[ConfigTypeEnum.SELECT], PropertyCategory.internal
    ] = ConfigTypeEnum.SELECT
    options: Optional[list]
    multiple: Optional[bool]


class TextTypes(BaseModel):
    text: Optional[TextType]
    select: Optional[SelectType]

    @root_validator
    def check_at_least_one(cls, values):
        # at least one of the fields is not None
        if not any(values.values()):
            raise ValidationError("At least one field must be provided.", IntegerTypes)
        return values


class ArrayType(BaseModel):
    config_type: Annotated[
        Literal[ConfigTypeEnum.ARRAY], PropertyCategory.internal
    ] = ConfigTypeEnum.ARRAY
    display_as: Optional[Literal["tags", "area", "bar"]] = "tags"


class ArrayTypes(BaseModel):
    array: Optional[ArrayType]

    @root_validator
    def check_at_least_one(cls, values):
        # at least one of the fields is not None
        if not any(values.values()):
            raise ValidationError("At least one field must be provided.", IntegerTypes)
        return values


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
        Optional[Union[IntegerTypes, TextTypes, ArrayTypes]],
        PropertyCategory.default,  # ERROR!!! TextTypes is TAKEN AS Integer Types use ENUM
    ]

    @root_validator
    def check_configurations(cls, values):
        display_type, configurations = values.get("display_type"), values.get("configurations")
        if display_type == DisplayType.currency and not isinstance(configurations, CurrencyType):
            raise ValueError("Configurations for 'currency' must be a CurrencyType instance")
        if display_type == DisplayType.select and not isinstance(configurations, SelectType):
            raise ValueError("configurations for 'datetime' must be a DatetimeType instance")
        return values
