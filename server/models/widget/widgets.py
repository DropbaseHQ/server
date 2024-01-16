from typing import Annotated, Optional

from pydantic import BaseModel

from server.models.category import PropertyCategory


# widget
class WidgetDisplayProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]


class WidgetSharedProperty(BaseModel):
    pass


class WidgetContextProperty(WidgetDisplayProperty, WidgetSharedProperty):
    pass


class WidgetBaseProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]


class WidgetDefinedProperty(WidgetBaseProperty, WidgetSharedProperty):
    pass
