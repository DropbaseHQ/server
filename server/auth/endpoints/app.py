from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..controllers.policy import (
    PolicyUpdater,
)
from ..permissions.casbin_utils import get_all_action_permissions
from .. import crud
from ..schemas import AppShareRequest
from ..controllers.app import filter_apps
from ..models import User
from ..authorization import get_current_user
from ..connect import get_db
from server.controllers import app as app_controller

router = APIRouter(prefix="/app", tags=["app"])


class UpdateAppRequest(BaseModel):
    resource: str
    action: str


@router.post("/{app_id}/share")
def share_app(app_id: UUID, request: AppShareRequest, db: Session = Depends(get_db)):
    target_app = crud.app.get_object_by_id_or_404(db=db, id=app_id)

    successful_changes = []
    for subject_id in request.subjects:
        policy_updater = PolicyUpdater(
            db=db,
            subject_id=subject_id,
            workspace_id=target_app.workspace_id,
            request=UpdateAppRequest(resource=str(app_id), action=request.action),
        )
        policy_updater.update_policy()
        successful_changes.append(
            {
                "subject_id": subject_id,
                "action": request.action,
                "resource": app_id,
            }
        )

    return successful_changes


@router.get("/{app_id}/has_access")
def get_app_access(app_id: UUID, db: Session = Depends(get_db)):
    app = crud.app.get_object_by_id_or_404(db=db, id=app_id)
    workspace_users = crud.workspace.get_workspace_users(
        db=db, workspace_id=app.workspace_id
    )
    workspace_groups = crud.workspace.get_workspace_groups(
        db=db, workspace_id=app.workspace_id
    )

    def get_highest_permissions_for_list(workspace_subjects):
        final_app_permissions = []
        for user in workspace_subjects:
            subject_id = str(user.id)
            permissions = get_all_action_permissions(
                db=db,
                user_id=user.id,
                workspace_id=app.workspace_id,
                app_id=str(app_id),
            )
            app_permissions = permissions.get("app_permissions")
            if app_permissions.get("own"):
                final_app_permissions.append(
                    {
                        "id": subject_id,
                        "permission": "own",
                    }
                )
                continue
            if app_permissions.get("edit"):
                final_app_permissions.append(
                    {
                        "id": subject_id,
                        "permission": "edit",
                    }
                )
                continue

            if app_permissions.get("use"):
                final_app_permissions.append(
                    {
                        "id": subject_id,
                        "permission": "use",
                    }
                )
        return final_app_permissions

    users_permissions = get_highest_permissions_for_list(workspace_users)
    groups_permissions = get_highest_permissions_for_list(workspace_groups)

    return {
        "users": users_permissions,
        "groups": groups_permissions,
    }


# Overrides the base default list endpoint
@router.get("/list/")
def get_apps(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    response = app_controller.get_workspace_apps()
    all_apps = response.get("apps")
    workspace_id = response.get("workspace_id")
    return filter_apps(db=db, apps=all_apps, workspace_id=workspace_id, user_id=user.id)
