from pydantic import BaseModel

from dropbase.schemas.files import DataFile
from dropbase.schemas.table import FilterSort


class RunSQLStringRequest(BaseModel):
    app_name: str
    page_name: str
    file_content: str
    source: str
    state: dict


class RunSQLRequestTask(BaseModel):
    app_name: str
    page_name: str
    file: DataFile
    filter_sort: FilterSort
    state: dict
