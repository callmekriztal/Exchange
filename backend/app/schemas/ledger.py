import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LedgerEntryResponse(BaseModel):
    id: uuid.UUID
    payment_id: Optional[uuid.UUID]
    contract_id: Optional[uuid.UUID]
    debit_account: str
    credit_account: str
    amount_usd: float
    entry_type: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class AccountBalanceResponse(BaseModel):
    account_name: str
    total_debit: float
    total_credit: float
    net_balance: float
