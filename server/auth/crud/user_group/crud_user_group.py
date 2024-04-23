from typing import List

from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import Group, UserGroup


class CRUDUserGroup(CRUDBase[UserGroup, UserGroup, UserGroup]):
    def get_user_groups(self, db: Session, user_id: str):
        return db.query(UserGroup.group_id).filter(UserGroup.user_id == user_id).all()

    def get_user_workspace_groups(self, db: Session, user_id: str, workspace_id: str):
        return (
            db.query(Group)
            .join(UserGroup, UserGroup.group_id == Group.id)
            .filter(UserGroup.user_id == user_id, Group.workspace_id == workspace_id)
            .all()
        )

    def get_user_workspace_user_groups(
        self, db: Session, user_id: str, workspace_id: str
    ) -> List[UserGroup]:
        return (
            db.query(UserGroup)
            .join(Group, UserGroup.group_id == Group.id)
            .filter(UserGroup.user_id == user_id, Group.workspace_id == workspace_id)
            .all()
        )

    def get_user_role(self, db: Session, user_id: str, group_id: str):
        return (
            db.query(UserGroup.role)
            .filter(UserGroup.user_id == user_id, UserGroup.group_id == group_id)
            .one_or_none()
        )


user_group = CRUDUserGroup(UserGroup)
