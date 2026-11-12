import uuid
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.ledger import LedgerEntry


class LedgerService:
    ACCOUNT_PAYPAL_CLEARING = "PAYPAL_CLEARING"
    ACCOUNT_ESCROW_HOLD = "ESCROW_HOLD"
    ACCOUNT_SELLER_AGENT = "SELLER_AGENT_BALANCE"
    ACCOUNT_PLATFORM_FEE = "PLATFORM_FEE_REVENUE"

    @classmethod
    async def record_escrow_deposit(
        cls,
        db: AsyncSession,
        payment_id: uuid.UUID,
        contract_id: Optional[uuid.UUID],
        amount_usd: float,
        description: str,
    ) -> LedgerEntry:
        """Records human payment captured via PayPal into internal Escrow hold."""
        entry = LedgerEntry(
            payment_id=payment_id,
            contract_id=contract_id,
            debit_account=cls.ACCOUNT_PAYPAL_CLEARING,
            credit_account=cls.ACCOUNT_ESCROW_HOLD,
            amount_usd=amount_usd,
            entry_type="escrow_lock",
            description=description,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @classmethod
    async def settle_contract_payout(
        cls,
        db: AsyncSession,
        contract_id: uuid.UUID,
        seller_agent_name: str,
        total_amount_usd: float,
    ) -> List[LedgerEntry]:
        """Settles escrow to seller agent and platform fee upon deliverable acceptance."""
        fee_rate = settings.PLATFORM_FEE_PERCENTAGE
        platform_fee = round(total_amount_usd * fee_rate, 2)
        seller_payout = round(total_amount_usd - platform_fee, 2)

        # 1. Payout to Seller Agent balance
        seller_entry = LedgerEntry(
            contract_id=contract_id,
            debit_account=cls.ACCOUNT_ESCROW_HOLD,
            credit_account=f"{cls.ACCOUNT_SELLER_AGENT}_{seller_agent_name}",
            amount_usd=seller_payout,
            entry_type="seller_settlement",
            description=f"Deliverable accepted: Payout to {seller_agent_name} for contract {contract_id}",
        )

        # 2. Platform fee
        fee_entry = LedgerEntry(
            contract_id=contract_id,
            debit_account=cls.ACCOUNT_ESCROW_HOLD,
            credit_account=cls.ACCOUNT_PLATFORM_FEE,
            amount_usd=platform_fee,
            entry_type="platform_fee",
            description=f"Marketplace service fee ({int(fee_rate*100)}%) for contract {contract_id}",
        )

        db.add_all([seller_entry, fee_entry])
        await db.commit()
        await db.refresh(seller_entry)
        await db.refresh(fee_entry)
        return [seller_entry, fee_entry]

    @staticmethod
    async def get_entries_for_contract(db: AsyncSession, contract_id: uuid.UUID) -> List[LedgerEntry]:
        stmt = select(LedgerEntry).where(LedgerEntry.contract_id == contract_id).order_by(LedgerEntry.created_at)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_all_entries(db: AsyncSession) -> List[LedgerEntry]:
        stmt = select(LedgerEntry).order_by(LedgerEntry.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())
