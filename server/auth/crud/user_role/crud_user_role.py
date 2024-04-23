from uuid import UUID

from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import Role, UserRole
from ...schemas.role import CreateRole, UpdateRole


class CRUDUserRole(CRUDBase[UserRole, CreateRole, UpdateRole]):
    def user_is_in_workspace(
        self, db: Session, user_id: UUID, workspace_id: UUID
    ) -> bool:
        return (
            db.query(UserRole)
            .filter(UserRole.user_id == str(user_id))
            .filter(UserRole.workspace_id == str(workspace_id))
            .count()
            > 0
        )

    def get_user_role(self, db: Session, user_id: UUID, workspace_id: UUID) -> Role:
        return (
            db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .filter(UserRole.workspace_id == workspace_id)
            .one_or_none()
        )

    def get_user_user_role(
        self, db: Session, user_id: UUID, workspace_id: UUID
    ) -> UserRole:
        return (
            db.query(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .filter(UserRole.workspace_id == workspace_id)
            .with_entities(UserRole.id, UserRole.role_id, Role.name)
            .one_or_none()
        )

    def get_workspace_owner(self, db: Session, workspace_id: UUID) -> UserRole:
        return (
            db.query(UserRole)
            .filter(UserRole.workspace_id == workspace_id)
            .order_by(UserRole.date)
            .first()
        )


user_role = CRUDUserRole(UserRole)
