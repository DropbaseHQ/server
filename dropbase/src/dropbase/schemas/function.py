from typing import List, Optional

from pydantic import BaseModel


class RunClass(BaseModel):
    app_name: str
    page_name: str
    action: str
    resource: str
    section: Optional[str]
    component: Optional[str]
    state: dict
    edits: Optional[List[dict]]
