from typing import Optional

from pydantic import BaseModel


class PromptComponent(BaseModel):
    action: str
    block: str
    section: Optional[str]
    component: Optional[str]


class FuncPrompt(BaseModel):
    prompt: str
    app_name: str
    page_name: str
    component: Optional[PromptComponent]


class UIPrompt(BaseModel):
    prompt: str
    app_name: str
    page_name: str
