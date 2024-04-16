from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..controllers import workspace as workspace_controller
from ..schemas.workspace import (
    AddUserRequest,
    CreateWorkspaceRequest,
    RemoveUserRequest,
    RequestCloud,
    UpdateUserRoleRequest,
    UpdateWorkspace,
    UpdateWorkspaceToken,
)
from ..authorization import RESOURCES, AuthZDepFactory, get_current_user
from ..connect import get_db

workspace_authorizer = AuthZDepFactory(default_resource_type=RESOURCES.WORKSPACE)

router = APIRouter(
    prefix="/workspace_control",
    tags=["workspace_control"],
    dependencies=[Depends(workspace_authorizer)],
)


@router.get("/{workspace_id}")
def get_workspace(workspace_id: UUID, db: Session = Depends(get_db)):
    return crud.workspace.get_object_by_id_or_404(db, id=workspace_id)


@router.get("/{workspace_id}/users/")
def get_workspace_users(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.get_workspace_users(db, workspace_id=workspace_id)


@router.get("/{workspace_id}/groups")
def get_workspace_groups(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.get_workspace_groups(db, workspace_id=workspace_id)


@router.post("/{workspace_id}/add_user")
def add_user_to_workspace(
    workspace_id: UUID, request: AddUserRequest, db: Session = Depends(get_db)
):
    return workspace_controller.add_user_to_workspace(
        db, workspace_id, request.user_email, request.role_id
    )


@router.post("/{workspace_id}/remove_user")
def remove_user_from_workspace(
    workspace_id: UUID, request: RemoveUserRequest, db: Session = Depends(get_db)
):
    return workspace_controller.remove_user_from_workspace(
        db, workspace_id, request.user_id
    )


@router.put("/{workspace_id}/user_role")
def update_user_role_in_workspace(
    workspace_id: UUID, request: UpdateUserRoleRequest, db: Session = Depends(get_db)
):
    return workspace_controller.update_user_role_in_workspace(db, workspace_id, request)


@router.put("/{workspace_id}/token")
def update_workspace_token(
    workspace_id: UUID, request: UpdateWorkspaceToken, db: Session = Depends(get_db)
):
    return workspace_controller.update_workspace_token(db, workspace_id, request)


@router.post("/")
def create_workspace(
    request: CreateWorkspaceRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return workspace_controller.create_workspace(db, request, user)


@router.put("/{workspace_id}")
def update_workspace(
    workspace_id: UUID, request: UpdateWorkspace, db: Session = Depends(get_db)
):
    return crud.workspace.update_by_pk(db, pk=workspace_id, obj_in=request)


@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.delete_workspace(db, workspace_id)


@router.post("/{workspace_id}/request_cloud")
def request_cloud(
    workspace_id: UUID,
    request: RequestCloud,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return workspace_controller.request_cloud(db, user, workspace_id, request)
