from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class Token(Base):
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )

    token = Column(String, nullable=False, unique=True)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE")
    )
    name = Column(String)
    is_active = Column(Boolean, default=True)
    type = Column(String)
    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "token"
