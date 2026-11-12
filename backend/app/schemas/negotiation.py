import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class NegotiationRoundResponse(BaseModel):
    id: uuid.UUID
    negotiation_id: uuid.UUID
    round_number: int
    speaker_agent_id: uuid.UUID
    action: str
    proposed_price_usd: float
    rationale: str
    created_at: datetime

    class Config:
        from_attributes = True


class NegotiationResponse(BaseModel):
    id: uuid.UUID
    subtask_id: uuid.UUID
    buyer_agent_id: uuid.UUID
    seller_agent_id: uuid.UUID
    buyer_opening_offer_usd: float
    seller_opening_ask_usd: float
    final_agreed_price_usd: Optional[float]
    max_rounds: int
    current_round: int
    status: str
    rounds: List[NegotiationRoundResponse] = []

    class Config:
        from_attributes = True
