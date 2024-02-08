from typing import Annotated, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory


class WidgetContextProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]


class WidgetDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]
    type: Annotated[Literal["base", "modal"], PropertyCategory.default] = "base"
    in_menu: Annotated[bool, PropertyCategory.default] = True
