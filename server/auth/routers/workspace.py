from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..authorization import ACTIONS, RESOURCES, AuthZDepFactory
from ..connect import get_db
from ..controllers import workspace as workspace_controller
from ..schemas.workspace import AddUserRequest, RemoveUserRequest, UpdateUserRoleRequest

workspace_authorizer = AuthZDepFactory(default_resource_type=RESOURCES.WORKSPACE)

router = APIRouter(
    prefix="/workspace_control",
    tags=["workspace_control"],
    dependencies=[Depends(workspace_authorizer)],
)


@router.get("/{workspace_id}/users/")
def get_workspace_users(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.get_workspace_users(db, workspace_id=workspace_id)


@router.get("/{workspace_id}/groups")
def get_workspace_groups(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.get_workspace_groups(db, workspace_id=workspace_id)


@router.post(
    "/{workspace_id}/add_user",
    dependencies=[
        Depends(workspace_authorizer.use_params(resource_type=RESOURCES.WORKSPACE, action=ACTIONS.OWN))
    ],
)
def add_user_to_workspace(workspace_id: UUID, request: AddUserRequest, db: Session = Depends(get_db)):
    return workspace_controller.add_user_to_workspace(
        db, workspace_id, request.user_email, request.role_id
    )


@router.post(
    "/{workspace_id}/remove_user",
    dependencies=[
        Depends(workspace_authorizer.use_params(resource_type=RESOURCES.WORKSPACE, action=ACTIONS.OWN))
    ],
)
def remove_user_from_workspace(
    workspace_id: UUID, request: RemoveUserRequest, db: Session = Depends(get_db)
):
    return workspace_controller.remove_user_from_workspace(db, workspace_id, request.user_id)


@router.put(
    "/{workspace_id}/user_role",
    dependencies=[
        Depends(workspace_authorizer.use_params(resource_type=RESOURCES.WORKSPACE, action=ACTIONS.OWN))
    ],
)
def update_user_role_in_workspace(
    workspace_id: UUID, request: UpdateUserRoleRequest, db: Session = Depends(get_db)
):
    return workspace_controller.update_user_role_in_workspace(db, workspace_id, request)


@router.delete(
    "/{workspace_id}",
    dependencies=[
        Depends(workspace_authorizer.use_params(resource_type=RESOURCES.WORKSPACE, action=ACTIONS.OWN))
    ],
)
def delete_workspace(workspace_id: UUID, db: Session = Depends(get_db)):
    return workspace_controller.delete_workspace(db, workspace_id)
