from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class BooleanDefinedProperty(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]

    default: Annotated[Optional[Any], PropertyCategory.default] = False

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    data_type: Literal["boolean"] = "boolean"
    component_type: Literal["boolean"]

    context: ModelMetaclass = ComponentDisplayProperties
