import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.base import UUIDAuditMixin


class AuditLog(Base, UUIDAuditMixin):
    __tablename__ = "audit_logs"

    entity_name: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, agent, system, paypal
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
