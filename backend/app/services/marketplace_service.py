import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.agent import Agent, AgentService
from app.models.user import User
from app.core.security import get_password_hash


class MarketplaceService:
    @staticmethod
    async def get_all_agents(db: AsyncSession) -> List[Agent]:
        stmt = select(Agent).options(selectinload(Agent.services)).where(Agent.is_active == True)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_agent_by_id(db: AsyncSession, agent_id: uuid.UUID) -> Optional[Agent]:
        stmt = select(Agent).options(selectinload(Agent.services)).where(Agent.id == agent_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_agent_by_type(db: AsyncSession, agent_type: str) -> Optional[Agent]:
        stmt = select(Agent).options(selectinload(Agent.services)).where(Agent.agent_type == agent_type, Agent.is_active == True)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def find_sellers_for_category(db: AsyncSession, category: str) -> List[Agent]:
        stmt = (
            select(Agent)
            .join(AgentService)
            .options(selectinload(Agent.services))
            .where(
                Agent.is_active == True,
                Agent.agent_type != "buyer",
                AgentService.service_category == category,
                AgentService.is_available == True,
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def seed_default_agents(cls, db: AsyncSession) -> List[Agent]:
        # Ensure a system/admin user exists to own default agents
        stmt = select(User).where(User.email == "system@ai-economy.com")
        res = await db.execute(stmt)
        system_user = res.scalars().first()

        if not system_user:
            system_user = User(
                email="system@ai-economy.com",
                hashed_password=get_password_hash("SystemAdminPassword123!"),
                role="admin",
            )
            db.add(system_user)
            await db.commit()
            await db.refresh(system_user)

        # Check existing agents
        existing_agents = await cls.get_all_agents(db)
        if len(existing_agents) >= 4:
            return existing_agents

        # Seed 1: Buyer Agent
        buyer_agent = Agent(
            owner_user_id=system_user.id,
            name="Apex Buyer Agent",
            agent_type="buyer",
            description="Decomposes high-level objectives into actionable subtasks, discovers competitive sellers, negotiates fair prices, and evaluates deliverables against objective rubrics.",
            system_prompt_template="You are the Apex Buyer Agent. Your objective is to achieve the user's strategic goals within budget constraints.",
            capabilities=["task_decomposition", "seller_discovery", "price_negotiation", "deliverable_evaluation"],
            pricing_policy={"model": "buyer_orchestrator", "fee_rate": 0.00},
        )

        # Seed 2: Research Agent
        research_agent = Agent(
            owner_user_id=system_user.id,
            name="Veritas Research Agent",
            agent_type="research",
            description="Specializes in comprehensive web investigations, factual data extraction, citation verification, and structured intelligence synthesis.",
            system_prompt_template="You are the Veritas Research Agent. You gather objective facts, primary sources, and verified market signals.",
            capabilities=["web_research", "source_verification", "fact_extraction"],
            pricing_policy={"model": "unit_fixed", "base_price": 4.00, "min_price": 2.50, "max_price": 6.00},
        )
        research_service = AgentService(
            service_name="Market & Academic Web Research",
            service_category="research",
            description="Performs in-depth research on specified subjects, extracting verified facts, statistics, and citations into structured JSON.",
            base_price_usd=4.00,
            min_price_usd=2.50,
            max_price_usd=6.00,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}, "depth": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"findings": {"type": "array"}, "sources": {"type": "array"}}},
        )
        research_agent.services.append(research_service)

        # Seed 3: Analysis Agent
        analysis_agent = Agent(
            owner_user_id=system_user.id,
            name="QuantMatrix Analysis Agent",
            agent_type="analysis",
            description="Performs quantitative calculations, statistical modeling, CAGR projections, KPI trend analysis, and anomaly detection.",
            system_prompt_template="You are the QuantMatrix Analysis Agent. You specialize in quantitative mathematics, trends, and analytical insights.",
            capabilities=["statistical_analysis", "cagr_calculation", "trend_projection", "metrics_synthesis"],
            pricing_policy={"model": "dataset_fixed", "base_price": 5.00, "min_price": 3.00, "max_price": 7.50},
        )
        analysis_service = AgentService(
            service_name="Quantitative Trend & Data Analysis",
            service_category="analysis",
            description="Analyzes structured datasets or research inputs to compute trends, CAGRs, variance, and analytical insights.",
            base_price_usd=5.00,
            min_price_usd=3.00,
            max_price_usd=7.50,
            input_schema={"type": "object", "properties": {"data_points": {"type": "array"}, "metrics": {"type": "array"}}},
            output_schema={"type": "object", "properties": {"cagr": {"type": "number"}, "insights": {"type": "array"}}},
        )
        analysis_agent.services.append(analysis_service)

        # Seed 4: Report Agent
        report_agent = Agent(
            owner_user_id=system_user.id,
            name="Executive Brief Report Agent",
            agent_type="report",
            description="Synthesizes multi-source research, quantitative metrics, and conclusions into executive-grade structured markdown reports.",
            system_prompt_template="You are the Executive Brief Report Agent. You produce compelling, structured executive summaries and reports.",
            capabilities=["report_synthesis", "markdown_formatting", "executive_summary"],
            pricing_policy={"model": "deliverable_fixed", "base_price": 6.00, "min_price": 4.00, "max_price": 9.00},
        )
        report_service = AgentService(
            service_name="Executive Brief Compilation",
            service_category="report",
            description="Compiles research and analytical findings into polished, publication-ready markdown with executive summaries and visual structure.",
            base_price_usd=6.00,
            min_price_usd=4.00,
            max_price_usd=9.00,
            input_schema={"type": "object", "properties": {"research_data": {"type": "object"}, "analysis_data": {"type": "object"}}},
            output_schema={"type": "object", "properties": {"title": {"type": "string"}, "markdown_report": {"type": "string"}}},
        )
        report_agent.services.append(report_service)

        db.add_all([buyer_agent, research_agent, analysis_agent, report_agent])
        await db.commit()

        return await cls.get_all_agents(db)
