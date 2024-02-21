from typing import Literal, Optional

from pydantic import BaseModel

from dropbase.models.common import BaseColumnDefinedProperty, ComponentDisplayProperties


class SnowflakeColumnContextProperty(ComponentDisplayProperties):
    pass


class SnowflakeColumnDefinedProperty(BaseColumnDefinedProperty):

    schema_name: str = None
    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    edit_keys: list = []

    # internal
    column_type: Literal["snowflake"] = "snowflake"

    # visibility
    hidden: bool = False
    editable: bool = False
