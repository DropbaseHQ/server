from typing import Literal

from pydantic import BaseModel


class XAxis(BaseModel):
    type: Literal["category"]


class YAxis(BaseModel):
    type: Literal["value"]


class Series(BaseModel):
    type: Literal["bar"]


class Bar(BaseModel):
    chart_type: Literal["bar"]
    xAxis: XAxis
    yAxis: YAxis
    series: Series
