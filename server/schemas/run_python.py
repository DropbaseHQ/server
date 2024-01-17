from typing import Any, Dict, Optional

from pydantic import BaseModel

from server.schemas.table import FilterSort, TableBase


class QueryTablePayload(BaseModel):
    context: Dict[str, Any]
    state: Dict[str, Any]


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    payload: QueryTablePayload
    file: dict


class QueryPythonRequest(BaseModel):
    app_name: str
    page_name: str
    table: TableBase
    filter_sort: FilterSort
    state: dict
    context: Optional[dict] = None
