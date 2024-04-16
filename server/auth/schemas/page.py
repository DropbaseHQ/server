from pydantic import BaseModel


class CreatePageRequest(BaseModel):
    name: str
    label: str
    id: str
    app_id: str
