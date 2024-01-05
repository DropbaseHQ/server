from typing import Optional

from pydantic import BaseModel


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]
    editable: Optional[bool]
    message: Optional[str]
    message_type: Optional[str]
