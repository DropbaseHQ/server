from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class TextDefinedProperty(BaseModel):
    component_type: Literal["text"]
    name: Annotated[str, PropertyCategory.default]
    text: Annotated[str, PropertyCategory.default]
    size: Annotated[Optional[Literal["small", "medium", "large"]], PropertyCategory.default]
    color: Annotated[
        Optional[
            Literal[
                "red",
                "blue",
                "green",
                "yellow",
                "black",
                "white",
                "grey",
                "orange",
                "purple",
                "pink",
            ]
        ],
        PropertyCategory.default,
    ]

    # display_rules
    display_rules: Annotated[Optional[List[Dict]], PropertyCategory.display_rules]

    # internal
    context: ModelMetaclass = ComponentDisplayProperties
