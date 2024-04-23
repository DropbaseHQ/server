from sqlalchemy import TIMESTAMP, Column, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class WorkerStatus(Base):
    token = Column(String, ForeignKey("token.token", ondelete="SET NULL"))
    version = Column(String)
    date = Column(TIMESTAMP, server_default=func.now())
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )
    __tablename__ = "worker_status"
