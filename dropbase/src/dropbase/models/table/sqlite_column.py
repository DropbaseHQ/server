from typing import Annotated, Literal

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ColumnTypeEnum, ComponentDisplayProperties


class SqliteColumnContextProperty(ComponentDisplayProperties):
    pass


class SqliteColumnDefinedProperty(BaseColumnDefinedProperty):

    # schema_name: str = None
    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    edit_keys: list = []

    # internal
    column_type: Annotated[
        Literal[ColumnTypeEnum.SQLITE], PropertyCategory.internal
    ] = ColumnTypeEnum.SQLITE

    # visibility
    hidden: bool = False
    editable: bool = False
