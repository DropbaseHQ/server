from pydantic import BaseModel

from server.schemas.table import FilterSort, QueryTablePayload, TableBase


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    payload: QueryTablePayload
    file: dict


class RunPythonRequest(BaseModel):
    app_name: str
    page_name: str
    file_name: str
    payload: QueryTablePayload


class RunDataFetcherStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    state: dict


class QueryPythonRequest(BaseModel):
    app_name: str
    page_name: str
    table: TableBase
    filter_sort: FilterSort
    state: dict
