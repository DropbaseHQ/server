from typing import List

from pydantic import BaseModel


class SyncColumnsRequest(BaseModel):
    table_id: str
    columns: List[str]
    type: str


class SyncComponentsRequest(BaseModel):
    app_name: str
    page_name: str
    token: str
