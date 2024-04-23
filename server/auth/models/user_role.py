from sqlalchemy import TIMESTAMP, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class UserRole(Base):
    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"))
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"))

    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "user_role"
