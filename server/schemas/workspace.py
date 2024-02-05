from pydantic import BaseModel, Field

from server.constants import FILE_NAME_REGEX


class CreateAppRequest(BaseModel):
    app_name: str
    workspace_id: str


class RenameAppRequest(BaseModel):
    old_name: str = Field(regex=FILE_NAME_REGEX)
    new_name: str = Field(regex=FILE_NAME_REGEX)
