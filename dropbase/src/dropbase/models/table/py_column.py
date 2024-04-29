from typing import Annotated, Literal

from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ColumnDisplayProperties


class PyColumnDefinedProperty(BaseColumnDefinedProperty):
    # internal
    column_type: Annotated[Literal["python"], PropertyCategory.internal] = "python"

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
    editable: Annotated[bool, PropertyCategory.default] = False

    context: ModelMetaclass = ColumnDisplayProperties
