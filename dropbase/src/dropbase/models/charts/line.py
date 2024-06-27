from typing import Literal

from pydantic import BaseModel


class XAxis(BaseModel):
    type: Literal["category"]


class YAxis(BaseModel):
    type: Literal["value"]


class Series(BaseModel):
    type: Literal["line"]


class Line(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["line"]
    xAxis: XAxis
    yAxis: YAxis
    series: Series
