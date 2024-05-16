from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentProperty

color_options = Literal["red", "blue", "green", "yellow", "gray", "orange", "purple", "pink"]


class ButtonProperty(BaseModel):
    component_type: Literal["button"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    color: Annotated[Optional[color_options], PropertyCategory.default] = "blue"

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = ComponentProperty
