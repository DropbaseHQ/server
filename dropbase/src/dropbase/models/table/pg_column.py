from typing import Literal

from dropbase.models.common import BaseColumnDefinedProperty, ComponentDisplayProperties


class PgColumnContextProperty(ComponentDisplayProperties):
    pass


class PgColumnDefinedProperty(BaseColumnDefinedProperty):

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
    column_type: Literal["postgres"] = "postgres"

    # visibility
    hidden: bool = False
    editable: bool = False
