from pydantic import BaseModel


class CreateAppRequest(BaseModel):
    name: str
    label: str
    id: str


class AppShareRequest(BaseModel):
    subjects: list[str]
    action: str
