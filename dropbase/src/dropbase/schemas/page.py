from typing import List, Union

from pydantic import BaseModel

from dropbase.models.table import (
    ButtonColumnDefinedProperty,
    PgColumnDefinedProperty,
    PyColumnDefinedProperty,
    TableDefinedProperty,
)
from dropbase.models.table.mysql_column import MySqlColumnDefinedProperty
from dropbase.models.table.snowflake_column import SnowflakeColumnDefinedProperty
from dropbase.models.table.sqlite_column import SqliteColumnDefinedProperty
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
    columns: List[
        Union[
            PgColumnDefinedProperty,
            MySqlColumnDefinedProperty,
            SnowflakeColumnDefinedProperty,
            SqliteColumnDefinedProperty,
            PyColumnDefinedProperty,
            ButtonColumnDefinedProperty,
        ]
    ]


class Properties(BaseModel):
    tables: List[TableProperties]
    widgets: List[WidgetProperties]
    files: List[DataFile]


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: Properties


class CreatePageRequest(BaseModel):
    app_name: str
    page_name: str
    page_label: str


class RenamePageRequest(BaseModel):
    new_page_label: str
