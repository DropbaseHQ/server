from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentProperty


class BooleanProperty(BaseModel):
    component_type: Literal["boolean"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    default: Annotated[Optional[Any], PropertyCategory.default] = False
    data_type: Literal["boolean"] = "boolean"

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = ComponentProperty
