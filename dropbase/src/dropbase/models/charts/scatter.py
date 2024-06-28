from typing import Literal

from pydantic import BaseModel


class ScatterProperty(BaseModel):
    series_type: Literal["scatter"]
    # column name
    x_axis: str
    y_axis: str
