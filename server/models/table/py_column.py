from typing import Literal, Optional

from pydantic import BaseModel

from server.models.common import ComponentDisplayProperties


class PyColumnSharedProperty(BaseModel):
    pass


class PyColumnContextProperty(ComponentDisplayProperties, PyColumnSharedProperty):
    pass


class PyColumnBaseProperty(BaseModel):
    name: str
    type: Optional[Literal["str", "int", "float", "bool"]] = "str"


class PyColumnDefinedProperty(PyColumnBaseProperty, PyColumnSharedProperty):
    pass
