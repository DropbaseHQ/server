from typing import Optional

from pydantic import BaseModel

from server.models.common import ComponentDisplayProperties


class PgColumnSharedProperty(BaseModel):
    pass


class PgColumnContextProperty(ComponentDisplayProperties, PgColumnSharedProperty):
    pass


class PgColumnBaseProperty(BaseModel):
    name: str
    type: Optional[str]

    schema_name: str = None
    table_name: str = None
    column_name: str = None

    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = True
    unique: bool = False

    edit_keys: list = []


class PgColumnDefinedProperty(PgColumnBaseProperty, PgColumnSharedProperty):
    pass