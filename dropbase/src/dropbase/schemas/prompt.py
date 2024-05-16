from typing import Literal, Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str
    app_name: str
    page_name: str
    type: Literal["ui", "function"]
    parent: Optional[str]
    method: Optional[str]
