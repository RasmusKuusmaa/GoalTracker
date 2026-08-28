import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.journal import JournalKind


class JournalCreate(BaseModel):
    id: uuid.UUID
    name: str
    kind: JournalKind
    unit: str | None = None
    sort_order: int = 0


class JournalUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    sort_order: int | None = None


class JournalRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    kind: JournalKind
    unit: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
