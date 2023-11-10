from typing import Optional

from pydantic import BaseModel


class WidgetBaseProperty(BaseModel):
    name: Optional[str]
    description: Optional[str]


class CreateWidget(BaseModel):
    name: str
    property: WidgetBaseProperty
    page_id: str


class UpdateWidget(BaseModel):
    name: Optional[str]
    property: WidgetBaseProperty


class UpdatewidgetRequest(WidgetBaseProperty):
    pass
