from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class App(Base):
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )
    name = Column(String)
    label = Column(String)
    description = Column(String)
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE")
    )
    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "app"
