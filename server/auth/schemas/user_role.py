from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BaseUserRole(BaseModel):
    user_id: UUID
    workspace_id: UUID
    role_id: str


class ReadUserRole(BaseUserRole):
    id: UUID
    date: datetime


class CreateUserRole(BaseUserRole):
    pass


class UpdateUserRole(BaseModel):
    user_id: Optional[UUID]
    workspace_id: Optional[UUID]
