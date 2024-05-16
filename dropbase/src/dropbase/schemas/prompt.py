# from typing import List, Optional, Union
from pydantic import BaseModel


class Prompt(BaseModel):
    prompt: str
    method: str
    app_name: str
    page_name: str
