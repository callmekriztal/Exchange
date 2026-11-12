import uuid
from typing import Any, Dict, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.websocket_manager import ws_manager
from app.models.agent import Agent
from app.models.negotiation import Negotiation, NegotiationRound
from app.models.objective import Subtask


class NegotiationEngine:
    @classmethod
    async def run_negotiation(
        cls,
        db: AsyncSession,
        subtask: Subtask,
        buyer_agent: Agent,
        seller_agent: Agent,
        objective_id: str,
    ) -> Tuple[Negotiation, bool, float]:
        """Runs the 3-round alternating-offer negotiation protocol."""
        allocated_budget = float(subtask.allocated_budget_usd)
        pricing_policy = seller_agent.pricing_policy or {}
        base_price = float(pricing_policy.get("base_price", allocated_budget))
        min_price = float(pricing_policy.get("min_price", base_price * 0.70))

        # Initialize Negotiation in database
        negotiation = Negotiation(
            subtask_id=subtask.id,
            buyer_agent_id=buyer_agent.id,
            seller_agent_id=seller_agent.id,
            buyer_opening_offer_usd=round(max(min_price, allocated_budget * 0.75), 2),
            seller_opening_ask_usd=round(base_price, 2),
            max_rounds=3,
            current_round=0,
            status="active",
        )
        db.add(negotiation)
        await db.commit()
        await db.refresh(negotiation)

        agreed = False
        final_price = 0.0

        # === Round 1: Buyer Opening Offer ===
        round1_offer = float(negotiation.buyer_opening_offer_usd)
        round1_rationale = f"Buyer offers ${round1_offer:.2f} for '{subtask.title}' based on preliminary scope estimation and portfolio budget allocation."
        r1 = NegotiationRound(
            negotiation_id=negotiation.id,
            round_number=1,
            speaker_agent_id=buyer_agent.id,
            action="offer",
            proposed_price_usd=round1_offer,
            rationale=round1_rationale,
        )
        db.add(r1)
        negotiation.current_round = 1
        await db.commit()

        await ws_manager.broadcast(objective_id, {
            "type": "NEGOTIATION_ROUND",
            "subtask_id": str(subtask.id),
            "round": 1,
            "speaker": buyer_agent.name,
            "speaker_type": "buyer",
            "action": "offer",
            "proposed_price_usd": round1_offer,
            "rationale": round1_rationale,
        })

        # Check if seller accepts Round 1 immediately
        if round1_offer >= base_price:
            agreed = True
            final_price = round1_offer
            r1_accept = NegotiationRound(
                negotiation_id=negotiation.id,
                round_number=2,
                speaker_agent_id=seller_agent.id,
                action="accept",
                proposed_price_usd=final_price,
                rationale=f"Seller {seller_agent.name} accepts buyer's initial offer of ${final_price:.2f}.",
            )
            db.add(r1_accept)
            negotiation.current_round = 2
            negotiation.status = "agreed"
            negotiation.final_agreed_price_usd = final_price
            await db.commit()
            return negotiation, True, final_price

        # === Round 2: Seller Counter-Offer ===
        # Seller concedes 10% below base price, bounded by min_price
        seller_counter = round(max(min_price, base_price * 0.90), 2)
        seller_rationale = (
            f"Seller {seller_agent.name} requests ${seller_counter:.2f} reflecting domain expertise, "
            f"model token throughput, and verification requirements."
        )
        r2 = NegotiationRound(
            negotiation_id=negotiation.id,
            round_number=2,
            speaker_agent_id=seller_agent.id,
            action="counter_offer",
            proposed_price_usd=seller_counter,
            rationale=seller_rationale,
        )
        db.add(r2)
        negotiation.current_round = 2
        await db.commit()

        await ws_manager.broadcast(objective_id, {
            "type": "NEGOTIATION_ROUND",
            "subtask_id": str(subtask.id),
            "round": 2,
            "speaker": seller_agent.name,
            "speaker_type": "seller",
            "action": "counter_offer",
            "proposed_price_usd": seller_counter,
            "rationale": seller_rationale,
        })

        # === Round 3: Buyer Final Assessment ===
        if seller_counter <= allocated_budget:
            agreed = True
            final_price = seller_counter
            r3_action = "accept"
            r3_rationale = f"Buyer accepts seller's counter-offer of ${final_price:.2f} as it fits within allocated budget (${allocated_budget:.2f})."
        else:
            # Buyer offers maximum subtask budget as final offer
            final_buyer_offer = allocated_budget
            if final_buyer_offer >= min_price:
                agreed = True
                final_price = final_buyer_offer
                r3_action = "accept"
                r3_rationale = f"Buyer counters with final cap of ${final_price:.2f}. Seller reservation check satisfied."
            else:
                agreed = False
                final_price = 0.0
                r3_action = "reject"
                r3_rationale = f"Buyer final budget cap (${final_buyer_offer:.2f}) falls below seller reservation floor (${min_price:.2f}). Negotiation terminated."

        r3 = NegotiationRound(
            negotiation_id=negotiation.id,
            round_number=3,
            speaker_agent_id=buyer_agent.id,
            action=r3_action,
            proposed_price_usd=final_price,
            rationale=r3_rationale,
        )
        db.add(r3)
        negotiation.current_round = 3
        negotiation.status = "agreed" if agreed else "rejected"
        negotiation.final_agreed_price_usd = final_price if agreed else None
        await db.commit()
        await db.refresh(negotiation)

        await ws_manager.broadcast(objective_id, {
            "type": "NEGOTIATION_ROUND",
            "subtask_id": str(subtask.id),
            "round": 3,
            "speaker": buyer_agent.name,
            "speaker_type": "buyer",
            "action": r3_action,
            "proposed_price_usd": final_price,
            "rationale": r3_rationale,
        })

        return negotiation, agreed, final_price
