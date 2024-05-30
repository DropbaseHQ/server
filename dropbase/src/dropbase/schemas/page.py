from typing import List, Optional, Union

from pydantic import BaseModel

from dropbase.models.table import ButtonColumnProperty, PgColumnProperty, PyColumnProperty, TableProperty
from dropbase.models.table.mysql_column import MySqlColumnProperty
from dropbase.models.table.snowflake_column import SnowflakeColumnProperty
from dropbase.models.table.sqlite_column import SqliteColumnProperty
from dropbase.models.widget import (
    BooleanProperty,
    ButtonProperty,
    InputProperty,
    SelectProperty,
    TextProperty,
    WidgetProperty,
)


class WidgetProperties(WidgetProperty):
    components: List[
        Optional[
            Union[
                InputProperty,
                SelectProperty,
                TextProperty,
                ButtonProperty,
                BooleanProperty,
            ]
        ]
    ] = []


class TableProperties(TableProperty):
    columns: List[
        Optional[
            Union[
                PgColumnProperty,
                SnowflakeColumnProperty,
                MySqlColumnProperty,
                SqliteColumnProperty,
                PyColumnProperty,
                ButtonColumnProperty,
            ]
        ]
    ] = []


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: dict


class CreateRenamePageRequest(BaseModel):
    app_name: str
    page_name: str
    page_label: str


class SaveTableColumns(BaseModel):
    app_name: str
    page_name: str
    table_name: str
    columns: list
