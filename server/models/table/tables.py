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
    filters: Optional[List[PinnedFilter]]
    type: Literal["python", "sql"]

    # on row change
    on_change: Optional[str]


class TableDefinedProperty(TableBaseProperty, TableSharedProperty):
    pass
