import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.goal import GoalStatus


class GoalCreate(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    target_date: date | None = None
    sort_order: int = 0


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    target_date: date | None = None
    parent_id: uuid.UUID | None = None
    sort_order: int | None = None


class GoalRead(BaseModel):
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

    model_config = {"from_attributes": True}
