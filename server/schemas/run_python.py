from pydantic import BaseModel

from server.schemas.files import DataFile
from server.schemas.table import FilterSort, QueryTablePayload


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
    filter_sort: FilterSort
    file: DataFile
    state: dict
