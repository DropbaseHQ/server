from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...controllers.user.workspace_creator import WorkspaceCreator

from ... import crud
from ...models import Policy, User, Workspace
from ...schemas import (
    UpdateUserRoleRequest,
    SyncStructureRequest,
    SyncAppRequest,
    CreateWorkspaceRequest,
)


def get_workspace_users(db, workspace_id):
    workspace_users = crud.workspace.get_workspace_users(db, workspace_id)
    formatted_users = []
    for workspace_user in workspace_users:
        user_workspace_groups = crud.user_group.get_user_workspace_groups(
            db=db, user_id=workspace_user.id, workspace_id=workspace_id
        )
        workspace_users_dict = dict(workspace_user)
        workspace_users_dict["groups"] = user_workspace_groups
        formatted_users.append(workspace_users_dict)
    return formatted_users


def get_workspace_groups(db, workspace_id):
    workspace_group = crud.workspace.get_workspace_groups(db, workspace_id)
    return workspace_group


def add_user_to_workspace(db, workspace_id, user_email, role_id):
    try:
        user = crud.user.get_user_by_email(db, user_email)
        if not user:
            raise Exception("User does not exist")
        workspace_user = crud.user_role.create(
            db,
            obj_in={
                "user_id": user.id,
                "workspace_id": workspace_id,
                "role_id": role_id,
            },
            auto_commit=False,
        )

        target_role = crud.role.get_object_by_id_or_404(db, id=role_id)
        crud.policy.create(
            db,
            obj_in={
                "ptype": "g",
                "v0": user.id,
                "v1": target_role.name,
                "workspace_id": workspace_id,
            },
            auto_commit=False,
        )
        db.commit()
        return workspace_user
    except Exception as e:
        db.rollback()
        raise e


def remove_user_from_workspace(db, workspace_id, user_id):
    try:
        user = crud.user.get_object_by_id_or_404(db, id=user_id)
        if not user:
            raise Exception("User does not exist")
        user_role = crud.user_role.get_user_user_role(
            db, user_id=user_id, workspace_id=workspace_id
        )
        if not user_role:
            raise Exception("User does not belong to the workspace")

        # Remove user from workspace user roles table
        crud.user_role.remove(db, id=user_role.id, auto_commit=False)

        # Remove specific workspace user permissions from policy table
        db.query(Policy).filter(Policy.ptype == "p", Policy.v1 == str(user.id)).filter(
            Policy.workspace_id == str(workspace_id)
        ).delete()

        user_workspace_groups = crud.user_group.get_user_workspace_user_groups(
            db, user_id=user_id, workspace_id=workspace_id
        )

        for user_group in user_workspace_groups:
            # Remove user from workspace user groups table
            crud.user_group.remove(db, id=user_group.id, auto_commit=False)

        # Remove policy inheritance from user for workspace
        db.query(Policy).filter(Policy.ptype == "g", Policy.v0 == str(user.id)).filter(
            Policy.workspace_id == str(workspace_id)
        ).delete()

        db.commit()
        return {"message": "User removed from workspace"}
    except Exception as e:
        db.rollback()
        raise e


def update_user_role_in_workspace(
    db: Session, workspace_id: UUID, request: UpdateUserRoleRequest
):
    try:
        # Update user role in user role table
        user_role = crud.user_role.get_user_user_role(
            db=db, user_id=request.user_id, workspace_id=workspace_id
        )
        old_role_name = user_role.name
        crud.user_role.update_by_pk(
            db, pk=user_role.id, obj_in={"role_id": request.role_id}, auto_commit=False
        )

        role = crud.role.get(db, id=request.role_id)
        # Update user role in policy table
        db.query(Policy).filter(
            Policy.ptype == "g",
            Policy.v0 == str(request.user_id),
            Policy.v1 == old_role_name,
        ).filter(Policy.workspace_id == str(workspace_id)).update(
            {"v1": str(role.name)}
        )

        db.commit()

    except Exception as e:
        db.rollback()
        raise e


def delete_workspace(db: Session, workspace_id: UUID):
    try:
        crud.workspace.remove(db, id=workspace_id, auto_commit=False)
        db.commit()
        return {"message": "Workspace deleted"}
    except Exception as e:
        db.rollback()
        raise e


def sync_structure(db: Session, request: SyncStructureRequest, workspace: Workspace):
    structure_report = {"apps_with_id": {}, "apps_without_id": []}

    for app in request.apps:
        target_app = crud.app.get(db, id=app.id)
        if not target_app:
            app_by_name = crud.app.get_app_by_name(
                db=db, app_name=app.name, workspace_id=workspace.id
            )
            if not app_by_name:
                structure_report["apps_without_id"].append(
                    {
                        "status": "NOT_FOUND",
                        "message": f"App with id {app.id} not found. No app with name {app.name} found either.",  # noqa
                    }
                )
            else:
                structure_report["apps_without_id"].append(
                    {
                        "status": "ID_NOT_FOUND_NAME_FOUND",
                        "message": f"App with id {app.id} not found. App with name {app.name} found. Suggest resyncing.",  # noqa
                        "name": app.name,
                    }
                )
            continue

        if target_app.name != app.name:
            crud.app.update_by_pk(db, pk=target_app.id, obj_in={"name": app.name})
            structure_report["apps_with_id"][app.id] = {
                "status": "UPDATED",
                "message": f"App with id {app.id} updated in database",
            }

        if target_app.label != app.label:
            crud.app.update_by_pk(db, pk=target_app.id, obj_in={"label": app.label})
            structure_report["apps_with_id"][app.id] = {
                "status": "UPDATED",
                "message": f"App with id {app.id} updated in database",
            }

        if target_app.label == app.label and target_app.name == app.name:
            structure_report["apps_with_id"][app.id] = {
                "status": "SYNCED",
                "message": f"App with id {app.id} is already synced. No changes made.",
            }

        if not app.pages:
            continue
        for page in app.pages:
            target_page = crud.page.get(db, id=page.id)
            if not target_page:
                page_by_name = crud.page.get_page_by_name(
                    db=db, page_name=page.name, app_id=app.id
                )
                if not page_by_name:
                    structure_report["apps_with_id"][app.id][page.id] = {
                        "status": "NOT_FOUND",
                        "message": f"Page with id {page.id} not found. No page with name {page.name} found either.",  # noqa
                    }
                else:
                    structure_report["apps_with_id"][app.id][page.id] = {
                        "status": "ID_NOT_FOUND_NAME_FOUND",
                        "message": f"Page with id {page.id} not found. Page with name {page.name} found. Suggest resyncing.",  # noqa
                    }
                continue

            if target_page.name != page.name:
                crud.page.update_by_pk(
                    db, pk=target_page.id, obj_in={"name": page.name}
                )
                structure_report["apps_with_id"][app.id][page.id] = {
                    "status": "UPDATED",
                    "message": f"Page with id {page.id} updated in database",
                }

            if target_page.label != page.label:
                crud.page.update_by_pk(
                    db, pk=target_page.id, obj_in={"label": page.label}
                )
                structure_report["apps_with_id"][app.id][page.id] = {
                    "status": "UPDATED",
                    "message": f"Page with id {page.id} updated in database",
                }

            if target_page.label == page.label and target_page.name == page.name:
                structure_report["apps_with_id"][app.id][page.id] = {
                    "status": "SYNCED",
                    "message": f"Page with id {page.id} is already synced. No changes made.",
                }
    return structure_report


def sync_app(db: Session, request: SyncAppRequest, workspace: Workspace):
    if not request.generate_new and request.app_name is not None:
        app = crud.app.get_app_by_name(db, request.app_name, workspace.id)
        if not app:
            return HTTPException(
                status_code=404,
                detail=f"App with name {request.app_name} not found in workspace",
            )
        return {"status": "FOUND", "app_id": app.id}
    if request.app_name is None:
        return HTTPException(status_code=400, detail="App name not provided")

    new_app = crud.app.create(
        db=db,
        obj_in={
            "name": request.app_name,
            "label": request.app_label,
            "workspace_id": workspace.id,
        },
    )
    db.flush()
    pages_info = []
    if request.pages:
        for page in request.pages:
            crud.page.create(
                db=db,
                obj_in={
                    "name": page.name,
                    "label": page.label,
                    "app_id": new_app.id,
                },
            )
            db.flush()
            pages_info.append(
                {
                    "name": page.name,
                    "id": page.id,
                }
            )

    return {"status": "CREATED", "app_id": new_app.id, "pages": pages_info}


def create_workspace(db: Session, request: CreateWorkspaceRequest, user: User):
    workspace_creator = WorkspaceCreator(db=db, user_id=user.id)
    workspace_creator.create(workspace_name=request.name)

    db.commit()

    return {"message": "Workspace created"}
