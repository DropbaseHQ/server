from typing import Literal

from pydantic import BaseModel


class Prompt(BaseModel):
    type: Literal["function", "ui"]
    prompt: str
    app_name: str
    page_name: str
