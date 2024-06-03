from pydantic import BaseModel, Field

from dropbase.constants import FILE_NAME_REGEX


class UpdateFile(BaseModel):
    app_name: str = Field(regex=FILE_NAME_REGEX)
    page_name: str = Field(regex=FILE_NAME_REGEX)
    file_name: str = Field(regex=FILE_NAME_REGEX)
    code: str
