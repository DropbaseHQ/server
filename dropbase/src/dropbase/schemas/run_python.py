from pydantic import BaseModel


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    line_number: int
    state: dict
