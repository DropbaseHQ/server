from typing import Literal, Optional

from pydantic import BaseModel

from server.models.common import ComponentDisplayProperties


class PyColumnSharedProperty(BaseModel):
    pass


class PyColumnContextProperty(ComponentDisplayProperties, PyColumnSharedProperty):
    pass


class PyColumnBaseProperty(BaseModel):
    name: str
    type: Optional[Literal["text", "integer", "float", "boolean"]] = "text"
    original_type: Optional[str]


class PyColumnDefinedProperty(PyColumnBaseProperty, PyColumnSharedProperty):
    pass
