from pydantic import BaseModel


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
    target: str
    state: dict
