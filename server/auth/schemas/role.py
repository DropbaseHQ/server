from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BaseRole(BaseModel):
    user_id: UUID
    workspace_id: UUID
    role: str


class ReadRole(BaseRole):
    id: UUID
    date: datetime


class CreateRole(BaseRole):
    pass


class UpdateRole(BaseModel):
    user_id: Optional[UUID]
    workspace_id: Optional[UUID]
