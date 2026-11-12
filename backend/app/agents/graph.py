import asyncio
import uuid
from typing import Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import END, StateGraph
from app.agents.buyer.decomposition import decompose_goal_llm
from app.agents.buyer.discovery import AgentMatchmaker
from app.agents.buyer.evaluation import DeliverableEvaluator
from app.agents.negotiation.engine import NegotiationEngine
from app.agents.sellers.analysis_agent import AnalysisAgentExecutor
from app.agents.sellers.report_agent import ReportAgentExecutor
from app.agents.sellers.research_agent import ResearchAgentExecutor
from app.agents.state import MarketplaceState
from app.core.database import AsyncSessionLocal
from app.core.websocket_manager import ws_manager
from app.models.agent import Agent
from app.models.contract import Contract
from app.models.deliverable import Deliverable, Evaluation
from app.models.objective import Objective, Subtask
from app.services.contract_service import ContractService
from app.services.ledger_service import LedgerService
from app.services.marketplace_service import MarketplaceService


async def decompose_node(state: MarketplaceState) -> Dict[str, Any]:
    """LangGraph Node: Decomposes objective into subtasks and persists them."""
    objective_id = state["objective_id"]
    async with AsyncSessionLocal() as db:
        tasks = await decompose_goal_llm(
            title=state["title"],
            description=state["description"],
            max_budget_usd=state["max_budget_usd"],
        )

        subtask_states = []
        for task_dict in tasks:
            subtask = Subtask(
                objective_id=uuid.UUID(objective_id),
                title=task_dict["title"],
                description=task_dict["description"],
                service_type=task_dict["service_type"],
                allocated_budget_usd=task_dict["allocated_budget_usd"],
                sequence_order=task_dict["sequence_order"],
                status="pending",
                input_payload=task_dict.get("input_payload", {}),
            )
            db.add(subtask)
            await db.commit()
            await db.refresh(subtask)

            subtask_states.append({
                "id": str(subtask.id),
                "title": subtask.title,
                "description": subtask.description,
                "service_type": subtask.service_type,
                "allocated_budget_usd": float(subtask.allocated_budget_usd),
                "sequence_order": subtask.sequence_order,
                "assigned_seller_id": None,
                "agreed_price_usd": None,
                "status": subtask.status,
                "input_payload": subtask.input_payload,
            })

        # Update objective status
        stmt = select(Objective).where(Objective.id == uuid.UUID(objective_id))
        res = await db.execute(stmt)
        obj = res.scalars().first()
        if obj:
            obj.status = "negotiating"
            await db.commit()

    await ws_manager.broadcast(objective_id, {
        "type": "SUBTASKS_DECOMPOSED",
        "objective_id": objective_id,
        "subtasks": subtask_states,
    })

    return {"subtasks": subtask_states, "current_step": "discovery"}


async def discovery_node(state: MarketplaceState) -> Dict[str, Any]:
    """LangGraph Node: Matches each decomposed subtask to a Seller Agent."""
    objective_id = state["objective_id"]
    updated_subtasks = []

    async with AsyncSessionLocal() as db:
        for st in state["subtasks"]:
            seller = await AgentMatchmaker.match_subtask_to_seller(
                db=db,
                service_type=st["service_type"],
                allocated_budget_usd=st["allocated_budget_usd"],
            )
            if seller:
                st_id = uuid.UUID(st["id"])
                stmt = select(Subtask).where(Subtask.id == st_id)
                res = await db.execute(stmt)
                db_st = res.scalars().first()
                if db_st:
                    db_st.assigned_seller_id = seller.id
                    await db.commit()
                st["assigned_seller_id"] = str(seller.id)
                st["seller_name"] = seller.name
            updated_subtasks.append(st)

    await ws_manager.broadcast(objective_id, {
        "type": "SELLERS_MATCHED",
        "objective_id": objective_id,
        "subtasks": updated_subtasks,
    })

    return {"subtasks": updated_subtasks, "current_step": "negotiation"}


async def negotiate_node(state: MarketplaceState) -> Dict[str, Any]:
    """LangGraph Node: Executes bilateral price negotiation for all subtasks."""
    objective_id = state["objective_id"]
    negotiations_map = {}
    updated_subtasks = []

    async with AsyncSessionLocal() as db:
        buyer = await MarketplaceService.get_agent_by_type(db, "buyer")
        if not buyer:
            buyer = (await MarketplaceService.get_all_agents(db))[0]

        for st in state["subtasks"]:
            st_id = uuid.UUID(st["id"])
            stmt = select(Subtask).where(Subtask.id == st_id)
            res = await db.execute(stmt)
            db_st = res.scalars().first()

            seller = await MarketplaceService.get_agent_by_id(db, uuid.UUID(st["assigned_seller_id"]))

            negotiation, agreed, final_price = await NegotiationEngine.run_negotiation(
                db=db,
                subtask=db_st,
                buyer_agent=buyer,
                seller_agent=seller,
                objective_id=objective_id,
            )

            negotiations_map[st["id"]] = {
                "negotiation_id": str(negotiation.id),
                "subtask_id": st["id"],
                "buyer_agent_id": str(buyer.id),
                "seller_agent_id": str(seller.id),
                "seller_name": seller.name,
                "final_price_usd": final_price,
                "status": "agreed" if agreed else "rejected",
            }
            st["agreed_price_usd"] = final_price
            st["status"] = "agreed" if agreed else "rejected"
            updated_subtasks.append(st)

    return {
        "subtasks": updated_subtasks,
        "negotiations": negotiations_map,
        "current_step": "contract_generation",
    }


async def contract_generation_node(state: MarketplaceState) -> Dict[str, Any]:
    """LangGraph Node: Formulates binding contracts for all successfully negotiated subtasks."""
    objective_id = state["objective_id"]
    contracts_list = []
    total_contracted = 0.0

    async with AsyncSessionLocal() as db:
        for st in state["subtasks"]:
            neg_info = state["negotiations"].get(st["id"])
            if not neg_info or neg_info["status"] != "agreed":
                continue

            agreed_amount = neg_info["final_price_usd"]
            total_contracted += agreed_amount

            terms = {
                "service_category": st["service_type"],
                "scope_of_work": st["description"],
                "acceptance_rubric": {
                    "minimum_score": 75.0,
                    "criteria": ["completeness", "depth_and_rigor", "format_and_integrity"],
                },
                "payment_rail": "PAYPAL_SANDBOX_ORDERS_V2",
                "escrow_guaranteed": True,
            }

            contract = await ContractService.create_contract(
                db=db,
                subtask_id=uuid.UUID(st["id"]),
                buyer_agent_id=uuid.UUID(neg_info["buyer_agent_id"]),
                seller_agent_id=uuid.UUID(neg_info["seller_agent_id"]),
                negotiation_id=uuid.UUID(neg_info["negotiation_id"]),
                agreed_amount_usd=agreed_amount,
                terms_and_conditions=terms,
            )

            contracts_list.append({
                "contract_id": str(contract.id),
                "subtask_id": st["id"],
                "title": st["title"],
                "agreed_amount_usd": agreed_amount,
                "status": contract.status,
                "seller_name": neg_info["seller_name"],
            })

        # Update objective status to awaiting_payment
        stmt = select(Objective).where(Objective.id == uuid.UUID(objective_id))
        res = await db.execute(stmt)
        obj = res.scalars().first()
        if obj:
            obj.status = "awaiting_payment"
            await db.commit()

    await ws_manager.broadcast(objective_id, {
        "type": "CONTRACTS_GENERATED",
        "objective_id": objective_id,
        "contracts": contracts_list,
        "total_amount_usd": round(total_contracted, 2),
    })

    return {
        "contracts": contracts_list,
        "current_step": "awaiting_payment",
    }


def build_marketplace_graph():
    """Compiles the phase-1 planning graph."""
    workflow = StateGraph(MarketplaceState)

    workflow.add_node("decompose", decompose_node)
    workflow.add_node("discover", discovery_node)
    workflow.add_node("negotiate", negotiate_node)
    workflow.add_node("contract", contract_generation_node)

    workflow.set_entry_point("decompose")
    workflow.add_edge("decompose", "discover")
    workflow.add_edge("discover", "negotiate")
    workflow.add_edge("negotiate", "contract")
    workflow.add_edge("contract", END)

    return workflow.compile()


marketplace_graph = build_marketplace_graph()


async def execute_task_fulfillment(objective_id: str):
    """Executes Seller Agent tools, Buyer Agent evaluation, and Ledger settlement after PayPal payment capture."""
    async with AsyncSessionLocal() as db:
        # Retrieve all funded/active contracts for this objective
        contracts = await ContractService.get_by_objective(db, uuid.UUID(objective_id))
        buyer = await MarketplaceService.get_agent_by_type(db, "buyer")

        research_content = None
        analysis_content = None

        # Sort contracts by subtask sequence
        # Execute sequentially or in dependency order
        for contract in contracts:
            subtask = contract.subtask
            seller = contract.seller_agent

            await ws_manager.broadcast(objective_id, {
                "type": "EXECUTION_STARTED",
                "contract_id": str(contract.id),
                "subtask_id": str(subtask.id),
                "seller_name": seller.name,
                "service_type": subtask.service_type,
            })

            # Execute specialized toolchain
            if subtask.service_type == "research":
                result = await ResearchAgentExecutor.execute(subtask.title, subtask.input_payload)
                research_content = result["content"]
            elif subtask.service_type == "analysis":
                result = await AnalysisAgentExecutor.execute(subtask.title, subtask.input_payload, research_content)
                analysis_content = result["content"]
            else:  # report
                result = await ReportAgentExecutor.execute(subtask.title, subtask.input_payload, research_content, analysis_content)

            # Persist Deliverable
            deliverable = Deliverable(
                contract_id=contract.id,
                seller_agent_id=seller.id,
                artifact_type=result["artifact_type"],
                content=result["content"],
                checksum=result["checksum"],
                execution_duration_ms=result["execution_duration_ms"],
            )
            db.add(deliverable)
            await db.commit()
            await db.refresh(deliverable)

            await ws_manager.broadcast(objective_id, {
                "type": "DELIVERABLE_SUBMITTED",
                "contract_id": str(contract.id),
                "subtask_id": str(subtask.id),
                "artifact_type": deliverable.artifact_type,
                "checksum": deliverable.checksum,
            })

            # Buyer Agent Quality Evaluation
            score, accepted, rubric, feedback = DeliverableEvaluator.evaluate(
                subtask_title=subtask.title,
                service_type=subtask.service_type,
                artifact_type=deliverable.artifact_type,
                content=deliverable.content,
                checksum=deliverable.checksum,
            )

            evaluation = Evaluation(
                deliverable_id=deliverable.id,
                evaluator_agent_id=buyer.id if buyer else seller.id,
                rubric_scores=rubric,
                score=score,
                is_accepted=accepted,
                feedback=feedback,
            )
            db.add(evaluation)

            if accepted:
                contract.status = "completed"
                subtask.status = "accepted"
                # Settle internal ledger payout
                await LedgerService.settle_contract_payout(
                    db=db,
                    contract_id=contract.id,
                    seller_agent_name=seller.name,
                    total_amount_usd=float(contract.agreed_amount_usd),
                )
            else:
                contract.status = "disputed"
                subtask.status = "rejected"

            await db.commit()

            await ws_manager.broadcast(objective_id, {
                "type": "EVALUATION_COMPLETED",
                "contract_id": str(contract.id),
                "subtask_id": str(subtask.id),
                "score": score,
                "is_accepted": accepted,
                "feedback": feedback,
            })

        # Mark Objective completed
        stmt = select(Objective).where(Objective.id == uuid.UUID(objective_id))
        res = await db.execute(stmt)
        obj = res.scalars().first()
        if obj:
            obj.status = "completed"
            await db.commit()

        await ws_manager.broadcast(objective_id, {
            "type": "OBJECTIVE_COMPLETED",
            "objective_id": objective_id,
            "status": "completed",
        })
