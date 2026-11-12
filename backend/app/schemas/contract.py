import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ContractResponse(BaseModel):
    id: uuid.UUID
    subtask_id: uuid.UUID
    buyer_agent_id: uuid.UUID
    seller_agent_id: uuid.UUID
    negotiation_id: uuid.UUID
    agreed_amount_usd: float
    terms_and_conditions: Dict[str, Any]
    status: str
    signed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
