from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BasePolicy(BaseModel):
    name: str
    workspace_id: UUID


class ReadPolicy(BasePolicy):
    pass


class CreatePolicy(BasePolicy):
    pass


class UpdatePolicy(BaseModel):
    name: Optional[str]
    workspace_id: Optional[UUID]


class PolicyTemplate(BaseModel):
    ptype: str = "p"
    resource: str = ""
    action: str = ""
    workspace_id: UUID = None
