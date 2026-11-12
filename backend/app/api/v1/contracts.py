import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.contract import Contract
from app.models.negotiation import Negotiation
from app.schemas.contract import ContractResponse
from app.schemas.negotiation import NegotiationResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts & Negotiations"])


@router.get("/objective/{objective_id}", response_model=List[ContractResponse])
async def list_contracts_for_objective(
    objective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    contracts = await ContractService.get_by_objective(db, objective_id)
    return contracts


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    contract = await ContractService.get_by_id(db, contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


@router.get("/negotiation/{subtask_id}", response_model=NegotiationResponse)
async def get_negotiation_by_subtask(
    subtask_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Negotiation)
        .options(selectinload(Negotiation.rounds))
        .where(Negotiation.subtask_id == subtask_id)
    )
    res = await db.execute(stmt)
    neg = res.scalars().first()
    if not neg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negotiation not found for subtask")
    return neg
