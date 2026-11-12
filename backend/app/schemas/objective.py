import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SubtaskResponse(BaseModel):
    id: uuid.UUID
    objective_id: uuid.UUID
    assigned_seller_id: Optional[uuid.UUID]
    title: str
    description: str
    service_type: str
    allocated_budget_usd: float
    agreed_price_usd: Optional[float]
    sequence_order: int
    status: str
    input_payload: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ObjectiveCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    max_budget_usd: float = Field(..., gt=0)


class ObjectiveResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str
    max_budget_usd: float
    total_spent_usd: float
    status: str
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = []

    class Config:
        from_attributes = True
