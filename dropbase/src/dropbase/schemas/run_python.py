from pydantic import BaseModel


class RunPythonStringRequest(BaseModel):
    code: str
    test: str
    state: dict
