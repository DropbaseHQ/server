from typing import Any, List, Literal, Optional

from pydantic import BaseModel


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


class TableDisplayProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]


class TableSharedProperty(BaseModel):
    pass


class TableContextProperty(TableDisplayProperty, TableSharedProperty):
    pass


class TableBaseProperty(BaseModel):
    name: str
    type: Literal["python", "postgres"]

    # settings
    height: Optional[str]
    size: Optional[int] = 10

    # actions
    on_row_change: Optional[str]
    on_row_selection: Optional[str]

    # table filters
    filters: Optional[List[PinnedFilter]]

    # data fetcher
    fetcher: Optional[str]


class TableDefinedProperty(TableBaseProperty, TableSharedProperty):
    pass
