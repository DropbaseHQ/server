from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class BooleanContextProperty(ComponentDisplayProperties):
    pass


class OnToggle(BaseModel):
    type: Literal["widget", "function"] = "function"
    value: str


class BooleanDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]

    # events
    on_toggle: Annotated[Optional[OnToggle], PropertyCategory.events]

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    data_type: Literal["boolean"] = "boolean"
    component_type: Literal["boolean"]
