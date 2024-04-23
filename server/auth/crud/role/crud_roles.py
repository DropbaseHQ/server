from uuid import UUID

from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import Policy, Role
from ...schemas.role import CreateRole, UpdateRole


class CRUDRole(CRUDBase[Role, CreateRole, UpdateRole]):
    def get_role_policies(self, db: Session, role_id: UUID):
        return (
            db.query(Policy)
            .join(Role, Role.id == Policy.role_id)
            .filter(Role.id == role_id)
            .all()
        )

    def get_role_by_name(self, db: Session, role_name: str):
        return db.query(Role).filter(Role.name == role_name).one()


role = CRUDRole(Role)
