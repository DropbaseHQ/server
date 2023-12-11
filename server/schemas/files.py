from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from server.constants import FILE_NAME_REGEX


class TypeEnum(str, Enum):
    ui = "ui"
    bananadata_fetcher = "data_fetcher"
    sql = "sql"


class ReadRequest(BaseModel):
    path: str


class CreateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    name: str = Field(regex=FILE_NAME_REGEX)
    type: TypeEnum
    page_id: str
    source: Optional[str]


class SaveSql(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    file_name: str = Field(regex=FILE_NAME_REGEX)
    sql: str


# data files
class DataFile(BaseModel):
    name: str = Field(regex=FILE_NAME_REGEX)
    type: TypeEnum
    source: Optional[str]


class UpdateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    name: str = Field(regex=FILE_NAME_REGEX)
    sql: str
    source: Optional[str]
    file_id: UUID
    type: TypeEnum
    # file: dict


class RenameFile(BaseModel):
    page_id: str
    old_name: str = Field(regex=FILE_NAME_REGEX)
    new_name: str = Field(regex=FILE_NAME_REGEX)
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    type: TypeEnum


class DeleteFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    file_name: str = Field(regex=FILE_NAME_REGEX)
    type: TypeEnum
