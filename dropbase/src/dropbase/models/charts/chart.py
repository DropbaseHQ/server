from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.charts.bar import Bar


class ChartContextProperty(BaseModel):
    data: Optional[Any]
    message: Optional[str]
    message_type: Optional[str]


class ChartProperty(BaseModel):
    block_type: Literal["chart"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    options: Union[Bar]

    # position
    w: Annotated[Optional[int], PropertyCategory.internal] = 1
    h: Annotated[Optional[int], PropertyCategory.internal] = 1
    x: Annotated[Optional[int], PropertyCategory.internal] = 0
    y: Annotated[Optional[int], PropertyCategory.internal] = 0

    # internal
    context: ModelMetaclass = ChartContextProperty
