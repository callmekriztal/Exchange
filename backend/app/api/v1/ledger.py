import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.ledger import LedgerEntryResponse
from app.services.ledger_service import LedgerService

router = APIRouter(prefix="/ledger", tags=["Double-Entry Ledger"])


@router.get("", response_model=List[LedgerEntryResponse])
async def list_ledger_entries(db: AsyncSession = Depends(get_db)):
    entries = await LedgerService.get_all_entries(db)
    return entries


@router.get("/contract/{contract_id}", response_model=List[LedgerEntryResponse])
async def get_contract_ledger_entries(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    entries = await LedgerService.get_entries_for_contract(db, contract_id)
    return entries
