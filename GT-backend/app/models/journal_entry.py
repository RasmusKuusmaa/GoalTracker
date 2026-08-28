import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, text
from sqlalchemy import Uuid as SAUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SyncMixin, TimestampMixin


class JournalEntry(Base, TimestampMixin, SyncMixin):
    __tablename__ = "journal_entries"
    __table_args__ = (
        Index(
            "ix_journal_entries_journal_id_local_date",
            "journal_id",
            "local_date",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
            sqlite_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(SAUuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("users.id"))
    journal_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("journals.id"))
    local_date: Mapped[date] = mapped_column(Date)
    body: Mapped[str | None] = mapped_column(String, nullable=True)
    value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
