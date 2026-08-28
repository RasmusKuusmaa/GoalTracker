import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.journal import Journal
from app.models.user import User
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.services.journals import create_journal, soft_delete_journal, update_journal

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("", response_model=JournalRead, status_code=status.HTTP_201_CREATED)
async def create_journal_endpoint(
    payload: JournalCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Journal:
    return await create_journal(session, current_user.id, payload)


@router.get("", response_model=list[JournalRead])
async def list_journals(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Journal]:
    query = select(Journal).where(
        Journal.user_id == current_user.id, Journal.deleted_at.is_(None)
    )
    result = await session.scalars(query)
    return list(result)


@router.patch("/{journal_id}", response_model=JournalRead)
async def patch_journal(
    journal_id: uuid.UUID,
    payload: JournalUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Journal:
    return await update_journal(session, current_user.id, journal_id, payload)


@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal(
    journal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await soft_delete_journal(session, current_user.id, journal_id)
