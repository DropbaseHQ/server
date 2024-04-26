from typing import List, Optional

from pydantic import BaseModel

from dropbase.schemas.edit_cell import CellEdit


class RunFunction(BaseModel):
    app_name: str
    page_name: str
    function_name: str
    file_name: str
    state: dict


class RunClass(BaseModel):
    app_name: str
    page_name: str
    action: str
    resource: str
    component: Optional[str]
    state: dict
    edits: Optional[List[CellEdit]]
