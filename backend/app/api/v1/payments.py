import uuid
from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.agents.graph import execute_task_fulfillment
from app.core.config import settings
from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.models.contract import Contract
from app.models.objective import Objective
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import (
    CaptureOrderRequest,
    CaptureOrderResponse,
    CreateOrderRequest,
    CreateOrderResponse,
)
from app.services.auth_service import get_current_user
from app.services.contract_service import ContractService
from app.services.ledger_service import LedgerService
from app.services.paypal_service import PayPalService

router = APIRouter(prefix="/payments", tags=["PayPal Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_paypal_order(
    data: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Verify Objective and User ownership
    stmt = select(Objective).where(Objective.id == data.objective_id, Objective.user_id == current_user.id)
    res = await db.execute(stmt)
    objective = res.scalars().first()
    if not objective:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found or access denied")

    # 2. Verify Contracts and Compute Total
    stmt = select(Contract).where(Contract.id.in_(data.contract_ids))
    res = await db.execute(stmt)
    contracts = list(res.scalars().all())

    if len(contracts) != len(data.contract_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more specified contracts were not found")

    total_amount = sum(float(c.agreed_amount_usd) for c in contracts)

    # 3. Policy Check: Total amount cannot exceed objective max budget
    if total_amount > float(objective.max_budget_usd):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Total contract cost (${total_amount:.2f}) exceeds objective budget (${float(objective.max_budget_usd):.2f})",
        )

    # 4. Invoke PayPal Orders API v2
    custom_id = f"OBJ_{objective.id}"
    paypal_order = await PayPalService.create_order(
        amount_usd=total_amount,
        reference_id=str(objective.id),
        description=f"Funding AI Economy contracts for: {objective.title}",
        custom_id=custom_id,
    )

    paypal_order_id = paypal_order["id"]

    # 5. Persist Payment Record in DB
    payment = Payment(
        user_id=current_user.id,
        contract_id=contracts[0].id if contracts else None,
        paypal_order_id=paypal_order_id,
        amount_usd=total_amount,
        currency="USD",
        status="created",
        raw_paypal_response=paypal_order,
    )
    db.add(payment)
    await db.commit()

    return CreateOrderResponse(
        paypal_order_id=paypal_order_id,
        amount_usd=total_amount,
        currency="USD",
        status="created",
        contract_ids=data.contract_ids,
    )


@router.post("/capture-order", response_model=CaptureOrderResponse)
async def capture_paypal_order(
    data: CaptureOrderRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Lookup Payment by paypal_order_id with row-level lock to prevent concurrent captures
    stmt = (
        select(Payment)
        .where(Payment.paypal_order_id == data.paypal_order_id)
        .with_for_update()
    )
    res = await db.execute(stmt)
    payment = res.scalars().first()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment record not found for this PayPal Order ID",
        )

    # 2. Verify payment belongs to current authenticated user
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user does not own this payment record",
        )

    # 3. Idempotency: If already captured, return immediately without re-capturing or double-crediting
    if payment.status == "captured":
        return CaptureOrderResponse(
            status="captured",
            paypal_order_id=payment.paypal_order_id,
            paypal_capture_id=payment.paypal_capture_id,
            amount_usd=float(payment.amount_usd),
            contracts_funded=1,
        )

    # 4. Execute Capture with PayPal Orders API v2
    capture_resp = await PayPalService.capture_order(data.paypal_order_id)

    # 5. Validate PayPal response status and extract capture details
    overall_status = capture_resp.get("status")
    purchase_units = capture_resp.get("purchase_units", [])
    if not purchase_units:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid PayPal capture response: missing purchase_units (status: {overall_status})",
        )

    captures = purchase_units[0].get("payments", {}).get("captures", [])
    if not captures:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PayPal order has no captures recorded (order status: {overall_status})",
        )

    primary_capture = captures[0]
    capture_id = primary_capture.get("id")
    capture_status = primary_capture.get("status")

    if capture_status != "COMPLETED" and overall_status != "COMPLETED":
        payment.status = "failed"
        payment.raw_paypal_response = capture_resp
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PayPal capture was not completed (capture status: {capture_status}, order: {overall_status})",
        )

    # 6. Validate captured amount and currency against expected contract amounts
    amount_info = primary_capture.get("amount", {})
    captured_currency = amount_info.get("currency_code", "USD")
    try:
        captured_amount = float(amount_info.get("value", 0.0))
    except (ValueError, TypeError):
        captured_amount = 0.0

    if captured_currency != payment.currency:
        payment.status = "failed"
        payment.raw_paypal_response = capture_resp
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Captured currency mismatch: expected {payment.currency}, got {captured_currency}",
        )

    expected_amount = float(payment.amount_usd)
    if abs(captured_amount - expected_amount) > 0.01:
        payment.status = "failed"
        payment.raw_paypal_response = capture_resp
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Captured amount mismatch: expected ${expected_amount:.2f}, got ${captured_amount:.2f}",
        )

    # 7. Update Payment record to captured
    payment.status = "captured"
    payment.paypal_capture_id = capture_id
    payment.raw_paypal_response = capture_resp

    # 8. Find all contracts associated with this objective
    obj_id = None
    if payment.contract_id:
        c_stmt = (
            select(Contract)
            .options(selectinload(Contract.subtask))
            .where(Contract.id == payment.contract_id)
        )
        c_res = await db.execute(c_stmt)
        c = c_res.scalars().first()
        if c and c.subtask:
            obj_id = str(c.subtask.objective_id)

    # Transition contracts to funded/active and lock escrow in ledger
    funded_count = 0
    if obj_id:
        all_contracts = await ContractService.get_by_objective(db, uuid.UUID(obj_id))
        for ct in all_contracts:
            ct.status = "funded"
            funded_count += 1
            # 9. Record internal accounting double-entry ledger line for Escrow
            await LedgerService.record_escrow_deposit(
                db=db,
                payment_id=payment.id,
                contract_id=ct.id,
                amount_usd=float(ct.agreed_amount_usd),
                description=f"PayPal Capture {capture_id}: Escrow locked for contract {ct.id}",
            )

    await db.commit()

    # 10. Broadcast Payment Captured event
    if obj_id:
        await ws_manager.broadcast(obj_id, {
            "type": "PAYMENT_CAPTURED",
            "paypal_order_id": payment.paypal_order_id,
            "paypal_capture_id": capture_id,
            "amount_usd": float(payment.amount_usd),
            "status": "funded",
        })

        # 11. Dispatch Seller execution, Buyer deliverable grading, and Escrow settlement in background
        background_tasks.add_task(execute_task_fulfillment, obj_id)

    return CaptureOrderResponse(
        status="captured",
        paypal_order_id=payment.paypal_order_id,
        paypal_capture_id=capture_id,
        amount_usd=float(payment.amount_usd),
        contracts_funded=funded_count or 1,
    )


@router.post("/webhook")
async def paypal_webhook(
    request: Request,
    paypal_transmission_id: str = Header(None, alias="Paypal-Transmission-Id"),
    paypal_transmission_time: str = Header(None, alias="Paypal-Transmission-Time"),
    paypal_cert_url: str = Header(None, alias="Paypal-Cert-Url"),
    paypal_auth_algo: str = Header(None, alias="Paypal-Auth-Algo"),
    paypal_transmission_sig: str = Header(None, alias="Paypal-Transmission-Sig"),
    db: AsyncSession = Depends(get_db),
):
    """Asynchronous webhook receiver with cryptographic signature verification and idempotent event handling."""
    body = await request.json()

    # Reject if headers are missing when not in mock test mode
    if not settings.PAYPAL_MOCK_MODE:
        if not (paypal_transmission_id and paypal_transmission_sig and paypal_cert_url and paypal_auth_algo and paypal_transmission_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required PayPal transmission verification headers",
            )

        is_valid = await PayPalService.verify_webhook_signature(
            transmission_id=paypal_transmission_id,
            transmission_time=paypal_transmission_time,
            cert_url=paypal_cert_url,
            auth_algo=paypal_auth_algo,
            transmission_sig=paypal_transmission_sig,
            webhook_body=body,
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PayPal webhook signature",
            )

    event_type = body.get("event_type")
    resource = body.get("resource", {})

    print(f"[PayPal Webhook] Received verified event: {event_type} for resource: {resource.get('id')}")
    return {"received": True, "event_type": event_type}
