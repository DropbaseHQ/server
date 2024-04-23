from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ... import crud
from ...controllers.policy import PolicyUpdater, format_permissions_for_highest_action
from ...models import Policy, User, UserGroup
from ...schemas.group import (
    AddGroupPolicyRequest,
    CreateGroup,
    RemoveGroupPolicyRequest,
    UpdateGroupPolicyRequest,
)
from ...permissions.casbin_utils import get_contexted_enforcer


class GroupController:
    """Controls group CRUD operations.
    We use a class for this because we cannot just use the crud functions for user_group.
    To allow efficient permission checking, we need to give casbin information about what a user
    inherits. This means we need to add/update/delete "g" type policies to our policy table whenever
    we add/update/delete a user_group.
    """

    @staticmethod
    def add_user(
        db: Session,
        user: User,
        group_id: str,
        user_id: str,
        role: str = "member",
        require_leader: bool = True,
    ):
        if require_leader:
            require_group_leader(db, group_id, user)
        group = crud.group.get_object_by_id_or_404(db, id=group_id)
        try:
            """
            Are there any existing user_group policies for this user
            in this workspace IN the policy table?
            """
            existing_group_policy = (
                db.query(Policy)
                .filter(
                    Policy.ptype == "g",
                    Policy.v0 == str(user_id),
                    Policy.v1 == str(group.id),
                )
                .filter(Policy.workspace_id == str(group.workspace_id))
                .one_or_none()
            )
            if not existing_group_policy:
                # If not, create one
                crud.policy.create(
                    db,
                    obj_in=Policy(
                        ptype="g",
                        v0=str(user_id),
                        v1=group.id,
                        workspace_id=group.workspace_id,
                    ),
                    auto_commit=False,
                )
            existing_user_group = (
                db.query(UserGroup)
                .filter(
                    UserGroup.user_id == str(user_id),
                    UserGroup.group_id == str(group.id),
                )
                .one_or_none()
            )
            if not existing_user_group:
                # Add the user to the group
                crud.user_group.create(
                    db,
                    obj_in={"user_id": user_id, "group_id": group_id, "role": role},
                    auto_commit=False,
                )

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def remove_user(db: Session, user: User, group_id: str, user_id: str):
        require_group_leader(db, group_id, user)

        group = crud.group.get_object_by_id_or_404(db, id=group_id)
        try:
            # Remove the user from the group in policy table
            db.query(Policy).filter(
                Policy.ptype == "g",
                Policy.v0 == str(user_id),
                Policy.v1 == str(group.id),
            ).filter(Policy.workspace_id == str(group.workspace_id)).delete()

            # Remove the user from the group in user_group table
            db.query(UserGroup).filter(
                UserGroup.user_id == str(user_id), UserGroup.group_id == str(group.id)
            ).delete()

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def add_policies(db: Session, group_id: str, request: AddGroupPolicyRequest):
        group = crud.group.get_object_by_id_or_404(db, id=group_id)
        try:
            # Add policies to policy table
            for policy in request.policies:
                crud.policy.create(
                    db,
                    obj_in=Policy(
                        ptype="p",
                        v0=10,
                        v1=group.id,
                        v2=policy.resource,
                        v3=policy.action,
                        workspace_id=group.workspace_id,
                    ),
                    auto_commit=False,
                )

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def remove_policies(db: Session, group_id: str, request: RemoveGroupPolicyRequest):
        group = crud.group.get_object_by_id_or_404(db, id=group_id)
        try:
            # Remove policies from policy table
            for policy in request.policies:
                db.query(Policy).filter(
                    Policy.v1 == str(group.id),
                    Policy.v2 == policy.resource,
                    Policy.v3 == policy.action,
                ).filter(Policy.workspace_id == str(group.workspace_id)).delete()

            db.commit()

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def update_policy(db: Session, group_id: str, request: UpdateGroupPolicyRequest):
        group = crud.group.get_object_by_id_or_404(db, id=group_id)
        policy_updater = PolicyUpdater(
            db=db,
            subject_id=group_id,
            workspace_id=group.workspace_id,
            request=request,
        )
        return policy_updater.update_policy()

    @staticmethod
    def create_group(db: Session, request: CreateGroup, user: User):
        try:
            new_group = crud.group.create(db, obj_in=request, auto_commit=False)
            db.flush()
            GroupController.add_user(
                db=db,
                user=user,
                group_id=new_group.id,
                user_id=user.id,
                role="leader",
                require_leader=False,
            )

            db.commit()
            return new_group
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def delete_group(db: Session, user: User, group_id: str):
        require_group_leader(db, group_id, user)
        try:
            # Delete user group associations
            db.query(UserGroup).filter(UserGroup.group_id == str(group_id)).delete()

            # Delete group policies
            db.query(Policy).filter(
                or_(Policy.v0 == str(group_id), Policy.v1 == str(group_id))
            ).delete()

            # Delete group
            crud.group.remove(db, id=str(group_id), auto_commit=False)

            db.commit()
        except Exception as e:
            db.rollback
            raise e

    @staticmethod
    def get_group_users(db: Session, group_id: str):
        """Returns all users in a group."""
        users = (
            db.query(User)
            .join(UserGroup, UserGroup.user_id == User.id)
            .filter(UserGroup.group_id == group_id)
            .with_entities(User.id, User.email, User.name, UserGroup.role)
            .all()
        )
        return users


def get_group(db: Session, group_id: str):
    """Returns all permissions for a group."""
    group = crud.group.get_object_by_id_or_404(db, id=group_id)
    enforcer = get_contexted_enforcer(db, group.workspace_id)
    permissions = enforcer.get_filtered_policy(1, str(group.id))

    formatted_permissions = format_permissions_for_highest_action(permissions)

    return {"group": group, "permissions": formatted_permissions}


def is_group_leader(db: Session, group_id: UUID, user: User):
    user_role = crud.user_group.get_user_role(db, user.id, group_id)
    if user_role is None:
        return False
    if user_role.role == "leader":
        return True
    return False


def require_group_leader(db: Session, group_id: UUID, user: User):
    if not is_group_leader(db, group_id, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User {user.id} is not a leader of group {group_id}",
        )
