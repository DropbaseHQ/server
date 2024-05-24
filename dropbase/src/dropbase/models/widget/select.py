from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentProperty


class SelectContextProperty(ComponentProperty):
    options: Annotated[Optional[List[Dict]], PropertyCategory.default]


data_type_options = Literal["string", "integer", "float", "boolean", "string_array"]


class SelectOptions(BaseModel):
    id: Optional[str]
    label: str
    value: Any


class SelectProperty(BaseModel):
    component_type: Literal["select"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    data_type: Annotated[data_type_options, PropertyCategory.default]
    options: Annotated[Optional[List[SelectOptions]], PropertyCategory.default]

    default: Annotated[Optional[Any], PropertyCategory.other]
    multiple: Annotated[Optional[bool], PropertyCategory.other] = False

    # display_rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = SelectContextProperty

    def __init__(self, **data):
        data.setdefault("data_type", "string")
        super().__init__(**data)
