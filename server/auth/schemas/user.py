from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str
    email: str
    hashed_password: str
    trial_eligible: bool
    active: bool

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    name: str
    last_name: Optional[str]
    company: Optional[str]
    email: str
    hashed_password: Optional[str]
    active: bool = False
    trial_eligible: bool = True
    confirmation_token: Optional[str]
    social_login: Optional[str]


class ReadUser(BaseModel):
    id: UUID
    name: str
    email: str
    active: Optional[bool]
    date: Optional[datetime]

    class Config:
        orm_mode = True


class UpdateUser(BaseModel):
    name: Optional[str]
    email: Optional[str]
    active: Optional[bool]


class LoginUser(BaseModel):
    email: str
    password: str


class LoginGoogleUser(BaseModel):
    credential: str


class CreateGoogleUserRequest(BaseModel):
    credential: str


class CreateUserRequest(BaseModel):
    email: str
    password: str


class PowerCreateUserRequest(BaseModel):
    name: str
    last_name: str
    company: str
    email: str
    password: str
    active: Optional[bool]


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str
    reset_token: str


class AddPolicy(BaseModel):
    resource: str
    action: str


class AddPolicyRequest(BaseModel):
    workspace_id: str
    policies: list[AddPolicy]


class GetUserDetails(BaseModel):
    workspace_id: str


class UpdateUserPolicyRequest(BaseModel):
    resource: str
    action: str
    workspace_id: str


class ResendConfirmationEmailRequest(BaseModel):
    email: str


class RequestResetPassword(BaseModel):
    email: str


class OnboardUser(BaseModel):
    name: str
    last_name: Optional[str]
    company: str


class CheckPermissionRequest(BaseModel):
    app_id: Optional[str]


class PageObject(BaseModel):
    name: str
    id: Optional[str]
    label: Optional[str]


class AppObject(BaseModel):
    name: str
    id: Optional[str]
    label: Optional[str]
    pages: Optional[list[PageObject]]


class SyncStructureRequest(BaseModel):
    apps: list[AppObject]


class SyncAppRequest(BaseModel):
    app_name: Optional[str] = None
    app_label: Optional[str] = None
    generate_new: bool = True
    pages: Optional[list[PageObject]] = None


class CheckAppsPermissionsRequest(BaseModel):
    app_ids: list


class CreateTestUserRequest(BaseModel):
    name: str
    last_name: str
    company: str
    email: str
    password: str
    workspace_id: str


class CreateTestDBTableRequest(BaseModel):
    name: str
    last_name: str
    password: str
