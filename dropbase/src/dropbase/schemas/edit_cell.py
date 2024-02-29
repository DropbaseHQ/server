from typing import Any, List, Optional

from pydantic import BaseModel

from dropbase.schemas.files import DataFile


class CellProps(BaseModel):
    name: str
    schema_name: Optional[str]
    table_name: str
    column_name: str
    edit_keys: List[str]


class CellEdit(BaseModel):
    column_name: str
    data_type: str
    old_value: Any
    new_value: Any
    row: dict
    columns: List[CellProps]


class EditCellRequest(BaseModel):
    edits: List[CellEdit]
    file: DataFile
