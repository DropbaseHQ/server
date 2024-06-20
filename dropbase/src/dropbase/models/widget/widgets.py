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

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    # children
    components: Annotated[
        List[Union[ButtonProperty, InputProperty, SelectProperty, TextProperty, BooleanProperty]],
        PropertyCategory.default,
    ]

    # position
    w: Annotated[Optional[int], PropertyCategory.internal] = 1
    h: Annotated[Optional[int], PropertyCategory.internal] = 1
    x: Annotated[Optional[int], PropertyCategory.internal] = 0
    y: Annotated[Optional[int], PropertyCategory.internal] = 0

    # internal
    context: ModelMetaclass = WidgetContextProperty
