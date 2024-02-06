from pydantic import BaseModel, Field
from typing import Optional
from server.constants import FILE_NAME_REGEX


class CreateAppRequest(BaseModel):
    app_name: str
    workspace_id: str


class RenameAppRequest(BaseModel):
    old_name: Optional[str] = Field(regex=FILE_NAME_REGEX)
    new_name: Optional[str] = Field(regex=FILE_NAME_REGEX)
    app_id: str
    new_label: Optional[str] = Field(regex=FILE_NAME_REGEX)
