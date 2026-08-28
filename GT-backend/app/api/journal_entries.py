import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.journal_entry import JournalEntry
from app.models.user import User
from app.schemas.journal_entry import JournalEntryRead, JournalEntryUpsert
from app.services.journal_entries import (
    list_journal_entries,
    soft_delete_journal_entry,
    upsert_journal_entry,
)

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.put("", response_model=JournalEntryRead)
async def upsert_journal_entry_endpoint(
    payload: JournalEntryUpsert,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JournalEntry:
    return await upsert_journal_entry(session, current_user.id, payload)


@router.get("", response_model=list[JournalEntryRead])
async def list_journal_entries_endpoint(
    journal_id: uuid.UUID,
    from_: date = Query(alias="from"),
    to: date = Query(),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[JournalEntry]:
    return await list_journal_entries(session, current_user.id, journal_id, from_, to)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await soft_delete_journal_entry(session, current_user.id, entry_id)
