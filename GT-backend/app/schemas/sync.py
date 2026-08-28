import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.commitment import CommitmentCadence, CommitmentComparator, CommitmentType
from app.models.completion import CompletionStatus
from app.models.goal import GoalStatus
from app.models.journal import JournalKind

# Sync rows carry every field needed for both directions of the sync protocol: `updated_at`
# for last-write-wins conflict resolution and `deleted_at` to propagate tombstones. The
# REST `*Read`/`*Create` schemas omit one or both of these, so each entity gets its own
# row shape here rather than reusing them.


class GoalSyncRow(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    parent_id: uuid.UUID | None
    title: str
    description: str | None
    target_date: date | None
    status: GoalStatus
    completed_at: datetime | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class CommitmentSyncRow(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    goal_id: uuid.UUID | None
    journal_id: uuid.UUID | None
    title: str
    type: CommitmentType
    cadence: CommitmentCadence
    target_count: int | None
    target_value: Decimal | None
    comparator: CommitmentComparator | None
    unit: str | None
    active_from: date
    active_until: date | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class CompletionSyncRow(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    commitment_id: uuid.UUID
    local_date: date
    status: CompletionStatus
    value: Decimal | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class JournalSyncRow(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    kind: JournalKind
    unit: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class JournalEntrySyncRow(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    journal_id: uuid.UUID
    local_date: date
    body: str | None
    value: Decimal | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class SyncPullResponse(BaseModel):
    goals: list[GoalSyncRow] = Field(default_factory=list)
    commitments: list[CommitmentSyncRow] = Field(default_factory=list)
    completions: list[CompletionSyncRow] = Field(default_factory=list)
    journals: list[JournalSyncRow] = Field(default_factory=list)
    journal_entries: list[JournalEntrySyncRow] = Field(default_factory=list)
    cursor: str
    has_more: bool


class SyncPushRequest(BaseModel):
    goals: list[GoalSyncRow] = Field(default_factory=list)
    commitments: list[CommitmentSyncRow] = Field(default_factory=list)
    completions: list[CompletionSyncRow] = Field(default_factory=list)
    journals: list[JournalSyncRow] = Field(default_factory=list)
    journal_entries: list[JournalEntrySyncRow] = Field(default_factory=list)


class SyncPushResponse(BaseModel):
    goals: list[GoalSyncRow] = Field(default_factory=list)
    commitments: list[CommitmentSyncRow] = Field(default_factory=list)
    completions: list[CompletionSyncRow] = Field(default_factory=list)
    journals: list[JournalSyncRow] = Field(default_factory=list)
    journal_entries: list[JournalEntrySyncRow] = Field(default_factory=list)
