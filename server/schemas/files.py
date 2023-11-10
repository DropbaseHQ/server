from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReadRequest(BaseModel):
    path: str


class CreateFile(BaseModel):
    app_name: str
    page_name: str
    name: str
    type: str
    page_id: str
    source: Optional[str]


class SaveSql(BaseModel):
    app_name: str
    page_name: str
    file_name: str
    sql: str


# data files
class DataFile(BaseModel):
    name: str
    type: str
    source: Optional[str]


class UpdateFile(BaseModel):
    app_name: str
    page_name: str
    name: str
    sql: str
    source: Optional[str]
    file_id: UUID
    type: str
    # file: dict


class RenameFile(BaseModel):
    page_id: str
    old_name: str
    new_name: str
    app_name: str
    page_name: str
    type: str


class DeleteFile(BaseModel):
    app_name: str
    page_name: str
    file_name: str
    type: str
