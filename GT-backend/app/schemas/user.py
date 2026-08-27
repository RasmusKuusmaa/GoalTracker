import uuid
from datetime import datetime

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: str
    timezone: str
    week_start: int = 1


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    timezone: str
    week_start: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = None
    timezone: str | None = None
    week_start: int | None = None
