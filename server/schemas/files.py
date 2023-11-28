from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from server.constants import FILE_NAME_REGEX


class ReadRequest(BaseModel):
    path: str


class CreateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    name: str = Field(regex=FILE_NAME_REGEX)
    type: str
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
    type: str
    source: Optional[str]


class UpdateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    name: str = Field(regex=FILE_NAME_REGEX)
    sql: str
    source: Optional[str]
    file_id: UUID
    type: str
    # file: dict


class RenameFile(BaseModel):
    page_id: str
    old_name: str = Field(regex=FILE_NAME_REGEX)
    new_name: str = Field(regex=FILE_NAME_REGEX)
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    type: str


class DeleteFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    file_name: str = Field(regex=FILE_NAME_REGEX)
    type: str
