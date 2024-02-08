from typing import Any, Dict

from pydantic import BaseModel

from dropbase.schemas.table import FilterSort, TableBase


class QueryTablePayload(BaseModel):
    context: Dict[str, Any]
    state: Dict[str, Any]


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    payload: QueryTablePayload
    file: dict


class RunPythonStringRequestNew(BaseModel):
    file_code: str
    test_code: str
    state: dict
    context: dict


class QueryPythonRequest(BaseModel):
    app_name: str
    page_name: str
    table: TableBase
    filter_sort: FilterSort
    state: dict
