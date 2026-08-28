from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.journal_entry import JournalEntry
from app.models.user import User
from app.schemas.journal_entry import JournalEntryRead, JournalEntryUpsert
from app.services.journal_entries import upsert_journal_entry

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.put("", response_model=JournalEntryRead)
async def upsert_journal_entry_endpoint(
    payload: JournalEntryUpsert,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> JournalEntry:
    return await upsert_journal_entry(session, current_user.id, payload)
