from typing import Annotated, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ComponentDisplayProperties


class SnowflakeColumnContextProperty(ComponentDisplayProperties):
    pass


class SnowflakeColumnDefinedProperty(BaseColumnDefinedProperty):

    schema_name: Annotated[str, PropertyCategory.view_only] = None
    table_name: Annotated[str, PropertyCategory.view_only] = None
    column_name: Annotated[str, PropertyCategory.view_only] = None

    primary_key: Annotated[bool, PropertyCategory.view_only] = False
    foreign_key: Annotated[bool, PropertyCategory.view_only] = False
    default: Annotated[str, PropertyCategory.view_only] = None
    nullable: Annotated[bool, PropertyCategory.view_only] = False
    unique: Annotated[bool, PropertyCategory.view_only] = False

    edit_keys: Annotated[list, PropertyCategory.internal] = []

    # internal
    column_type: Annotated[Literal["snowflake"], PropertyCategory.internal] = "snowflake"

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
    editable: Annotated[bool, PropertyCategory.default] = False


# class SnowflakeColumnDefinedProperty(BaseColumnDefinedProperty):

#     schema_name: str = None
#     table_name: str = None
#     column_name: str = None

#     primary_key: bool = False
#     foreign_key: bool = False
#     default: str = None
#     nullable: bool = True
#     unique: bool = False

#     edit_keys: list = []

#     # internal
#     column_type: Literal["snowflake"] = "snowflake"

#     # visibility
#     hidden: bool = False
#     editable: bool = False
