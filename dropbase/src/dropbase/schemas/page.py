from typing import List, Optional, Union

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
        Optional[
            Union[
                InputDefinedProperty,
                SelectDefinedProperty,
                TextDefinedProperty,
                ButtonDefinedProperty,
                BooleanDefinedProperty,
            ]
        ]
    ] = []


class TableProperties(TableDefinedProperty):
    columns: List[
        Optional[
            Union[
                PgColumnDefinedProperty,
                SnowflakeColumnDefinedProperty,
                MySqlColumnDefinedProperty,
                SqliteColumnDefinedProperty,
                PyColumnDefinedProperty,
                ButtonColumnDefinedProperty,
            ]
        ]
    ] = []


class Properties(BaseModel):
    blocks: List[Union[TableProperties, WidgetProperties]]
    files: List[DataFile]


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: dict


class CreatePageRequest(BaseModel):
    app_name: str
    page_name: str
    page_label: str


class SaveTableColumnProperties(BaseModel):
    name: str
    data_type: str
    display_type: str
    column_type: str
    source_name: str
    # schema_name: Optional[str]


class SaveTableColumns(BaseModel):
    app_name: str
    page_name: str
    table_name: str
    columns: list  # TODO: Define this model (it contains name, data_type, display_type, column_type, and newly added source_name + optiona schema_name)
