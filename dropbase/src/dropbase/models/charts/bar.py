from typing import Literal

from pydantic import BaseModel


class Bar(BaseModel):
    series_type: Literal["bar"]
    # column name
    data_column: str
