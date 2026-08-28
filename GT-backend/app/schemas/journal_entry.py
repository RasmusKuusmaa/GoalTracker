import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class JournalEntryUpsert(BaseModel):
    id: uuid.UUID
    journal_id: uuid.UUID
    local_date: date
    body: str | None = None
    value: Decimal | None = None


class JournalEntryRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    journal_id: uuid.UUID
    local_date: date
    body: str | None
    value: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
