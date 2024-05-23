from typing import Annotated, Literal

from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.common import BaseColumnProperty, ColumnProperty


class PyColumnProperty(BaseColumnProperty):
    column_type: Annotated[Literal["python"], PropertyCategory.internal] = "python"

    # general
    hidden: Annotated[bool, PropertyCategory.default] = False
    editable: Annotated[bool, PropertyCategory.default] = False

    # internal
    context: ModelMetaclass = ColumnProperty
