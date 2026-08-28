import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Uuid as SAUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SyncMixin, TimestampMixin


class CommitmentType(enum.StrEnum):
    binary = "binary"
    quota = "quota"
    numeric = "numeric"
    journal = "journal"


class CommitmentCadence(enum.StrEnum):
    daily = "daily"
    weekly = "weekly"


class CommitmentComparator(enum.StrEnum):
    lte = "lte"
    gte = "gte"


class Commitment(Base, TimestampMixin, SyncMixin):
    __tablename__ = "commitments"

    id: Mapped[uuid.UUID] = mapped_column(SAUuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("users.id"))
    goal_id: Mapped[uuid.UUID | None] = mapped_column(SAUuid, ForeignKey("goals.id"), nullable=True)
    journal_id: Mapped[uuid.UUID | None] = mapped_column(
        SAUuid, ForeignKey("journals.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String)
    type: Mapped[CommitmentType] = mapped_column(SAEnum(CommitmentType, name="commitment_type"))
    cadence: Mapped[CommitmentCadence] = mapped_column(
        SAEnum(CommitmentCadence, name="commitment_cadence")
    )
    target_count: Mapped[int | None] = mapped_column(nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    comparator: Mapped[CommitmentComparator | None] = mapped_column(
        SAEnum(CommitmentComparator, name="commitment_comparator"), nullable=True
    )
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    active_from: Mapped[date] = mapped_column(Date)
    active_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
