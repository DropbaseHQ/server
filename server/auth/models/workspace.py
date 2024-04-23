import datetime

from sqlalchemy import TIMESTAMP, Boolean, Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from .base import Base


class Workspace(Base):
    id = Column(
        UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True
    )

    name = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    date = Column(TIMESTAMP, server_default=func.now())
    worker_url = Column(String)
    in_trial = Column(Boolean, default=False)
    trial_end_date = Column(
        DateTime, server_default=text("(NOW() + INTERVAL '14 days')")
    )

    __tablename__ = "workspace"
