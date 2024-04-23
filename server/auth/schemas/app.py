from pydantic import BaseModel


class AppShareRequest(BaseModel):
    subjects: list[str]
    action: str
