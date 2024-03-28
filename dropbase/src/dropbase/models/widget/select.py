from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties, OnEvent


class SelectContextProperty(ComponentDisplayProperties):
    pass


class SelectDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]

    data_type: Annotated[
        Literal["string", "integer", "float", "boolean", "string_array"],
        PropertyCategory.default,
    ]

    use_fetcher: Annotated[bool, PropertyCategory.default] = False
    options: Annotated[Optional[List[Dict]], PropertyCategory.default]
    fetcher: Annotated[str, PropertyCategory.default]
    name_column: Annotated[str, PropertyCategory.default]
    value_column: Annotated[str, PropertyCategory.default]

    default: Annotated[Optional[Any], PropertyCategory.other]
    multiple: Annotated[Optional[bool], PropertyCategory.other] = False

    # events
    on_change: Annotated[Optional[OnEvent], PropertyCategory.events]

    # display_rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    component_type: Literal["select"]

    def __init__(self, **data):
        data.setdefault("data_type", "string")
        super().__init__(**data)
