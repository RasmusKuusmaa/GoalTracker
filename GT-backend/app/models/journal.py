import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy import Uuid as SAUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SyncMixin, TimestampMixin


class JournalKind(enum.StrEnum):
    text = "text"
    numeric = "numeric"


class Journal(Base, TimestampMixin, SyncMixin):
    __tablename__ = "journals"

    id: Mapped[uuid.UUID] = mapped_column(SAUuid, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(SAUuid, ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    kind: Mapped[JournalKind] = mapped_column(SAEnum(JournalKind, name="journal_kind"))
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
