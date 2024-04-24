# @JON: DO WE STILL NEED THIS MODEL?? THERE IS NO SCHEMA ASSOCIATED WITH IT
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class UserGroup(Base):
    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.id", ondelete="CASCADE"))
    role = Column(String, default="member")

    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "user_group"
