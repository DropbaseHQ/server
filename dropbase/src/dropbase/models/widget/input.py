from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties, OnEvent


class InputContextProperty(ComponentDisplayProperties):
    pass


class InputDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    data_type: Annotated[
        Literal["text", "integer", "float", "datetime", "date", "time"], PropertyCategory.default
    ]
    placeholder: Annotated[Optional[str], PropertyCategory.default]
    default: Annotated[Optional[Any], PropertyCategory.default]
    multiline: Annotated[Optional[bool], PropertyCategory.default] = False

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # events
    on_change: Annotated[Optional[OnEvent], PropertyCategory.events]

    # internal
    component_type: Literal["input"]

    def __init__(self, **data):
        data.setdefault("data_type", "text")
        super().__init__(**data)
