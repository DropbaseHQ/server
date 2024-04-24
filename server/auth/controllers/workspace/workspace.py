from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...controllers.user.workspace_creator import WorkspaceCreator

from ... import crud
from ...models import Policy, User, Workspace
from ...schemas import UpdateUserRoleRequest, CreateWorkspaceRequest


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


def create_workspace(db: Session, request: CreateWorkspaceRequest, user: User):
    workspace_creator = WorkspaceCreator(db=db, user_id=user.id)
    workspace_creator.create(workspace_name=request.name)

    db.commit()

    return {"message": "Workspace created"}
