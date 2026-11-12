import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.agent import AgentResponse
from app.services.marketplace_service import MarketplaceService

router = APIRouter(prefix="/agents", tags=["Agent Registry"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    agents = await MarketplaceService.get_all_agents(db)
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    agent = await MarketplaceService.get_agent_by_id(db, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.post("/seed", response_model=List[AgentResponse])
async def seed_agents(db: AsyncSession = Depends(get_db)):
    agents = await MarketplaceService.seed_default_agents(db)
    return agents
