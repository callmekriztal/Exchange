import asyncio
import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.agents.graph import marketplace_graph
from app.core.database import get_db
from app.models.objective import Objective, Subtask
from app.models.user import User
from app.schemas.objective import ObjectiveCreate, ObjectiveResponse, SubtaskResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/objectives", tags=["Objectives"])


async def run_objective_workflow_background(objective_id: str, user_id: str, title: str, description: str, max_budget_usd: float):
    initial_state = {
        "objective_id": objective_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "max_budget_usd": max_budget_usd,
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


@router.post("", response_model=ObjectiveResponse, status_code=status.HTTP_201_CREATED)
async def create_objective(
    data: ObjectiveCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    objective = Objective(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        max_budget_usd=data.max_budget_usd,
        status="planning",
    )
    db.add(objective)
    await db.commit()
    await db.refresh(objective)

    # Launch autonomous agent workflow in background
    background_tasks.add_task(
        run_objective_workflow_background,
        str(objective.id),
        str(current_user.id),
        objective.title,
        objective.description,
        float(objective.max_budget_usd),
    )

    return objective


@router.get("", response_model=List[ObjectiveResponse])
async def list_objectives(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Objective)
        .options(selectinload(Objective.subtasks))
        .where(Objective.user_id == current_user.id)
        .order_by(Objective.created_at.desc())
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.get("/{objective_id}", response_model=ObjectiveResponse)
async def get_objective(
    objective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Objective)
        .options(selectinload(Objective.subtasks))
        .where(Objective.id == objective_id, Objective.user_id == current_user.id)
    )
    res = await db.execute(stmt)
    obj = res.scalars().first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objective not found")
    return obj
