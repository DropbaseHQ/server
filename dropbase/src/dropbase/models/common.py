from typing import Optional

from pydantic import BaseModel


class ComponentDisplayProperties(BaseModel):
    visible: Optional[bool]  # used for display rules
    message: Optional[str]
    message_type: Optional[str]
