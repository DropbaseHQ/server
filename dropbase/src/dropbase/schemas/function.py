from pydantic import BaseModel


class RunFunction(BaseModel):
    app_name: str
    page_name: str
    function_name: str
    state: dict
