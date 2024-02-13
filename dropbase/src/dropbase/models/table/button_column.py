from typing import Annotated, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ComponentDisplayProperties


class ButtonColumnContextProperty(ComponentDisplayProperties):
    pass


class ButtonColumnDefinedProperty(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    column_type: Literal["button"] = "button"

    label: Annotated[str, PropertyCategory.default]
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
