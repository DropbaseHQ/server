from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel
from pydantic.main import ModelMetaclass

from dropbase.models.category import PropertyCategory
from dropbase.models.charts.bar import BarProperty
from dropbase.models.charts.line import LineProperty
from dropbase.models.charts.pie import PieProperty
from dropbase.models.charts.scatter import ScatterProperty


class ChartContextProperty(BaseModel):
    data: Optional[Any]
    message: Optional[str]
    message_type: Optional[str]


class XAxis(BaseModel):
    type: Literal["category", "value", "time", "log"] = "category"
    data_column: Optional[str]


class YAxis(BaseModel):
    type: Literal["category", "value", "time", "log"] = "value"


# https://echarts.apache.org/en/option.html#series-bar
class ChartProperty(BaseModel):
    block_type: Literal["chart"]

    # general
    label: Annotated[str, PropertyCategory.default]
    name: Annotated[str, PropertyCategory.default]
    description: Annotated[Optional[str], PropertyCategory.default]

    xAxis: Annotated[Optional[XAxis], PropertyCategory.default]
    yAxis: Annotated[Optional[YAxis], PropertyCategory.default]

    series: List[Union[BarProperty, LineProperty, PieProperty, ScatterProperty]] = []

    # position
    w: Annotated[Optional[int], PropertyCategory.internal] = 1
    h: Annotated[Optional[int], PropertyCategory.internal] = 1
    x: Annotated[Optional[int], PropertyCategory.internal] = 0
    y: Annotated[Optional[int], PropertyCategory.internal] = 0

    # internal
    context: ModelMetaclass = ChartContextProperty
