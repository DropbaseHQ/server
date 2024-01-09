from typing import List, Optional

from pydantic import BaseModel, Field

from server.constants import FILE_NAME_REGEX
from server.schemas.table import TableBase


class CreateAppRequest(BaseModel):
    app_name: str


class DeleteAppRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)


class UpdateTables(BaseModel):
    name: Optional[str]
    property: TableBase
    file_id: Optional[str]
    depends_on: Optional[List[str]] = []


class UpdateTableRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    state: dict
    table: dict
    page_id: str
    file: Optional[dict]

    table_updates: UpdateTables


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
