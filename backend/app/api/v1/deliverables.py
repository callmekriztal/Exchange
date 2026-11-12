import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.deliverable import Deliverable
from app.schemas.deliverable import DeliverableResponse

router = APIRouter(prefix="/deliverables", tags=["Deliverables & Evaluations"])


@router.get("/contract/{contract_id}", response_model=DeliverableResponse)
async def get_deliverable_by_contract(
    contract_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Deliverable)
        .options(selectinload(Deliverable.evaluation))
        .where(Deliverable.contract_id == contract_id)
    )
    res = await db.execute(stmt)
    deliv = res.scalars().first()
    if not deliv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found for this contract")
    return deliv
