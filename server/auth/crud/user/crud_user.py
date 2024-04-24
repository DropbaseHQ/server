from sqlalchemy.orm import Session
from ..base import CRUDBase
from ...models import User, UserRole, Workspace
from ...schemas.user import CreateUser, UpdateUser


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    def get_user_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()


user = CRUDUser(User)
