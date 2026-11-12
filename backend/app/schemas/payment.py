import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CreateOrderRequest(BaseModel):
    objective_id: uuid.UUID
    contract_ids: List[uuid.UUID]


class CreateOrderResponse(BaseModel):
    paypal_order_id: str
    amount_usd: float
    currency: str = "USD"
    status: str
    contract_ids: List[uuid.UUID]


class CaptureOrderRequest(BaseModel):
    paypal_order_id: str


class CaptureOrderResponse(BaseModel):
    status: str
    paypal_order_id: str
    paypal_capture_id: Optional[str]
    amount_usd: float
    contracts_funded: int


class PaymentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    contract_id: Optional[uuid.UUID]
    paypal_order_id: str
    paypal_capture_id: Optional[str]
    amount_usd: float
    currency: str
    status: str
    raw_paypal_response: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
