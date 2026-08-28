import base64
import json
import uuid

from sqlalchemy import select
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
    SyncPullResponse,
)

PAGE_SIZE = 500
ENTITY_NAMES = ("goals", "commitments", "completions", "journals", "journal_entries")


def decode_cursor(cursor: str | None) -> dict[str, int]:
    if not cursor:
        return dict.fromkeys(ENTITY_NAMES, 0)
    decoded: dict[str, int] = json.loads(base64.urlsafe_b64decode(cursor.encode()))
    return {name: decoded.get(name, 0) for name in ENTITY_NAMES}


def encode_cursor(positions: dict[str, int]) -> str:
    payload = json.dumps(positions, sort_keys=True).encode()
    return base64.urlsafe_b64encode(payload).decode()


async def pull_sync(
    session: AsyncSession, user_id: uuid.UUID, cursor: str | None
) -> SyncPullResponse:
    positions = decode_cursor(cursor)

    goal_rows = list(
        await session.scalars(
            select(Goal)
            .where(Goal.user_id == user_id, Goal.change_seq > positions["goals"])
            .order_by(Goal.change_seq)
            .limit(PAGE_SIZE + 1)
        )
    )
    goals_more = len(goal_rows) > PAGE_SIZE
    goal_rows = goal_rows[:PAGE_SIZE]
    goals_pos = goal_rows[-1].change_seq if goal_rows else positions["goals"]

    commitment_rows = list(
        await session.scalars(
            select(Commitment)
            .where(
                Commitment.user_id == user_id,
                Commitment.change_seq > positions["commitments"],
            )
            .order_by(Commitment.change_seq)
            .limit(PAGE_SIZE + 1)
        )
    )
    commitments_more = len(commitment_rows) > PAGE_SIZE
    commitment_rows = commitment_rows[:PAGE_SIZE]
    commitments_pos = (
        commitment_rows[-1].change_seq if commitment_rows else positions["commitments"]
    )

    completion_rows = list(
        await session.scalars(
            select(Completion)
            .where(
                Completion.user_id == user_id,
                Completion.change_seq > positions["completions"],
            )
            .order_by(Completion.change_seq)
            .limit(PAGE_SIZE + 1)
        )
    )
    completions_more = len(completion_rows) > PAGE_SIZE
    completion_rows = completion_rows[:PAGE_SIZE]
    completions_pos = (
        completion_rows[-1].change_seq if completion_rows else positions["completions"]
    )

    journal_rows = list(
        await session.scalars(
            select(Journal)
            .where(Journal.user_id == user_id, Journal.change_seq > positions["journals"])
            .order_by(Journal.change_seq)
            .limit(PAGE_SIZE + 1)
        )
    )
    journals_more = len(journal_rows) > PAGE_SIZE
    journal_rows = journal_rows[:PAGE_SIZE]
    journals_pos = journal_rows[-1].change_seq if journal_rows else positions["journals"]

    journal_entry_rows = list(
        await session.scalars(
            select(JournalEntry)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.change_seq > positions["journal_entries"],
            )
            .order_by(JournalEntry.change_seq)
            .limit(PAGE_SIZE + 1)
        )
    )
    journal_entries_more = len(journal_entry_rows) > PAGE_SIZE
    journal_entry_rows = journal_entry_rows[:PAGE_SIZE]
    journal_entries_pos = (
        journal_entry_rows[-1].change_seq
        if journal_entry_rows
        else positions["journal_entries"]
    )

    new_cursor = encode_cursor(
        {
            "goals": goals_pos,
            "commitments": commitments_pos,
            "completions": completions_pos,
            "journals": journals_pos,
            "journal_entries": journal_entries_pos,
        }
    )
    has_more = any(
        (goals_more, commitments_more, completions_more, journals_more, journal_entries_more)
    )

    return SyncPullResponse(
        goals=[GoalSyncRow.model_validate(row) for row in goal_rows],
        commitments=[CommitmentSyncRow.model_validate(row) for row in commitment_rows],
        completions=[CompletionSyncRow.model_validate(row) for row in completion_rows],
        journals=[JournalSyncRow.model_validate(row) for row in journal_rows],
        journal_entries=[
            JournalEntrySyncRow.model_validate(row) for row in journal_entry_rows
        ],
        cursor=new_cursor,
        has_more=has_more,
    )
