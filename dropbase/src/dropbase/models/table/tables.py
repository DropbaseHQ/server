from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory


class Filter(BaseModel):
    column_name: str
    condition: Literal["=", ">", "<", ">=", "<=", "like", "in"]
    value: Any


class Sort(BaseModel):
    column_name: str
    value: Literal["asc", "desc"]


class PinnedFilter(BaseModel):
    column_name: str
    condition: Literal["=", ">", "<", ">=", "<=", "like", "in"]


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


class TableDefinedProperty(BaseModel):
    block_type: Literal["table"] = "table"
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    # data fetcher
    fetcher: Annotated[Optional[Union[str, Dict]], PropertyCategory.default]
    widget: Annotated[Optional[str], PropertyCategory.default]

    # settings

    size: Annotated[Optional[int], PropertyCategory.default] = 10

    # actions
    # TODO: implement these
    # on_row_change: Annotated[Optional[str], PropertyCategory.events]
    # on_row_selection: Annotated[Optional[str], PropertyCategory.events]

    # table filters
    filters: Annotated[Optional[List[PinnedFilter]], PropertyCategory.other]

    # internal
    w: Annotated[Optional[int], PropertyCategory.internal] = 0
    h: Annotated[Optional[int], PropertyCategory.internal] = 0
    x: Annotated[Optional[int], PropertyCategory.internal] = 1
    y: Annotated[Optional[int], PropertyCategory.internal] = 4

    type: Optional[Literal["python", "sql"]] = "sql"
    smart: Optional[bool] = False
