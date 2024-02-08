from typing import Optional

from pydantic import BaseModel


class PayloadState(BaseModel):
    context: Optional[dict]
    state: Optional[dict]


class RunFunction(BaseModel):
    app_name: str
    page_name: str
    function_name: str
    payload: PayloadState
