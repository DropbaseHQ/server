from typing import Any, Literal

from pydantic import BaseModel


class TableFilter(BaseModel):
    column_name: str
    column_type: str
    condition: Literal["=", "!=", ">", "<", ">=", "<=", "like", "in", "is null", "is not null"]
    value: Any


class TableSort(BaseModel):
    column_name: str
    value: Literal["asc", "desc"]


class TablePagination(BaseModel):
    page: int
    page_size: int
