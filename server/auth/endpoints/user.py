from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from .. import crud

from ..controllers.user import get_user_permissions, user_controller
from ..models import User
from ..schemas.user import (
    AddPolicyRequest,
    CreateGoogleUserRequest,
    CreateUser,
    CreateUserRequest,
    PowerCreateUserRequest,
    LoginGoogleUser,
    LoginUser,
    OnboardUser,
    RequestResetPassword,
    ResendConfirmationEmailRequest,
    ResetPasswordRequest,
    UpdateUser,
    UpdateUserPolicyRequest,
    CheckPermissionRequest,
)
from ..authorization import (
    get_current_user,
    verify_user_id_belongs_to_current_user,
)
from ..connect import get_db

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/workspaces")
def get_user_worpsaces(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return user_controller.get_user_workspaces(db, user_id=user.id)


@router.post("/register")
def register_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    return user_controller.register_user(db, request)


@router.post("/verify")
def verify_user(token: str, user_id: UUID, db: Session = Depends(get_db)):
    return user_controller.verify_user(db, token, user_id)


@router.post("/resend_confirmation_email")
def resend_confirmation_email(
    request: ResendConfirmationEmailRequest, db: Session = Depends(get_db)
):
    return user_controller.resend_confirmation_email(db, request.email)


@router.post("/login")
def login_user(
    request: LoginUser, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()
):
    return user_controller.login_user(db, Authorize, request)


@router.delete("/logout")
def logout_user(response: Response, Authorize: AuthJWT = Depends()):
    return user_controller.logout_user(response, Authorize)


@router.post("/refresh")
def refresh_token(Authorize: AuthJWT = Depends()):
    return user_controller.refresh_token(Authorize)


@router.post("/request_reset_password")
def request_reset_password(
    request: RequestResetPassword, db: Session = Depends(get_db)
):
    return user_controller.request_reset_password(db, request)


@router.post("/reset_password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return user_controller.reset_password(db, request)


@router.post("/onboard")
def onboard_user(
    request: OnboardUser,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return user_controller.onboard_user(db, request, user.id)


@router.get("/{user_id}/details/{workspace_id}")
def get_user_details(user_id: UUID, workspace_id: UUID, db: Session = Depends(get_db)):
    # verify_user_id_belongs_to_current_user(user_id)
    return get_user_permissions(db=db, user_id=user_id, workspace_id=workspace_id)


@router.get("")
def get_user(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return crud.user.get_object_by_id_or_404(db, id=user.id)


@router.post("/")
def create_user(request: CreateUser, db: Session = Depends(get_db)):
    raise HTTPException(
        status_code=501, detail="Endpoint POST /user is not implemented"
    )


@router.put("/{user_id}")
def update_user(user_id: UUID, request: UpdateUser, db: Session = Depends(get_db)):
    verify_user_id_belongs_to_current_user(user_id)
    return crud.user.update_by_pk(db, user_id, request)


@router.delete("/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    # verify_user_id_belongs_to_current_user(user_id)
    return user_controller.delete_user(db, user_id)


@router.post("/add_policies/{user_id}")
def add_policies_to_user(
    user_id: UUID, request: AddPolicyRequest, db: Session = Depends(get_db)
):
    return user_controller.add_policy(db, user_id, request)


@router.post("/remove_policies/{user_id}")
def remove_policies_from_user(
    user_id: UUID, request: AddPolicyRequest, db: Session = Depends(get_db)
):
    return user_controller.remove_policy(db, user_id, request)


@router.post("/update_policy/{user_id}")
def update_policy_for_user(
    user_id: UUID, request: UpdateUserPolicyRequest, db: Session = Depends(get_db)
):
    return user_controller.update_policy(db, user_id, request)
