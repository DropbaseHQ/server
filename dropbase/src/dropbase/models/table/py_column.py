from typing import Literal

from pydantic import BaseModel

from dropbase.models.common import ComponentDisplayProperties


class PyColumnContextProperty(ComponentDisplayProperties):
    pass


class PyColumnDefinedProperty(BaseModel):
    # internal
    column_type: Literal["python"] = "python"

    # visibility
    hidden: bool = False
