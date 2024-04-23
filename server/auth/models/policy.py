from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from .base import Base


class Policy(Base):
    id = Column(UUID(as_uuid=True), server_default=text("uuid_generate_v4()"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id", ondelete="CASCADE"))
    ptype = Column(String, nullable=False)
    v0 = Column(String)
    v1 = Column(String)
    v2 = Column(String)
    v3 = Column(String)
    v4 = Column(String)
    v5 = Column(String)

    date = Column(TIMESTAMP, server_default=func.now())

    __tablename__ = "policy"
    __table_args__ = (
        UniqueConstraint(
            "ptype", "v0", "v1", "v2", "v3", "v4", "v5", "workspace_id", name="unique_policy_constraint"
        ),
    )

    def __str__(self):
        arr = [self.ptype]
        for v in (self.v0, self.v1, self.v2, self.v3, self.v4, self.v5):
            if v is None:
                break
            arr.append(v)
        return ", ".join(arr)
