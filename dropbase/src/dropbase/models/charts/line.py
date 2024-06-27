from typing import Literal

from pydantic import BaseModel


class Line(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["line"]
    x_axis: str
