from pydantic import BaseModel


class RunSQLRequest(BaseModel):
    app_name: str
    page_name: str
    file_content: str
    source: str
    state: dict
