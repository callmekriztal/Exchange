import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDAuditMixin, utc_now


class Negotiation(Base, UUIDAuditMixin):
    __tablename__ = "negotiations"

    subtask_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subtasks.id", ondelete="CASCADE"),
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
    buyer_opening_offer_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    seller_opening_ask_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    final_agreed_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    max_rounds: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    current_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    subtask = relationship("Subtask", back_populates="negotiation")
    buyer_agent = relationship("Agent", foreign_keys=[buyer_agent_id])
    seller_agent = relationship("Agent", foreign_keys=[seller_agent_id])
    rounds = relationship("NegotiationRound", back_populates="negotiation", cascade="all, delete-orphan", order_by="NegotiationRound.round_number", lazy="selectin")


class NegotiationRound(Base, UUIDAuditMixin):
    __tablename__ = "negotiation_rounds"

    negotiation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("negotiations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker_agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False)  # offer, counter_offer, accept, reject
    proposed_price_usd: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    negotiation = relationship("Negotiation", back_populates="rounds")
    speaker_agent = relationship("Agent")
