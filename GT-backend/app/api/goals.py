import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalRead
from app.services.goals import create_goal, get_owned_goal

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
async def create_goal_endpoint(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> GoalRead:
    goal = await create_goal(session, current_user.id, payload)
    return GoalRead.model_validate(goal)


@router.get("", response_model=list[GoalRead])
async def list_goals(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Goal]:
    result = await session.scalars(
        select(Goal).where(Goal.user_id == current_user.id, Goal.deleted_at.is_(None))
    )
    return list(result)


@router.get("/{goal_id}", response_model=GoalRead)
async def get_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Goal:
    return await get_owned_goal(session, current_user.id, goal_id)
