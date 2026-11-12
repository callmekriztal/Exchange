import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentServiceResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    service_name: str
    service_category: str
    description: str
    pricing_type: str
    base_price_usd: float
    min_price_usd: float
    max_price_usd: float
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    is_available: bool

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    id: uuid.UUID
    name: str
    agent_type: str
    description: Optional[str]
    capabilities: List[str]
    pricing_policy: Dict[str, Any]
    is_active: bool
    services: List[AgentServiceResponse] = []

    class Config:
        from_attributes = True


class AgentCreate(BaseModel):
    name: str
    agent_type: str
    description: Optional[str] = None
    system_prompt_template: str
    capabilities: List[str] = []
    pricing_policy: Dict[str, Any] = {}
