from pydantic import BaseModel


class PageProperties(BaseModel):
    app_name: str
    page_name: str
    properties: dict
