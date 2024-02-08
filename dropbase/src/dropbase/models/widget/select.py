from typing import Annotated, Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class SelectContextProperty(ComponentDisplayProperties):
    pass


class SelectDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]

    options: Annotated[Optional[List[Dict]], PropertyCategory.default]
    default: Annotated[Optional[Any], PropertyCategory.other]

    # events
    on_change: Annotated[Optional[str], PropertyCategory.events]

    # display_rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    component_type: Literal["select"]
