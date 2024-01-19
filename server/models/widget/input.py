from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from server.models.category import PropertyCategory
from server.models.common import ComponentDisplayProperties


class InputBaseProperties(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    data_type: Annotated[Literal["text", "integer", "float", "date"], PropertyCategory.default]
    placeholder: Annotated[Optional[str], PropertyCategory.default]
    default: Annotated[Optional[Any], PropertyCategory.default]

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    component_type: Literal["input"]

    def __init__(self, **data):
        data.setdefault("data_type", "text")
        super().__init__(**data)


class InputSharedProperties(BaseModel):
    pass


class InputDefinedProperty(InputBaseProperties, InputSharedProperties):
    pass


class InputContextProperty(ComponentDisplayProperties, InputSharedProperties):
    pass
