from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentProperty


class TextProperty(BaseModel):
    component_type: Literal["text"]

    # general
    name: Annotated[str, PropertyCategory.default]
    text: Annotated[str, PropertyCategory.default]

    # display_rules
    display_rules: Annotated[Optional[List[Dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = ComponentProperty
