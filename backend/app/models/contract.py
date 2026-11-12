import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDAuditMixin, utc_now


class Contract(Base, UUIDAuditMixin):
    __tablename__ = "contracts"

    subtask_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subtasks.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    buyer_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    seller_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    negotiation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("negotiations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    agreed_amount_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    terms_and_conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True, nullable=False)
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    subtask = relationship("Subtask", back_populates="contract", lazy="selectin")
    buyer_agent = relationship("Agent", foreign_keys=[buyer_agent_id], lazy="selectin")
    seller_agent = relationship("Agent", foreign_keys=[seller_agent_id], lazy="selectin")
    negotiation = relationship("Negotiation", lazy="selectin")
    deliverable = relationship("Deliverable", back_populates="contract", uselist=False, lazy="selectin")
    payments = relationship("Payment", back_populates="contract")
    ledger_entries = relationship("LedgerEntry", back_populates="contract")
