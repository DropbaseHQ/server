from typing import Any, List, Literal, Optional

from pydantic import BaseModel


class TableFilter(BaseModel):
    column_name: str
    condition: Literal["=", "!=", ">", "<", ">=", "<=", "like", "in", "is null", "is not null"]
    value: Any


class TableSort(BaseModel):
    column_name: str
    value: Literal["asc", "desc"]


class TablePagination(BaseModel):
    page: int
    page_size: int


class FilterSort(BaseModel):
    filters: List[Optional[TableFilter]]
    sorts: List[Optional[TableSort]]
    pagination: Optional[TablePagination]


class TableBase(BaseModel):
    name: str
    type: str
    fetcher: Optional[str]
