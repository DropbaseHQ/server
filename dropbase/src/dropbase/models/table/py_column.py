from typing import Literal, Optional

from pydantic import BaseModel

from dropbase.models.common import ComponentDisplayProperties


class PyColumnContextProperty(ComponentDisplayProperties):
    pass


class PyColumnDefinedProperty(BaseModel):
    name: str
    column_type: Literal["python"] = "python"
    data_type: Optional[str]
    display_type: Optional[Literal["text", "integer", "float", "boolean", "datetime", "date", "time"]]

    # visibility
    hidden: bool = False
