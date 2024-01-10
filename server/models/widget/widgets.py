from typing import Optional

from pydantic import BaseModel


# widget
class WidgetDisplayProperty(BaseModel):
    message: Optional[str]
    message_type: Optional[str]


class WidgetSharedProperty(BaseModel):
    pass


class WidgetContextProperty(WidgetDisplayProperty, WidgetSharedProperty):
    pass


class WidgetBaseProperty(BaseModel):
    name: Optional[str]
    description: Optional[str]


class WidgetDefinedProperty(WidgetBaseProperty, WidgetSharedProperty):
    pass
