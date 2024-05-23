from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.table.button_column import ButtonColumnProperty
from dropbase.models.table.pg_column import PgColumnProperty
from dropbase.models.table.py_column import PyColumnProperty
from dropbase.models.table.sqlite_column import SqliteColumnProperty
from dropbase.models.widget import (
    BooleanProperty,
    ButtonProperty,
    InputProperty,
    SelectProperty,
    TextProperty,
)


class TableColumn(BaseModel):
    name: str
    column_type: str
    data_type: str
    display_type: str


class TableData(BaseModel):
    type: Optional[Literal["python", "postgres", "mysql", "snowflake", "sqlite"]]
    columns: Optional[List[TableColumn]]
    data: Optional[List[List[Any]]]


class TableContextProperty(BaseModel):
    data: Optional[TableData]
    message: Optional[str]
    message_type: Optional[str]
    reload: Annotated[Optional[bool], PropertyCategory.other] = False


class TableProperty(BaseModel):
    block_type: Literal["table"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    # children
    columns: Annotated[
        List[Union[PgColumnProperty, PyColumnProperty, ButtonColumnProperty, SqliteColumnProperty]],
        PropertyCategory.default,
    ]
    header: Annotated[
        List[Union[ButtonProperty, InputProperty, SelectProperty, TextProperty, BooleanProperty]],
        PropertyCategory.default,
    ]
    footer: Annotated[
        List[Union[ButtonProperty, InputProperty, SelectProperty, TextProperty, BooleanProperty]],
        PropertyCategory.default,
    ]

    # position
    w: Annotated[Optional[int], PropertyCategory.internal] = 4
    h: Annotated[Optional[int], PropertyCategory.internal] = 1
    x: Annotated[Optional[int], PropertyCategory.internal] = 0
    y: Annotated[Optional[int], PropertyCategory.internal] = 0

    # internal
    context: ModelMetaclass = TableContextProperty
