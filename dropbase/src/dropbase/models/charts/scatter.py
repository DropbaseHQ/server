from typing import Literal

from pydantic import BaseModel


class Scatter(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["scatter"]
    x_axis: str
