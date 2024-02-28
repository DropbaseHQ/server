from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

from dropbase.constants import FILE_NAME_REGEX


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


class FilterSort(BaseModel):
    filters: List[Optional[TableFilter]]
    sorts: List[Optional[TableSort]]
    pagination: Optional[TablePagination]


class TableBase(BaseModel):
    name: str
    type: Optional[str]
    fetcher: Optional[str]


class ConvertTableRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    table: TableBase
    state: dict


class CommitTableColumnsRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    table: TableBase
    columns: List[dict]
