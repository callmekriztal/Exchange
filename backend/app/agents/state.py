from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class SubtaskState(TypedDict):
    id: str
    title: str
    description: str
    service_type: str
    allocated_budget_usd: float
    sequence_order: int
    assigned_seller_id: Optional[str]
    agreed_price_usd: Optional[float]
    status: str
    input_payload: Dict[str, Any]


class NegotiationState(TypedDict):
    subtask_id: str
    buyer_agent_id: str
    seller_agent_id: str
    seller_name: str
    rounds: List[Dict[str, Any]]
    final_price_usd: Optional[float]
    status: str  # agreed, rejected


class MarketplaceState(TypedDict):
    objective_id: str
    user_id: str
    title: str
    description: str
    max_budget_usd: float
    total_spent_usd: float
    subtasks: List[SubtaskState]
    negotiations: Dict[str, NegotiationState]
    contracts: List[Dict[str, Any]]
    deliverables: Dict[str, Any]
    evaluations: Dict[str, Any]
    payment_status: str
    logs: List[str]
    current_step: str
    is_completed: bool
