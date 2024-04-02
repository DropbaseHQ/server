from typing import Annotated, Literal, Optional

from pydantic import BaseModel

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ColumnDisplayProperties, OnEvent


class ButtonColumnContextProperty(ColumnDisplayProperties):
    pass


class ButtonColumnDefinedProperty(BaseModel):
    name: Annotated[str, PropertyCategory.default]
    column_type: Literal["button_column"] = "button_column"

    label: Annotated[str, PropertyCategory.default]
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

    # events
    on_click: Annotated[Optional[OnEvent], PropertyCategory.events]

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
