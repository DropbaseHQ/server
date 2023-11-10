from typing import List

from pydantic import BaseModel


class SyncTableColumns(BaseModel):
    app_name: str
    page_name: str
    tables: List[dict]
    state: dict


class GetTableColumns(BaseModel):
    app_name: str
    page_name: str
    table: dict
    file: dict
    state: dict


class SyncComponents(BaseModel):
    app_name: str
    page_name: str
