from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy import UniqueConstraint
from .base import Base


class Page(Base):
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )
    name = Column(String)
    label = Column(String)
    description = Column(String)
    app_id = Column(UUID(as_uuid=True), ForeignKey("app.id", ondelete="CASCADE"))
    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "page"
    __table_args__ = (
        UniqueConstraint("name", "app_id", name="unique_page_name_per_app"),
    )
