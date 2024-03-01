from typing import Annotated, Literal, Optional

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ColumnTypeEnum, ComponentDisplayProperties


class MySqlColumnContextProperty(ComponentDisplayProperties):
    pass


class MySqlColumnDefinedProperty(BaseColumnDefinedProperty):
    name: str
    column_type: Annotated[
        Literal[ColumnTypeEnum.MYSQL], PropertyCategory.internal
    ] = ColumnTypeEnum.MYSQL
    display_type: Optional[
        Literal["text", "integer", "float", "boolean", "datetime", "date", "time", "set", "blob"]
    ]

    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    edit_keys: list = []

    # visibility
    hidden: bool = False
    editable: bool = False
