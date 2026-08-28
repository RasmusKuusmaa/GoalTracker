import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import Journal
from app.schemas.journal import JournalCreate, JournalUpdate


async def create_journal(
    session: AsyncSession, user_id: uuid.UUID, payload: JournalCreate
) -> Journal:
    journal = Journal(
        id=payload.id,
        user_id=user_id,
        name=payload.name,
        kind=payload.kind,
        unit=payload.unit,
        sort_order=payload.sort_order,
    )
    session.add(journal)
    await session.commit()
    await session.refresh(journal)
    return journal


async def get_owned_journal(
    session: AsyncSession, user_id: uuid.UUID, journal_id: uuid.UUID
) -> Journal:
    journal = await session.scalar(
        select(Journal).where(
            Journal.id == journal_id,
            Journal.user_id == user_id,
            Journal.deleted_at.is_(None),
        )
    )
    if journal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "journal not found")
    return journal


async def update_journal(
    session: AsyncSession, user_id: uuid.UUID, journal_id: uuid.UUID, payload: JournalUpdate
) -> Journal:
    journal = await get_owned_journal(session, user_id, journal_id)
    changes = payload.model_dump(exclude_unset=True)

    for field, value in changes.items():
        setattr(journal, field, value)

    await session.commit()
    await session.refresh(journal)
    return journal


async def soft_delete_journal(
    session: AsyncSession, user_id: uuid.UUID, journal_id: uuid.UUID
) -> None:
    journal = await get_owned_journal(session, user_id, journal_id)
    journal.deleted_at = datetime.now(UTC)
    await session.commit()
