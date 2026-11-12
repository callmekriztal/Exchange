import uuid
from datetime import datetime
from typing import List
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDAuditMixin, utc_now


class Agent(Base, UUIDAuditMixin):
    __tablename__ = "agents"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # buyer, research, analysis, report
    description: Mapped[str] = mapped_column(Text, nullable=True)
    system_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    capabilities: Mapped[dict] = mapped_column(JSONB, default=list, nullable=False)
    pricing_policy: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="agents")
    services = relationship("AgentService", back_populates="agent", cascade="all, delete-orphan", lazy="selectin")


class AgentService(Base, UUIDAuditMixin):
    __tablename__ = "agent_services"

    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_name: Mapped[str] = mapped_column(String(120), nullable=False)
    service_category: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    pricing_type: Mapped[str] = mapped_column(String(30), default="fixed", nullable=False)
    base_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    min_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    input_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    agent = relationship("Agent", back_populates="services")
