from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from .base import Base


class ResetToken(Base):
    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)

    hashed_token = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    expiration_time = Column(DateTime, nullable=False)
    status = Column(String)

    __tablename__ = "reset_token"
