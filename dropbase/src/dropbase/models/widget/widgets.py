from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.widget import (
    BooleanProperty,
    ButtonProperty,
    InputProperty,
    SelectProperty,
    TextProperty,
)


class WidgetContextProperty(BaseModel):
    visible: Optional[bool]
    message: Optional[str]
    message_type: Optional[str]
    components: Optional[dict] = {}


class WidgetProperty(BaseModel):
    block_type: Literal["widget"]
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]
    type: Annotated[Literal["base", "modal", "inline"], PropertyCategory.default] = "base"
    in_menu: Annotated[bool, PropertyCategory.default] = True
    context: ModelMetaclass = WidgetContextProperty
    components: Annotated[
        List[
            Union[
                ButtonProperty,
                InputProperty,
                SelectProperty,
                TextProperty,
                BooleanProperty,
            ]
        ],
        PropertyCategory.default,
    ]
