from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel

from server.models.properties import PropertyCategory


# text
class TextSharedProperties(BaseModel):
    pass


class TextContextProperty(TextSharedProperties):
    pass


class TextBaseProperties(BaseModel):
    component_type: Literal["text"]
    name: Annotated[str, PropertyCategory.default]
    text: Annotated[Optional[str], PropertyCategory.default]
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


class TextDefinedProperty(TextBaseProperties, TextSharedProperties):
    pass
