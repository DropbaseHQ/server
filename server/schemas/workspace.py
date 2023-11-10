from typing import Any, List, Optional

from pydantic import BaseModel

from server.schemas.table import TablesBaseProperty


class CreateAppRequest(BaseModel):
    app_id: str
    app_template: Any


class CreateTableRequest(BaseModel):
    name: Optional[str]
    property: TablesBaseProperty
    page_id: str
    depends_on: Optional[List[str]]


class DeleteAppRequest(BaseModel):
    app_name: str


class UpdateTableRequest(BaseModel):
    app_name: str
    page_name: str
    name: str
    table: dict
    state: dict
    file: dict
    page_id: str
    property: dict
    depends_on: Optional[List[str]]


class ConvertTableRequest(BaseModel):
    app_name: str
    page_name: str
    table: dict
    file: dict
    state: dict


class RenameAppRequest(BaseModel):
    old_name: str
    new_name: str
