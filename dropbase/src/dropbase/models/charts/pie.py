from typing import Literal

from pydantic import BaseModel


class Series(BaseModel):
    type: Literal["pie"]


class Pie(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["pie"]
    series: Series
