from typing import Annotated, Literal, Optional

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import ColumnProperty

color_options = Literal["red", "blue", "green", "yellow", "gray", "orange", "purple", "pink"]


class ButtonColumnProperty(BaseModel):
    column_type: Literal["button_column"] = "button_column"

    # general
    name: Annotated[str, PropertyCategory.default]
    label: Annotated[str, PropertyCategory.default]
    color: Annotated[Optional[color_options], PropertyCategory.default] = "blue"
    hidden: Annotated[bool, PropertyCategory.default] = False

    # internal
    context: ModelMetaclass = ColumnProperty
