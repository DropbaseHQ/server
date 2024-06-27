from typing import Literal

from pydantic import BaseModel


class XAxis(BaseModel):
    pass


class YAxis(BaseModel):
    pass


class Series(BaseModel):
    type: Literal["scatter"]


class Scatter(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["scatter"]
    xAxis: XAxis
    yAxis: YAxis
    series: Series
