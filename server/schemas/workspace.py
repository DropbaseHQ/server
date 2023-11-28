from typing import Any, List, Optional

from pydantic import BaseModel, Field

from server.schemas.table import TablesBaseProperty
from server.constants import FILE_NAME_REGEX


class CreateAppRequest(BaseModel):
    app_id: str
    app_template: Any


class CreateTableRequest(BaseModel):
    name: Optional[str]
    property: TablesBaseProperty
    page_id: str
    depends_on: Optional[List[str]]


class DeleteAppRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)


class UpdateTableRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    name: str
    table: dict
    state: dict
    file: dict
    page_id: str
    property: dict
    depends_on: Optional[List[str]]


class ConvertTableRequest(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    table: dict
    file: dict
    state: dict


class RenameAppRequest(BaseModel):
    old_name: str = Field(regex=FILE_NAME_REGEX)
    new_name: str = Field(regex=FILE_NAME_REGEX)
