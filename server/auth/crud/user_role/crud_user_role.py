from uuid import UUID

from sqlalchemy.orm import Session

from ...models import Role, UserRole
from ...schemas.role import CreateRole, UpdateRole
from ..base import CRUDBase


class CRUDUserRole(CRUDBase[UserRole, CreateRole, UpdateRole]):
    def get_user_role(self, db: Session, user_id: UUID, workspace_id: UUID) -> Role:
        return (
            db.query(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .filter(UserRole.workspace_id == workspace_id)
            .one_or_none()
        )

    def get_user_user_role(self, db: Session, user_id: UUID, workspace_id: UUID) -> UserRole:
        return (
            db.query(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == user_id)
            .filter(UserRole.workspace_id == workspace_id)
            .with_entities(UserRole.id, UserRole.role_id, Role.name)
            .one_or_none()
        )


user_role = CRUDUserRole(UserRole)
