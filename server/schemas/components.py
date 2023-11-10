from typing import Optional

from pydantic import BaseModel


class CreateComponent(BaseModel):
    property: dict
    widget_id: str
    after: Optional[str]
    type: str


class UpdateComponent(BaseModel):
    property: dict
    type: str
