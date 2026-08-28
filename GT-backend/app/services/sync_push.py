import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.completion import Completion
from app.models.goal import Goal
from app.models.journal import Journal
from app.models.journal_entry import JournalEntry
from app.schemas.sync import (
    CommitmentSyncRow,
    CompletionSyncRow,
    GoalSyncRow,
    JournalEntrySyncRow,
    JournalSyncRow,
    SyncPushRequest,
    SyncPushResponse,
)


def _is_newer(incoming: datetime, current: datetime) -> bool:
    # SQLite (used only in tests) returns naive datetimes even for tz-aware columns,
    # unlike Postgres, which always round-trips DateTime(timezone=True) as aware.
    if incoming.tzinfo is None:
        incoming = incoming.replace(tzinfo=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return incoming > current


async def _apply_goal(session: AsyncSession, row: GoalSyncRow) -> Goal:
    existing = await session.get(Goal, row.id)
    if existing is None:
        goal = Goal(
            id=row.id,
            user_id=row.user_id,
            parent_id=row.parent_id,
            title=row.title,
            description=row.description,
            target_date=row.target_date,
            status=row.status,
            completed_at=row.completed_at,
            sort_order=row.sort_order,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
        session.add(goal)
        return goal
    if existing.user_id != row.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")
    if not _is_newer(row.updated_at, existing.updated_at):
        return existing
    existing.parent_id = row.parent_id
    existing.title = row.title
    existing.description = row.description
    existing.target_date = row.target_date
    existing.status = row.status
    existing.completed_at = row.completed_at
    existing.sort_order = row.sort_order
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at
    return existing


async def _apply_commitment(session: AsyncSession, row: CommitmentSyncRow) -> Commitment:
    existing = await session.get(Commitment, row.id)
    if existing is None:
        commitment = Commitment(
            id=row.id,
            user_id=row.user_id,
            goal_id=row.goal_id,
            journal_id=row.journal_id,
            title=row.title,
            type=row.type,
            cadence=row.cadence,
            target_count=row.target_count,
            target_value=row.target_value,
            comparator=row.comparator,
            unit=row.unit,
            active_from=row.active_from,
            active_until=row.active_until,
            archived_at=row.archived_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
        session.add(commitment)
        return commitment
    if existing.user_id != row.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")
    if not _is_newer(row.updated_at, existing.updated_at):
        return existing
    existing.goal_id = row.goal_id
    existing.journal_id = row.journal_id
    existing.title = row.title
    existing.type = row.type
    existing.cadence = row.cadence
    existing.target_count = row.target_count
    existing.target_value = row.target_value
    existing.comparator = row.comparator
    existing.unit = row.unit
    existing.active_from = row.active_from
    existing.active_until = row.active_until
    existing.archived_at = row.archived_at
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at
    return existing


async def _apply_completion(session: AsyncSession, row: CompletionSyncRow) -> Completion:
    existing = await session.get(Completion, row.id)
    if existing is None:
        completion = Completion(
            id=row.id,
            user_id=row.user_id,
            commitment_id=row.commitment_id,
            local_date=row.local_date,
            status=row.status,
            value=row.value,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
        session.add(completion)
        return completion
    if existing.user_id != row.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")
    if not _is_newer(row.updated_at, existing.updated_at):
        return existing
    existing.commitment_id = row.commitment_id
    existing.local_date = row.local_date
    existing.status = row.status
    existing.value = row.value
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at
    return existing


async def _apply_journal(session: AsyncSession, row: JournalSyncRow) -> Journal:
    existing = await session.get(Journal, row.id)
    if existing is None:
        journal = Journal(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            kind=row.kind,
            unit=row.unit,
            sort_order=row.sort_order,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
        session.add(journal)
        return journal
    if existing.user_id != row.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")
    if not _is_newer(row.updated_at, existing.updated_at):
        return existing
    existing.name = row.name
    existing.kind = row.kind
    existing.unit = row.unit
    existing.sort_order = row.sort_order
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at
    return existing


async def _apply_journal_entry(session: AsyncSession, row: JournalEntrySyncRow) -> JournalEntry:
    existing = await session.get(JournalEntry, row.id)
    if existing is None:
        entry = JournalEntry(
            id=row.id,
            user_id=row.user_id,
            journal_id=row.journal_id,
            local_date=row.local_date,
            body=row.body,
            value=row.value,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )
        session.add(entry)
        return entry
    if existing.user_id != row.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")
    if not _is_newer(row.updated_at, existing.updated_at):
        return existing
    existing.journal_id = row.journal_id
    existing.local_date = row.local_date
    existing.body = row.body
    existing.value = row.value
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at
    return existing


def _assert_user_scoped(user_id: uuid.UUID, payload: SyncPushRequest) -> None:
    rows: list[
        GoalSyncRow | CommitmentSyncRow | CompletionSyncRow | JournalSyncRow | JournalEntrySyncRow
    ] = [
        *payload.goals,
        *payload.commitments,
        *payload.completions,
        *payload.journals,
        *payload.journal_entries,
    ]
    if any(row.user_id != user_id for row in rows):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "cannot push rows owned by another user")


async def push_sync(
    session: AsyncSession, user_id: uuid.UUID, payload: SyncPushRequest
) -> SyncPushResponse:
    _assert_user_scoped(user_id, payload)

    goals = [await _apply_goal(session, row) for row in payload.goals]
    commitments = [await _apply_commitment(session, row) for row in payload.commitments]
    completions = [await _apply_completion(session, row) for row in payload.completions]
    journals = [await _apply_journal(session, row) for row in payload.journals]
    journal_entries = [
        await _apply_journal_entry(session, row) for row in payload.journal_entries
    ]

    await session.commit()
    for obj in (*goals, *commitments, *completions, *journals, *journal_entries):
        await session.refresh(obj)

    return SyncPushResponse(
        goals=[GoalSyncRow.model_validate(row) for row in goals],
        commitments=[CommitmentSyncRow.model_validate(row) for row in commitments],
        completions=[CompletionSyncRow.model_validate(row) for row in completions],
        journals=[JournalSyncRow.model_validate(row) for row in journals],
        journal_entries=[JournalEntrySyncRow.model_validate(row) for row in journal_entries],
    )
