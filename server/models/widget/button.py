from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel

from server.models.category import PropertyCategory
from server.models.common import ComponentDisplayProperties


# button
class ButtonSharedProperties(BaseModel):
    pass


class ButtonContextProperty(ComponentDisplayProperties, ButtonSharedProperties):
    pass


class ButtonBaseProperties(BaseModel):
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
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

    # events
    on_click: Annotated[Optional[str], PropertyCategory.events]

    # display rules
    display_rules: Annotated[Optional[List[dict]], PropertyCategory.display_rules]

    # internal
    component_type: Literal["button"]


class ButtonDefinedProperty(ButtonBaseProperties, ButtonSharedProperties):
    pass
