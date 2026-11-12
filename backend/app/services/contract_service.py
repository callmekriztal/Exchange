import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contract import Contract
from app.models.objective import Subtask


class ContractService:
    @staticmethod
    async def create_contract(
        db: AsyncSession,
        subtask_id: uuid.UUID,
        buyer_agent_id: uuid.UUID,
        seller_agent_id: uuid.UUID,
        negotiation_id: uuid.UUID,
        agreed_amount_usd: float,
        terms_and_conditions: dict,
    ) -> Contract:
        contract = Contract(
            subtask_id=subtask_id,
            buyer_agent_id=buyer_agent_id,
            seller_agent_id=seller_agent_id,
            negotiation_id=negotiation_id,
            agreed_amount_usd=agreed_amount_usd,
            terms_and_conditions=terms_and_conditions,
            status="pending_payment",
            signed_at=datetime.now(timezone.utc),
        )
        db.add(contract)

        # Update subtask agreed price & status
        stmt = select(Subtask).where(Subtask.id == subtask_id)
        res = await db.execute(stmt)
        subtask = res.scalars().first()
        if subtask:
            subtask.agreed_price_usd = agreed_amount_usd
            subtask.status = "contracted"

        await db.commit()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def get_by_id(db: AsyncSession, contract_id: uuid.UUID) -> Optional[Contract]:
        stmt = select(Contract).where(Contract.id == contract_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def get_by_subtask_id(db: AsyncSession, subtask_id: uuid.UUID) -> Optional[Contract]:
        stmt = select(Contract).where(Contract.id == subtask_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def get_by_objective(db: AsyncSession, objective_id: uuid.UUID) -> List[Contract]:
        stmt = (
            select(Contract)
            .join(Subtask, Contract.subtask_id == Subtask.id)
            .where(Subtask.objective_id == objective_id)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def update_status(db: AsyncSession, contract_id: uuid.UUID, new_status: str) -> Optional[Contract]:
        stmt = select(Contract).where(Contract.id == contract_id)
        res = await db.execute(stmt)
        contract = res.scalars().first()
        if contract:
            contract.status = new_status
            await db.commit()
            await db.refresh(contract)
        return contract
