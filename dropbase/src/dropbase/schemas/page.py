from typing import List, Union

from pydantic import BaseModel

from dropbase.models.table import PgColumnDefinedProperty, PyColumnDefinedProperty, TableDefinedProperty
from dropbase.models.table.snowflake_column import SnowflakeColumnDefinedProperty
from dropbase.models.widget import (
    BooleanDefinedProperty,
    ButtonDefinedProperty,
    InputDefinedProperty,
    SelectDefinedProperty,
    TextDefinedProperty,
    WidgetDefinedProperty,
)
from dropbase.schemas.files import DataFile


class WidgetProperties(WidgetDefinedProperty):
    components: List[
        Union[
            InputDefinedProperty,
            SelectDefinedProperty,
            TextDefinedProperty,
            ButtonDefinedProperty,
            BooleanDefinedProperty,
        ]
    ]


class TableProperties(TableDefinedProperty):
    columns: List[Union[PgColumnDefinedProperty, PyColumnDefinedProperty]]


class Properties(BaseModel):
    tables: List[TableProperties]
    widgets: List[WidgetProperties]
    files: List[DataFile]


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: Properties


class CreatePageRequest(BaseModel):
    page_name: str


class RenamePageRequest(BaseModel):
    new_page_label: str
