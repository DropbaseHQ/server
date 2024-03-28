from typing import Annotated, Literal

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnDefinedProperty, ColumnDisplayProperties


class PyColumnContextProperty(ColumnDisplayProperties):
    pass


class PyColumnDefinedProperty(BaseColumnDefinedProperty):
    # internal
    column_type: Annotated[Literal["python"], PropertyCategory.internal] = "python"

    # visibility
    hidden: Annotated[bool, PropertyCategory.default] = False
