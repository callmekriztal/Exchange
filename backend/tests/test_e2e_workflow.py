import asyncio
import os
import pytest
import httpx
from app.core.config import settings
from app.main import app

@pytest.mark.asyncio
async def test_complete_autonomous_marketplace_lifecycle():
    # Explicitly enable mock mode for automated continuous integration / e2e test suite
    settings.PAYPAL_MOCK_MODE = True
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=40.0) as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        # 2. Register / Login test user
        email = "trader@ai-economy.com"
        password = "SecureTraderPass123!"
        reg_res = await client.post("/api/v1/auth/register", json={"email": email, "password": password})
        if reg_res.status_code == 400:
            pass
        else:
            assert reg_res.status_code == 201

        login_res = await client.post("/api/v1/auth/login/json", json={"email": email, "password": password})
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify /me
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email

        # 3. Ensure agents are seeded
        agents_res = await client.get("/api/v1/agents")
        assert agents_res.status_code == 200
        agents = agents_res.json()
        if len(agents) < 4:
            seed_res = await client.post("/api/v1/agents/seed")
            assert seed_res.status_code == 200
            agents = seed_res.json()
        assert len(agents) >= 4

        # 4. Human user submits Objective
        obj_payload = {
            "title": "Renewable Hydrogen Economy 2026",
            "description": "Analyze green hydrogen production efficiency, perform cost-per-kg CAGR modeling, and synthesize an executive roadmap.",
            "max_budget_usd": 25.00,
        }
        create_obj_res = await client.post("/api/v1/objectives", json=obj_payload, headers=headers)
        assert create_obj_res.status_code == 201
        objective = create_obj_res.json()
        objective_id = objective["id"]

        # 5. Wait for LangGraph background decomposition, discovery, negotiation, and contract generation
        contracts = []
        for _ in range(25):
            await asyncio.sleep(0.5)
            c_res = await client.get(f"/api/v1/contracts/objective/{objective_id}", headers=headers)
            if c_res.status_code == 200 and len(c_res.json()) >= 3:
                contracts = c_res.json()
                break

        assert len(contracts) >= 3, f"LangGraph should generate 3 contracts, got: {len(contracts)}"
        contract_ids = [c["id"] for c in contracts]
        total_agreed = sum(c["agreed_amount_usd"] for c in contracts)
        assert total_agreed <= 25.00, f"Total agreed price ({total_agreed}) exceeded budget limit"

        # 6. Verify Negotiation rounds exist
        first_subtask_id = contracts[0]["subtask_id"]
        neg_res = await client.get(f"/api/v1/contracts/negotiation/{first_subtask_id}", headers=headers)
        assert neg_res.status_code == 200
        neg_data = neg_res.json()
        assert len(neg_data["rounds"]) >= 1
        assert neg_data["status"] == "agreed"

        # 7. Create PayPal Order
        pay_order_res = await client.post(
            "/api/v1/payments/create-order",
            json={"objective_id": objective_id, "contract_ids": contract_ids},
            headers=headers,
        )
        assert pay_order_res.status_code == 200
        order_data = pay_order_res.json()
        assert "paypal_order_id" in order_data
        assert order_data["amount_usd"] == total_agreed
        paypal_order_id = order_data["paypal_order_id"]

        # 8. Human approves checkout & Backend captures order
        capture_res = await client.post(
            "/api/v1/payments/capture-order",
            json={"paypal_order_id": paypal_order_id},
            headers=headers,
        )
        assert capture_res.status_code == 200
        capture_data = capture_res.json()
        assert capture_data["status"] == "captured"

        # 9. Wait for task fulfillment, evaluation, and ledger settlement
        is_completed = False
        for _ in range(25):
            await asyncio.sleep(0.5)
            check_obj = await client.get(f"/api/v1/objectives/{objective_id}", headers=headers)
            if check_obj.status_code == 200 and check_obj.json()["status"] == "completed":
                is_completed = True
                break

        assert is_completed, "Objective should reach completed status after task execution and evaluation"

        # 10. Verify Deliverable and Evaluation for first contract
        deliv_res = await client.get(f"/api/v1/deliverables/contract/{contracts[0]['id']}", headers=headers)
        assert deliv_res.status_code == 200
        deliv_data = deliv_res.json()
        assert "checksum" in deliv_data
        assert len(deliv_data["checksum"]) == 64
        assert deliv_data["evaluation"] is not None
        assert deliv_data["evaluation"]["score"] >= 75.0
        assert deliv_data["evaluation"]["is_accepted"] is True

        # 11. Verify Double-Entry Ledger Entries
        ledger_res = await client.get("/api/v1/ledger", headers=headers)
        assert ledger_res.status_code == 200
        entries = ledger_res.json()
        assert len(entries) > 0

        # Verify escrow locks and settlements exist
        entry_types = [e["entry_type"] for e in entries]
        assert "escrow_lock" in entry_types
        assert "seller_settlement" in entry_types
        assert "platform_fee" in entry_types

        print(f"\n=======================================================")
        print(f" [E2E SUCCESS] Successfully executed complete AI Economy cycle!")
        print(f" Objective: {objective_id}")
        print(f" Contracts Funded & Settled: {len(contracts)}")
        print(f" Deliverable Evaluated Score: {deliv_data['evaluation']['score']}/100")
        print(f" Total Double-Entry Ledger Entries: {len(entries)}")
        print(f"=======================================================\n")
