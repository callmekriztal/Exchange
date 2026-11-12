import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDAuditMixin, utc_now


class Objective(Base, UUIDAuditMixin):
    __tablename__ = "objectives"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    max_budget_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_spent_usd: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = relationship("User", back_populates="objectives")
    subtasks = relationship("Subtask", back_populates="objective", cascade="all, delete-orphan", order_by="Subtask.sequence_order", lazy="selectin")


class Subtask(Base, UUIDAuditMixin):
    __tablename__ = "subtasks"

    objective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("objectives.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_type: Mapped[str] = mapped_column(String(60), nullable=False)
    allocated_budget_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    agreed_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    objective = relationship("Objective", back_populates="subtasks")
    assigned_seller = relationship("Agent")
    contract = relationship("Contract", back_populates="subtask", uselist=False)
    negotiation = relationship("Negotiation", back_populates="subtask", uselist=False)
