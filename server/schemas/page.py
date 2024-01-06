from typing import List, Union

from pydantic import BaseModel

from server.models.table import PgColumnDefinedProperty, PyColumnDefinedProperty, TableDefinedProperty
from server.models.widget import (
    ButtonDefinedProperty,
    InputDefinedProperty,
    SelectDefinedProperty,
    TextDefinedProperty,
    WidgetDefinedProperty,
)


class WidgetProperties(WidgetDefinedProperty):
    components: List[
        Union[InputDefinedProperty, SelectDefinedProperty, TextDefinedProperty, ButtonDefinedProperty]
    ]


class TableProperties(TableDefinedProperty):
    columns: List[Union[PgColumnDefinedProperty, PyColumnDefinedProperty]]


class Properties(BaseModel):
    tables: List[TableProperties]
    widgets: List[WidgetProperties]


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: Properties
