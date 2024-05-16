from typing import Optional

from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str
    app_name: str
    page_name: str
    type: str
    method: Optional[str]
