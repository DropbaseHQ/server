from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..base import CRUDBase
from ...models import ResetToken, User


class CRUDResetToken(CRUDBase[ResetToken, ResetToken, ResetToken]):
    def get_latest_user_refresh_token(self, db: Session, user_id: str) -> ResetToken:
        return (
            db.query(ResetToken)
            .join(User, User.id == ResetToken.user_id)
            .filter(User.id == user_id)
            .filter(ResetToken.status == "valid")
            .order_by(desc(ResetToken.expiration_time))
        ).first()


reset_token = CRUDResetToken(ResetToken)
