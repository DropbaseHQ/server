from typing import Literal

from dropbase.models.common import BaseColumnDefinedProperty, ComponentDisplayProperties


class PyColumnContextProperty(ComponentDisplayProperties):
    pass


class PyColumnDefinedProperty(BaseColumnDefinedProperty):
    # internal
    column_type: Literal["python"] = "python"

    # visibility
    hidden: bool = False
