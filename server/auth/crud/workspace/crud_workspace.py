from typing import List
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func
from ..base import CRUDBase
from ...models import Group, Policy, Role, User, UserRole, Workspace
from ...schemas.workspace import CreateWorkspace, UpdateWorkspace


class CRUDWorkspace(CRUDBase[Workspace, CreateWorkspace, UpdateWorkspace]):
    def get_user_workspaces(self, db: Session, user_id: UUID) -> List[Workspace]:
        return (
            db.query(Workspace)
            .join(UserRole, UserRole.workspace_id == Workspace.id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(UserRole.user_id == user_id)
            .with_entities(
                Workspace.id,
                Workspace.name,
                Role.name.label("role_name"),
                Workspace.worker_url,
                Workspace.in_trial,
                Workspace.trial_end_date,
                Workspace.date,
            )
            .all()
        )

    def get_workspace_id(self, db: Session, workspace_id: UUID) -> str:
        return (db.query(Workspace.id).filter(Workspace.id == workspace_id).one()).id

    def get_workspace_policies(self, db: Session, workspace_id: UUID):
        return (
            db.query(Policy)
            .filter(Policy.workspace_id == workspace_id)
            .filter(Policy.ptype.startswith("p"))
            .all()
        )

    def get_workspace_grouping_policies(self, db: Session, workspace_id: UUID):
        return (
            db.query(Policy)
            .filter(Policy.workspace_id == workspace_id)
            .filter(Policy.ptype.startswith("g"))
            .all()
        )

    def get_workspace_users(self, db: Session, workspace_id: UUID):
        return (
            db.query(User)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .filter(UserRole.workspace_id == workspace_id)
            .with_entities(
                User.id,
                User.email,
                User.name,
                Role.name.label("role_name"),
                Role.id.label("role_id"),
            )
            .all()
        )

    def get_workspace_groups(self, db: Session, workspace_id: UUID):
        return db.query(Group).filter(Group.workspace_id == workspace_id).all()

    def get_oldest_user(self, db: Session, workspace_id: UUID):
        return (
            db.query(UserRole)
            .join(User, User.id == UserRole.user_id)
            .filter(UserRole.workspace_id == workspace_id)
            .order_by(UserRole.date)
            .with_entities(User.id, User.email)
            .first()
        )

    def get_user_owned_workspaces(self, db: Session, user_id: UUID):
        UserRoleAlias = aliased(UserRole)

        oldest_users_subquery = (
            db.query(
                UserRoleAlias.workspace_id, func.min(UserRoleAlias.date).label("date")
            )
            .group_by(UserRoleAlias.workspace_id)
            .subquery("oldest_users_subquery")
        )

        return (
            db.query(Workspace)
            .join(UserRole, UserRole.workspace_id == Workspace.id)
            .join(
                oldest_users_subquery,
                and_(
                    UserRole.workspace_id == oldest_users_subquery.c.workspace_id,
                    UserRole.date == oldest_users_subquery.c.date,
                ),
            )
            .filter(UserRole.user_id == user_id)
            .all()
        )


workspace = CRUDWorkspace(Workspace)
