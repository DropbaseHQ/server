from typing import Annotated, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ColumnDisplayProperties


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

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False

    # internal
    context: ModelMetaclass = ColumnDisplayProperties
