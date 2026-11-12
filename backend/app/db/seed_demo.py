import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.objective import Objective
from app.services.marketplace_service import MarketplaceService
from app.agents.graph import marketplace_graph, execute_task_fulfillment
from app.api.v1.payments import capture_paypal_order
from app.services.contract_service import ContractService
from app.services.paypal_service import PayPalService
from app.services.ledger_service import LedgerService
from app.models.payment import Payment
from sqlalchemy import select


async def seed_demo():
    print("Seeding full autonomous trading demonstration...")
    async with AsyncSessionLocal() as db:
        # 1. Seed agents
        agents = await MarketplaceService.seed_default_agents(db)
        print(f"Seeded {len(agents)} agents into registry.")

        # 2. Get or create demo user
        stmt = select(User).where(User.email == "trader@ai-economy.com")
        res = await db.execute(stmt)
        user = res.scalars().first()
        if not user:
            from app.core.security import get_password_hash
            user = User(
                email="trader@ai-economy.com",
                hashed_password=get_password_hash("SecureTraderPass123!"),
                role="human_user",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        # 3. Create Objective
        title = "Autonomous Drone Fleet Delivery Logistics 2026"
        description = "Research regulatory airspace corridors for urban drone logistics, calculate unit cost-per-drop CAGR, and produce an executive deployment report."
        max_budget = 28.00

        objective = Objective(
            user_id=user.id,
            title=title,
            description=description,
            max_budget_usd=max_budget,
            status="planning",
        )
        db.add(objective)
        await db.commit()
        await db.refresh(objective)
        print(f"Created Objective '{title}' (ID: {objective.id}) with budget ${max_budget:.2f}")

    # 4. Run LangGraph Multi-Agent Negotiation & Contracting
    print("Running LangGraph agent orchestration (Decomposition -> Matchmaking -> Negotiation -> Contracts)...")
    initial_state = {
        "objective_id": str(objective.id),
        "user_id": str(user.id),
        "title": title,
        "description": description,
        "max_budget_usd": max_budget,
        "total_spent_usd": 0.0,
        "subtasks": [],
        "negotiations": {},
        "contracts": [],
        "deliverables": {},
        "evaluations": {},
        "payment_status": "pending",
        "logs": [],
        "current_step": "init",
        "is_completed": False,
    }
    await marketplace_graph.ainvoke(initial_state)

    # 5. Simulate PayPal Capture & Settle Contracts
    async with AsyncSessionLocal() as db:
        contracts = await ContractService.get_by_objective(db, objective.id)
        total_amount = sum(float(c.agreed_amount_usd) for c in contracts)

        # Create PayPal Order
        paypal_order = await PayPalService.create_order(
            amount_usd=total_amount,
            reference_id=str(objective.id),
            description=f"Funding contracts for {title}",
            custom_id=f"OBJ_{objective.id}",
        )
        order_id = paypal_order["id"]

        payment = Payment(
            user_id=user.id,
            contract_id=contracts[0].id if contracts else None,
            paypal_order_id=order_id,
            paypal_capture_id=f"3C_DEMO_{order_id[2:]}",
            amount_usd=total_amount,
            currency="USD",
            status="captured",
            raw_paypal_response=paypal_order,
        )
        db.add(payment)

        for c in contracts:
            c.status = "funded"
            await LedgerService.record_escrow_deposit(
                db=db,
                payment_id=payment.id,
                contract_id=c.id,
                amount_usd=float(c.agreed_amount_usd),
                description=f"PayPal Capture {payment.paypal_capture_id}: Escrow locked for contract {c.id}",
            )
        await db.commit()
        print(f"PayPal Order {order_id} captured. ${total_amount:.2f} locked in internal Escrow.")

    # 6. Execute task fulfillment, Buyer deliverable grading & Ledger payout
    print("Executing Seller toolchains, Buyer deliverable evaluations, and Ledger payouts...")
    await execute_task_fulfillment(str(objective.id))
    print(f"\n[DEMO SEED COMPLETED] Objective {objective.id} successfully traded, delivered, and settled!")


if __name__ == "__main__":
    asyncio.run(seed_demo())
