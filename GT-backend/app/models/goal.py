import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Uuid as SAUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SyncMixin, TimestampMixin


class GoalStatus(enum.StrEnum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class Goal(Base, TimestampMixin, SyncMixin):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(SAUuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("users.id"), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        SAUuid, ForeignKey("goals.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(
        SAEnum(GoalStatus, name="goal_status"), default=GoalStatus.active
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
