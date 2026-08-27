import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, text
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Uuid as SAUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SyncMixin, TimestampMixin


class CompletionStatus(enum.StrEnum):
    done = "done"
    skipped = "skipped"


class Completion(Base, TimestampMixin, SyncMixin):
    __tablename__ = "completions"
    __table_args__ = (
        Index(
            "ix_completions_commitment_id_local_date",
            "commitment_id",
            "local_date",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
            sqlite_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(SAUuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("users.id"))
    commitment_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("commitments.id"))
    local_date: Mapped[date] = mapped_column(Date)
    status: Mapped[CompletionStatus] = mapped_column(
        SAEnum(CompletionStatus, name="completion_status")
    )
    value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
