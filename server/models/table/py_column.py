from typing import Literal, Optional

from pydantic import BaseModel

from server.models.common import ComponentDisplayProperties


class PyColumnSharedProperty(BaseModel):
    pass


class PyColumnContextProperty(ComponentDisplayProperties, PyColumnSharedProperty):
    pass


class PyColumnBaseProperty(BaseModel):
    name: str
    column_type: Optional[str]
    display_type: Optional[Literal["text", "integer", "float", "boolean", "datetime", "date", "time"]]


class PyColumnDefinedProperty(PyColumnBaseProperty, PyColumnSharedProperty):
    pass
