import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal
from app.schemas.goal import GoalCreate

MAX_GOAL_DEPTH = 5


async def get_owned_goal(session: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
    goal = await session.scalar(
        select(Goal).where(
            Goal.id == goal_id, Goal.user_id == user_id, Goal.deleted_at.is_(None)
        )
    )
    if goal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "goal not found")
    return goal


async def depth_of(session: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID) -> int:
    depth = 1
    ancestor_id: uuid.UUID | None = await session.scalar(
        select(Goal.parent_id).where(Goal.id == goal_id, Goal.user_id == user_id)
    )
    while ancestor_id is not None:
        depth += 1
        ancestor_id = await session.scalar(
            select(Goal.parent_id).where(Goal.id == ancestor_id, Goal.user_id == user_id)
        )
    return depth


async def assert_no_cycle(
    session: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID, parent_id: uuid.UUID
) -> None:
    if parent_id == goal_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "a goal cannot be its own parent")

    ancestor_id: uuid.UUID | None = parent_id
    while ancestor_id is not None:
        if ancestor_id == goal_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "a goal cannot be its own ancestor")
        ancestor_id = await session.scalar(
            select(Goal.parent_id).where(Goal.id == ancestor_id, Goal.user_id == user_id)
        )


async def create_goal(session: AsyncSession, user_id: uuid.UUID, payload: GoalCreate) -> Goal:
    if payload.parent_id is not None:
        parent = await session.scalar(
            select(Goal).where(
                Goal.id == payload.parent_id,
                Goal.user_id == user_id,
                Goal.deleted_at.is_(None),
            )
        )
        if parent is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "parent goal not found")
        await assert_no_cycle(session, user_id, payload.id, payload.parent_id)
        if await depth_of(session, user_id, payload.parent_id) + 1 > MAX_GOAL_DEPTH:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "goal tree depth limit exceeded")

    goal = Goal(
        id=payload.id,
        user_id=user_id,
        parent_id=payload.parent_id,
        title=payload.title,
        description=payload.description,
        target_date=payload.target_date,
        sort_order=payload.sort_order,
    )
    session.add(goal)
    await session.commit()
    await session.refresh(goal)
    return goal
