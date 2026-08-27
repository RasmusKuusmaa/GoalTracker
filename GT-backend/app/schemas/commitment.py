import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, model_validator

from app.models.commitment import CommitmentCadence, CommitmentComparator, CommitmentType


class CommitmentCreate(BaseModel):
    id: uuid.UUID
    goal_id: uuid.UUID | None = None
    journal_id: uuid.UUID | None = None
    title: str
    type: CommitmentType
    cadence: CommitmentCadence
    target_count: int | None = None
    target_value: Decimal | None = None
    comparator: CommitmentComparator | None = None
    unit: str | None = None
    active_from: date
    active_until: date | None = None

    @model_validator(mode="after")
    def check_type_rules(self) -> "CommitmentCreate":
        if self.type == CommitmentType.quota and self.cadence == CommitmentCadence.daily:
            raise ValueError("quota commitments cannot have a daily cadence")
        if self.type == CommitmentType.quota and self.target_count is None:
            raise ValueError("quota commitments require target_count")
        if self.type == CommitmentType.numeric and (
            self.target_value is None or self.comparator is None
        ):
            raise ValueError("numeric commitments require target_value and comparator")
        if self.type == CommitmentType.journal and self.journal_id is None:
            raise ValueError("journal commitments require journal_id")
        return self


class CommitmentUpdate(BaseModel):
    title: str | None = None
    goal_id: uuid.UUID | None = None
    journal_id: uuid.UUID | None = None
    target_count: int | None = None
    target_value: Decimal | None = None
    comparator: CommitmentComparator | None = None
    unit: str | None = None
    active_from: date | None = None
    active_until: date | None = None


class CommitmentRead(BaseModel):
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

    model_config = {"from_attributes": True}
