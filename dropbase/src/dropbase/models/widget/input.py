from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class InputContextProperty(ComponentDisplayProperties):
    pass


class InputDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    data_type: Annotated[
        Literal["text", "integer", "float", "datetime", "date", "time"], PropertyCategory.default
    ] = "text"
    placeholder: Annotated[Optional[str], PropertyCategory.default]
    default: Annotated[Optional[Any], PropertyCategory.default]

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    component_type: Literal["input"]
