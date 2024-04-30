from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class SelectContextProperty(ComponentDisplayProperties):
    options: Annotated[Optional[List[Dict]], PropertyCategory.default]


class SelectDefinedProperty(BaseModel):
    component_type: Literal["select"]
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]

    data_type: Annotated[
        Literal["string", "integer", "float", "boolean", "string_array"],
        PropertyCategory.default,
    ]

    options: Annotated[Optional[List[Dict]], PropertyCategory.default]

    default: Annotated[Optional[Any], PropertyCategory.other]
    multiple: Annotated[Optional[bool], PropertyCategory.other] = False

    # display_rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = SelectContextProperty

    def __init__(self, **data):
        data.setdefault("data_type", "string")
        super().__init__(**data)
