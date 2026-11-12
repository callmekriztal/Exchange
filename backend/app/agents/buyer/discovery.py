import uuid
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent import Agent
from app.services.marketplace_service import MarketplaceService


class AgentMatchmaker:
    @staticmethod
    async def match_subtask_to_seller(
        db: AsyncSession,
        service_type: str,
        allocated_budget_usd: float,
    ) -> Optional[Agent]:
        """Finds eligible seller agents whose services match the subtask category and budget."""
        candidates = await MarketplaceService.find_sellers_for_category(db, service_type)
        if not candidates:
            # Fallback by agent_type directly
            candidate = await MarketplaceService.get_agent_by_type(db, service_type)
            return candidate

        # Prioritize candidates whose min_price <= allocated_budget
        best_match = None
        for agent in candidates:
            policy = agent.pricing_policy or {}
            min_price = policy.get("min_price", 0.0)
            if min_price <= allocated_budget_usd:
                best_match = agent
                break

        return best_match or candidates[0]
