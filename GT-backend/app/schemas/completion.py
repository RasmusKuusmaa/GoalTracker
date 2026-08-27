import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.completion import CompletionStatus


class CompletionUpsert(BaseModel):
    id: uuid.UUID
    commitment_id: uuid.UUID
    local_date: date
    status: CompletionStatus
    value: Decimal | None = None


class CompletionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    commitment_id: uuid.UUID
    local_date: date
    status: CompletionStatus
    value: Decimal | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
