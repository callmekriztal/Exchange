import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    deliverable_id: uuid.UUID
    evaluator_agent_id: uuid.UUID
    rubric_scores: Dict[str, Any]
    score: float
    is_accepted: bool
    feedback: str
    evaluated_at: datetime

    class Config:
        from_attributes = True


class DeliverableResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    seller_agent_id: uuid.UUID
    artifact_type: str
    content: Dict[str, Any]
    checksum: str
    execution_duration_ms: int
    submitted_at: datetime
    evaluation: Optional[EvaluationResponse] = None

    class Config:
        from_attributes = True
