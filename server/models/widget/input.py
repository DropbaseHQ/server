from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from server.models.common import ComponentDisplayProperties
from server.models.properties import PropertyCategory


class InputBaseProperties(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    label: Annotated[Optional[str], PropertyCategory.default]
    type: Annotated[Optional[Literal["text", "number", "date"]], PropertyCategory.default] = "text"
    placeholder: Annotated[Optional[str], PropertyCategory.default]

    # display rules
    display_rules: Annotated[Optional[List[str]], PropertyCategory.display_rules]

    # other
    required: Annotated[Optional[bool], PropertyCategory.other]
    default: Annotated[Optional[Any], PropertyCategory.other]


class InputSharedProperties(BaseModel):
    value: Optional[str]


class InputDefinedProperty(InputBaseProperties, InputSharedProperties):
    pass


class InputContextProperty(ComponentDisplayProperties, InputSharedProperties):
    pass
