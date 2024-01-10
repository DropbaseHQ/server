from uuid import UUID

from pydantic import BaseModel


class RunSQLRequest(BaseModel):
    app_name: str
    page_name: str
    file_content: str
    source: str
    state: dict


class RunQueryRequest(BaseModel):
    user_sql: str
    values: dict
    source_id: UUID
    page_name: str
    tables: dict
