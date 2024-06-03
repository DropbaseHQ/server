from pydantic import BaseModel


class CreateAppRequest(BaseModel):
    app_label: str
    app_name: str


class RenameAppRequest(BaseModel):
    app_name: str
    new_label: str
