from sqlalchemy.orm import Session

from ...models import User
from ...schemas.user import CreateUser, UpdateUser
from ..base import CRUDBase


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    def get_user_by_email(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()


user = CRUDUser(User)
