import uuid

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
)


async def _apply_goal(session: AsyncSession, row: GoalSyncRow) -> None:
    existing = await session.get(Goal, row.id)
    if existing is None:
        session.add(
            Goal(
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
        )
        return
    if row.updated_at <= existing.updated_at:
        return
    existing.parent_id = row.parent_id
    existing.title = row.title
    existing.description = row.description
    existing.target_date = row.target_date
    existing.status = row.status
    existing.completed_at = row.completed_at
    existing.sort_order = row.sort_order
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at


async def _apply_commitment(session: AsyncSession, row: CommitmentSyncRow) -> None:
    existing = await session.get(Commitment, row.id)
    if existing is None:
        session.add(
            Commitment(
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
        )
        return
    if row.updated_at <= existing.updated_at:
        return
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


async def _apply_completion(session: AsyncSession, row: CompletionSyncRow) -> None:
    existing = await session.get(Completion, row.id)
    if existing is None:
        session.add(
            Completion(
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
        )
        return
    if row.updated_at <= existing.updated_at:
        return
    existing.commitment_id = row.commitment_id
    existing.local_date = row.local_date
    existing.status = row.status
    existing.value = row.value
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at


async def _apply_journal(session: AsyncSession, row: JournalSyncRow) -> None:
    existing = await session.get(Journal, row.id)
    if existing is None:
        session.add(
            Journal(
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
        )
        return
    if row.updated_at <= existing.updated_at:
        return
    existing.name = row.name
    existing.kind = row.kind
    existing.unit = row.unit
    existing.sort_order = row.sort_order
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at


async def _apply_journal_entry(session: AsyncSession, row: JournalEntrySyncRow) -> None:
    existing = await session.get(JournalEntry, row.id)
    if existing is None:
        session.add(
            JournalEntry(
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
        )
        return
    if row.updated_at <= existing.updated_at:
        return
    existing.journal_id = row.journal_id
    existing.local_date = row.local_date
    existing.body = row.body
    existing.value = row.value
    existing.updated_at = row.updated_at
    existing.deleted_at = row.deleted_at


async def push_sync(session: AsyncSession, user_id: uuid.UUID, payload: SyncPushRequest) -> None:
    for goal_row in payload.goals:
        await _apply_goal(session, goal_row)
    for commitment_row in payload.commitments:
        await _apply_commitment(session, commitment_row)
    for completion_row in payload.completions:
        await _apply_completion(session, completion_row)
    for journal_row in payload.journals:
        await _apply_journal(session, journal_row)
    for journal_entry_row in payload.journal_entries:
        await _apply_journal_entry(session, journal_entry_row)
    await session.commit()
