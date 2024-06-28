from typing import Literal

from pydantic import BaseModel


class LineProperty(BaseModel):
    series_type: Literal["line"]
    # column name
    data_column: str
