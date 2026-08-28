import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.journal import Journal, JournalKind
from app.models.user import User


async def test_change_seq_bumps_on_update(db_session: AsyncSession) -> None:
    user = User(
        email="sync-mixin@example.com",
        password_hash="hash",
        display_name="Sync Mixin",
        timezone="UTC",
        week_start=1,
    )
    db_session.add(user)
    await db_session.flush()

    journal = Journal(id=uuid.uuid4(), user_id=user.id, name="Original", kind=JournalKind.text)
    db_session.add(journal)
    await db_session.commit()
    await db_session.refresh(journal)

    first_seq = journal.change_seq

    journal.name = "Renamed"
    await db_session.commit()
    await db_session.refresh(journal)

    assert journal.change_seq > first_seq
