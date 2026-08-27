import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.goal import Goal
from app.schemas.commitment import CommitmentCreate, CommitmentUpdate


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


async def get_owned_commitment(
    session: AsyncSession, user_id: uuid.UUID, commitment_id: uuid.UUID
) -> Commitment:
    commitment = await session.scalar(
        select(Commitment).where(
            Commitment.id == commitment_id,
            Commitment.user_id == user_id,
            Commitment.deleted_at.is_(None),
        )
    )
    if commitment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "commitment not found")
    return commitment


async def update_commitment(
    session: AsyncSession, user_id: uuid.UUID, commitment_id: uuid.UUID, payload: CommitmentUpdate
) -> Commitment:
    commitment = await get_owned_commitment(session, user_id, commitment_id)
    changes = payload.model_dump(exclude_unset=True)

    if "goal_id" in changes and changes["goal_id"] is not None:
        await assert_valid_goal(session, user_id, changes["goal_id"])

    for field, value in changes.items():
        setattr(commitment, field, value)

    await session.commit()
    await session.refresh(commitment)
    return commitment
