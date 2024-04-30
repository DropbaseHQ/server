from pydantic import BaseModel


class RunPythonStringRequest(BaseModel):
    app_name: str
    page_name: str
    python_string: str
    state: dict
    file: dict


class RunPythonStringRequestNew(BaseModel):
    app_name: str
    page_name: str
    file_code: str
    test_code: str
    state: dict
