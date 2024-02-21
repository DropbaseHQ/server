from typing import Annotated, Literal

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ComponentDisplayProperties


class PgColumnContextProperty(ComponentDisplayProperties):
    pass


class PgColumnDefinedProperty(BaseColumnDefinedProperty):

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
    column_type: Annotated[Literal["postgres"], PropertyCategory.internal] = "postgres"

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
    editable: Annotated[bool, PropertyCategory.default] = False
