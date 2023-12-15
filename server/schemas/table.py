from typing import Any, Dict, List, Literal, Optional

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
    id: Optional[str]
    name: str
    property: dict
    file_id: Optional[str]
    page_id: str
    depends_on: Optional[List[str]]
    # type: str
    filters: Optional[List[TableFilter]]
    sorts: Optional[List[TableSort]]


# TODO: maybe merge with TableBase
class TablesBaseProperty(BaseModel):
    # events
    on_row_change: Optional[str]
    on_row_selection: Optional[str]

    # other
    appears_after: Optional[str]
    height: Optional[str]


class QueryTablePayload(BaseModel):
    context: Dict[str, Any]
    state: Dict[str, Any]
