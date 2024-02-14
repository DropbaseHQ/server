from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class TextContextProperty(ComponentDisplayProperties):
    pass


class TextDefinedProperty(BaseModel):
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
    component_type: Literal["text"]
