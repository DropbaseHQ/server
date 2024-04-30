from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class ButtonDefinedProperty(BaseModel):
    component_type: Literal["button"]
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    color: Annotated[
        Optional[
            Literal[
                "red",
                "blue",
                "green",
                "yellow",
                "gray",
                "orange",
                "purple",
                "pink",
            ]
        ],
        PropertyCategory.default,
    ]

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = ComponentDisplayProperties
