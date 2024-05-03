from typing import List

from pydantic import BaseModel


class EditInfo(BaseModel):
    new: dict
    old: dict


class CellEdit(BaseModel):
    edits: List[EditInfo]
