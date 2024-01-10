from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from server.models.category import PropertyCategory
from server.models.common import ComponentDisplayProperties


# select
class SelectSharedProperties(BaseModel):
    value: Optional[str]
    options: Annotated[Optional[List[Dict]], PropertyCategory.default]


class SelectContextProperty(ComponentDisplayProperties, SelectSharedProperties):
    pass


class SelectBaseProperties(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    label: Annotated[Optional[str], PropertyCategory.default]

    component_type: Literal["select"]

    # events
    on_change: Annotated[Optional[str], PropertyCategory.events]

    # display_rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # other
    required: Annotated[Optional[bool], PropertyCategory.other]
    default: Annotated[Optional[Any], PropertyCategory.other]


class SelectDefinedProperty(SelectBaseProperties, SelectSharedProperties):
    pass
