from typing import Annotated, Literal

from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnProperty, ColumnProperty, ColumnTypeEnum


class SnowflakeColumnProperty(BaseColumnProperty):

    schema_name: Annotated[str, PropertyCategory.view_only] = None
    table_name: Annotated[str, PropertyCategory.view_only] = None
    column_name: Annotated[str, PropertyCategory.view_only] = None

    primary_key: Annotated[bool, PropertyCategory.view_only] = False
    foreign_key: Annotated[bool, PropertyCategory.view_only] = False
    default: Annotated[str, PropertyCategory.view_only] = None
    nullable: Annotated[bool, PropertyCategory.view_only] = False
    unique: Annotated[bool, PropertyCategory.view_only] = False

    # internal
    column_type: Annotated[
        Literal[ColumnTypeEnum.SNOWFLAKE], PropertyCategory.internal
    ] = ColumnTypeEnum.SNOWFLAKE

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
    editable: Annotated[bool, PropertyCategory.default] = False
    context: ModelMetaclass = ColumnProperty
