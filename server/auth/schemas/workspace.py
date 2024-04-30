from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BaseWorkspace(BaseModel):
    name: str
    active: bool = True

    class Config:
        orm_mode = True


class ReadWorkspace(BaseWorkspace):
    id: UUID
    date: datetime


class CreateWorkspace(BaseWorkspace):
    pass


class UpdateWorkspace(BaseModel):
    name: Optional[str]
    active: Optional[bool]
    worker_url: Optional[str]


class AddUserRequest(BaseModel):
    user_email: str
    role_id: UUID


class RemoveUserRequest(BaseModel):
    user_id: UUID


class UpdateUserRoleRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class CreateWorkspaceRequest(BaseModel):
    name: Optional[str]
