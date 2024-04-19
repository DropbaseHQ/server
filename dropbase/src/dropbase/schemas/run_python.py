from typing import Dict, Optional, Union

from pydantic import BaseModel

from dropbase.schemas.table import FilterSort


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    state: dict
    file: dict


class RunPythonStringRequestNew(BaseModel):
    app_name: str
    page_name: str
    file_code: str
    test_code: str
    state: dict


class QueryPythonRequest(BaseModel):
    app_name: str
    page_name: str
    table_name: str
    fetcher: Union[str, Dict]
    filter_sort: Optional[FilterSort]
    state: dict
