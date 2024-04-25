from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from dropbase.constants import FILE_NAME_REGEX


class TypeEnum(str, Enum):
    sql = "sql"
    data_fetcher = "data_fetcher"
    ui = "ui"
    python = "python"


# data files
class DataFile(BaseModel):
    name: str = Field(regex=FILE_NAME_REGEX)
    function: Optional[str]
    type: TypeEnum
    source: Optional[str]
    depends_on: Optional[List[str]]


class UpdateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    file_name: str = Field(regex=FILE_NAME_REGEX)
    code: str
    source: Optional[str]
    type: TypeEnum
    depends_on: Optional[List[str]]
