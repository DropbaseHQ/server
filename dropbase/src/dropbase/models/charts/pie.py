from typing import Literal

from pydantic import BaseModel


class PieProperty(BaseModel):
    # mabye use the same type for both
    chart_type: Literal["pie"]
    name: str
    value: str
