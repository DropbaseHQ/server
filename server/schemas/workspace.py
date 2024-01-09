from typing import List

from pydantic import BaseModel, Field

from server.constants import FILE_NAME_REGEX
from server.schemas.table import TableBase


class CreateAppRequest(BaseModel):
    app_name: str


class ConvertTableRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    table: dict
    file: dict
    state: dict


class CommitTableColumnsRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    table: TableBase
    columns: List[dict]


class RenameAppRequest(BaseModel):
    old_name: str = Field(regex=FILE_NAME_REGEX)
    new_name: str = Field(regex=FILE_NAME_REGEX)
