from typing import List

from pydantic import BaseModel

from dropbase.schemas.files import DataFile


class EditInfo(BaseModel):
    new: dict
    old: dict


class CellEdit(BaseModel):
    row_edits: List[EditInfo]


class EditCellRequest(BaseModel):  # Don't use anymore
    edits: List[CellEdit]
    file: DataFile
