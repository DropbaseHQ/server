from sqlalchemy.orm import Session
from ..base import CRUDBase
from ...models import User, UserRole, Workspace
from ...schemas.user import CreateUser, UpdateUser


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    def update_user_refresh_token(self, db: Session, user_id: str, refresh_token: str):
        user = self.get(db, user_id)
        self.update(db, db_obj=user, obj_in={"refresh_token": refresh_token})
        db.commit()

    def get_user_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def get_user_first_workspace(self, db: Session, user_id: str):
        return (
            db.query(Workspace)
            .join(UserRole, UserRole.workspace_id == Workspace.id)
            .filter(UserRole.user_id == user_id)
            .first()
        )


user = CRUDUser(User)
