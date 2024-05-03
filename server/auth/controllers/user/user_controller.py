import secrets
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from uuid import UUID

from fastapi import HTTPException, Response, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from ... import crud
from ...authentication import get_password_hash, verify_password
from ...constants import ACCESS_TOKEN_EXPIRE_SECONDS, CLIENT_URL, REFRESH_TOKEN_EXPIRE_SECONDS
from ...controllers.policy import PolicyUpdater, format_permissions_for_highest_action
from ...models import Policy, User
from ...permissions.casbin_utils import get_all_action_permissions, get_contexted_enforcer
from ...schemas.user import (
    AddPolicyRequest,
    CheckPermissionRequest,
    CreateUser,
    CreateUserRequest,
    LoginUser,
    OnboardUser,
    ReadUser,
    ResetPasswordRequest,
    UpdateUserPolicyRequest,
)
from ...schemas.workspace import ReadWorkspace


def get_user(db: Session, user_email: str):
    try:
        return crud.user.get_user_by_email(db, email=user_email)
    except Exception as e:
        print("error", e)
        raise HTTPException(404, "User not found")


def login_user(db: Session, Authorize: AuthJWT, request: LoginUser):
    try:
        user = crud.user.get_user_by_email(db, email=request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email needs to be verified.",
            )
        access_token = Authorize.create_access_token(
            subject=user.email,
            expires_time=ACCESS_TOKEN_EXPIRE_SECONDS,
            user_claims={"user_id": str(user.id)},
        )
        refresh_token = Authorize.create_refresh_token(
            subject=user.email, expires_time=REFRESH_TOKEN_EXPIRE_SECONDS
        )

        workspaces = crud.workspace.get_user_workspaces(db, user_id=user.id)
        workspace = ReadWorkspace.from_orm(workspaces[0]) if len(workspaces) > 0 else None
        return {
            "user": ReadUser.from_orm(user),
            "workspace": workspace,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print("error", e)
        raise HTTPException(500, "Internal server error")


def logout_user(response: Response, Authorize: AuthJWT):
    try:
        Authorize.jwt_required()
        # Authorize.unset_jwt_cookies()
        response.delete_cookie("access_token_cookie", samesite="none", secure=True)
        response.delete_cookie("refresh_token_cookie", samesite="none", secure=True)
        return {"msg": "Successfully logout"}
    except Exception as e:
        print("error", e)
        raise HTTPException(500, "Internal server error")


def refresh_token(Authorize: AuthJWT):
    try:
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        all_claims = Authorize.get_raw_jwt()
        user_id = all_claims.get("user_id")
        new_access_token = Authorize.create_access_token(
            subject=current_user, user_claims={"user_id": user_id}
        )
        return {"msg": "Successfully refresh token", "access_token": new_access_token}
    except Exception as e:
        print("error", e)
        raise HTTPException(500, "Internal server error")


def register_user(db: Session, request: CreateUserRequest):
    try:
        hashed_password = get_password_hash(request.password)

        user_obj = CreateUser(
            name="",
            last_name="",
            company="",
            email=request.email,
            hashed_password=hashed_password,
            active=False,
        )
        crud.user.create(db, obj_in=user_obj, auto_commit=False)

        db.commit()
        return {"message": "User successfully registered"}
    except Exception as e:
        db.rollback()
        print("error", e)
        raise HTTPException(500, "Internal server error")


def verify_user(db: Session, token: str, user_id: UUID):
    # TODO: implement another way to verify user
    crud.user.get_object_by_id_or_404(db, id=user_id)


def onboard_user(db: Session, request: OnboardUser, user_id: UUID):
    user = crud.user.get_object_by_id_or_404(db, id=user_id)

    try:
        user.active = True
        user.name = request.name
        user.last_name = request.last_name
        user.company = request.company
        db.commit()

    except Exception as e:
        db.rollback()
        print("error", e)
        raise HTTPException(500, "Internal server error")

    return {"message": "User successfully onboarded"}


def add_policy(db: Session, user_id: UUID, request: AddPolicyRequest):
    try:
        for policy in request.policies:
            crud.policy.create(
                db,
                obj_in=Policy(
                    ptype="p",
                    v0=10,
                    v1=user_id,
                    v2=policy.resource,
                    v3=policy.action,
                    workspace_id=request.workspace_id,
                ),
                auto_commit=False,
            )
            db.commit()
            return {"message": "Polices successfully added"}

    except Exception as e:
        print("error", e)
        db.rollback()
        raise HTTPException(500, "Internal server error")


def remove_policy(db: Session, user_id: UUID, request: AddPolicyRequest):
    try:
        for policy in request.policies:
            db.query(Policy).filter(
                Policy.v1 == str(user_id),
                Policy.v2 == policy.resource,
                Policy.v3 == policy.action,
                Policy.workspace_id == request.workspace_id,
            ).delete()
            db.commit()
            return {"message": "Polices successfully removed"}

    except Exception as e:
        print("error", e)
        db.rollback()
        raise HTTPException(500, "Internal server error")


def get_user_permissions(db: Session, user_id: UUID, workspace_id: UUID):
    user = crud.user.get_object_by_id_or_404(db, id=user_id)
    user_role = crud.user_role.get_user_role(db, user_id=user_id, workspace_id=workspace_id)
    enforcer = get_contexted_enforcer(db, workspace_id)
    permissions = enforcer.get_filtered_policy(1, str(user.id))

    formatted_permissions = format_permissions_for_highest_action(permissions)

    formatted_user = user.__dict__
    formatted_user.pop("hashed_password")
    formatted_user.pop("active")
    formatted_user.pop("date")

    return {
        "user": formatted_user,
        "workspace_role": user_role,
        "permissions": formatted_permissions,
    }


def update_policy(db: Session, user_id: UUID, request: UpdateUserPolicyRequest):
    policy_updater = PolicyUpdater(
        db=db,
        subject_id=user_id,
        workspace_id=request.workspace_id,
        request=request,
    )
    return policy_updater.update_policy()


def get_user_workspaces(db: Session, user_id: UUID):
    workspaces = crud.workspace.get_user_workspaces(db, user_id=user_id)
    formatted_workspaces = []
    for workspace in workspaces:
        workspace_oldest_user = crud.workspace.get_oldest_user(db, workspace_id=workspace.id)
        formatted_workspaces.append(
            {
                "id": workspace.id,
                "name": workspace.name,
                "oldest_user": workspace_oldest_user,
                "role_name": workspace.role_name,
            }
        )

    return formatted_workspaces


def resend_confirmation_email(db: Session, user_email: str):
    pass


def _add_query_params(url, params):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params.update(params)
    encoded_params = urlencode(query_params, doseq=True)
    updated_url = urlunparse(parsed_url._replace(query=encoded_params))
    return updated_url


def request_reset_password(db: Session, request: ResetPasswordRequest):
    user = crud.user.get_user_by_email(db, email=request.email)
    if user:
        # Generate reset-token
        reset_token = secrets.token_urlsafe(16)
        hashed_token = get_password_hash(reset_token)
        expiry_hours = 2
        expiration_time = datetime.now() + timedelta(hours=expiry_hours)
        reset_link = f"{CLIENT_URL}/reset"
        _add_query_params(reset_link, {"email": user.email, "token": reset_token})
        crud.reset_token.create(
            db,
            obj_in={
                "hashed_token": hashed_token,
                "user_id": user.id,
                "expiration_time": expiration_time,
                "status": "valid",
            },
        )
        return {"message": "Successfully sent password reset email."}
    raise HTTPException(400, "No user associated with this email.")


def reset_password(db: Session, request: ResetPasswordRequest):
    user = crud.user.get_user_by_email(db, email=request.email)
    if not user:
        raise HTTPException(400, "No user associated with this email.")

    user_reset_token = crud.reset_token.get_latest_user_refresh_token(db, user.id)
    if not verify_password(request.reset_token, user_reset_token.hashed_token):
        raise HTTPException(403, "Incorrect reset token.")

    if user_reset_token.status != "valid":
        raise HTTPException(400, "Token is no longer valid.")

    if datetime.now() > user_reset_token.expiration_time:
        crud.reset_token.update_by_pk(db, pk=user_reset_token.id, obj_in={"status": "expired"})
        raise HTTPException(400, "Token is expired.")

    try:
        new_hashed_password = get_password_hash(request.new_password)
        crud.user.update_by_pk(
            db,
            pk=user.id,
            obj_in={"hashed_password": new_hashed_password},
            auto_commit=False,
        )
        crud.reset_token.update_by_pk(
            db, pk=user_reset_token.id, obj_in={"status": "used"}, auto_commit=False
        )
        db.commit()
        return {"message": "Successfully reset password."}

    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(500, "Failed to reset password.")


def delete_user(db: Session, user_id: UUID):
    try:
        # user = crud.user.get_object_by_id_or_404(db, id=user_id)
        crud.user.remove(db, id=user_id, auto_commit=False)
        user_owned_workspaces = crud.workspace.get_user_owned_workspaces(db, user_id=user_id)
        for workspace in user_owned_workspaces:
            crud.workspace.remove(db, id=workspace.id, auto_commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(500, "Internal server error")
    return {"message": "User successfully deleted"}


def check_permissions(db: Session, user: User, request: CheckPermissionRequest, workspace_id: UUID):
    app_id = None
    if hasattr(request, "app_id"):
        app_id = request.app_id

    permissions_dict = get_all_action_permissions(db, str(user.id), workspace_id, app_id)
    return permissions_dict
