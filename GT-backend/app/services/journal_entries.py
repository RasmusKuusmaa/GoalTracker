import uuid
from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import JournalKind
from app.models.journal_entry import JournalEntry
from app.schemas.journal_entry import JournalEntryUpsert
from app.services.journals import get_owned_journal


async def upsert_journal_entry(
    session: AsyncSession, user_id: uuid.UUID, payload: JournalEntryUpsert
) -> JournalEntry:
    journal = await get_owned_journal(session, user_id, payload.journal_id)

    is_numeric = journal.kind == JournalKind.numeric
    if is_numeric and payload.value is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "value is required for numeric journals"
        )
    if not is_numeric and payload.value is not None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "value is only valid for numeric journals"
        )

    entry = await session.scalar(
        select(JournalEntry).where(
            JournalEntry.journal_id == payload.journal_id,
            JournalEntry.local_date == payload.local_date,
        )
    )
    if entry is None:
        entry = JournalEntry(
            id=payload.id,
            user_id=user_id,
            journal_id=payload.journal_id,
            local_date=payload.local_date,
        )
        session.add(entry)

    entry.body = payload.body
    entry.value = payload.value
    entry.deleted_at = None

    await session.commit()
    await session.refresh(entry)
    return entry


async def list_journal_entries(
    session: AsyncSession,
    user_id: uuid.UUID,
    journal_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> list[JournalEntry]:
    await get_owned_journal(session, user_id, journal_id)

    result = await session.scalars(
        select(JournalEntry).where(
            JournalEntry.journal_id == journal_id,
            JournalEntry.local_date >= date_from,
            JournalEntry.local_date <= date_to,
            JournalEntry.deleted_at.is_(None),
        )
    )
    return list(result)


async def get_owned_journal_entry(
    session: AsyncSession, user_id: uuid.UUID, entry_id: uuid.UUID
) -> JournalEntry:
    entry = await session.scalar(
        select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id,
            JournalEntry.deleted_at.is_(None),
        )
    )
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "journal entry not found")
    return entry


async def soft_delete_journal_entry(
    session: AsyncSession, user_id: uuid.UUID, entry_id: uuid.UUID
) -> None:
    entry = await get_owned_journal_entry(session, user_id, entry_id)
    entry.deleted_at = datetime.now(UTC)
    await session.commit()
