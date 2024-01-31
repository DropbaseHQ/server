from typing import Any, List

from pydantic import BaseModel


class CellProps(BaseModel):
    name: str
    schema_name: str
    table_name: str
    column_name: str
    edit_keys: List[str]


class CellEdit(BaseModel):
    column_name: str
    column_type: str
    old_value: Any
    new_value: Any
    row: dict
    columns: List[CellProps]


class EditCellRequest(BaseModel):
    edits: List[CellEdit]
    file: dict
