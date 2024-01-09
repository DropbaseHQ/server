from pydantic import BaseModel


class ColumnBase(BaseModel):
    name: str
    type: str
