import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.goal import Goal
from app.schemas.commitment import CommitmentCreate


async def assert_valid_goal(session: AsyncSession, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
    goal = await session.scalar(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id, Goal.deleted_at.is_(None))
    )
    if goal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "goal not found")


async def create_commitment(
    session: AsyncSession, user_id: uuid.UUID, payload: CommitmentCreate
) -> Commitment:
    if payload.goal_id is not None:
        await assert_valid_goal(session, user_id, payload.goal_id)

    commitment = Commitment(
        id=payload.id,
        user_id=user_id,
        goal_id=payload.goal_id,
        journal_id=payload.journal_id,
        title=payload.title,
        type=payload.type,
        cadence=payload.cadence,
        target_count=payload.target_count,
        target_value=payload.target_value,
        comparator=payload.comparator,
        unit=payload.unit,
        active_from=payload.active_from,
        active_until=payload.active_until,
    )
    session.add(commitment)
    await session.commit()
    await session.refresh(commitment)
    return commitment
