from collections.abc import AsyncIterator
from itertools import count

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as create_test_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base, SyncMixin
from app.db.session import get_session
from app.main import app
from app.models import (  # noqa: F401  ensure models are registered on Base.metadata
    commitment,
    completion,
    goal,
    journal,
    journal_entry,
    user,
)

# SQLite has no equivalent to Postgres's Identity()/bigserial for a non-primary-key
# column, so change_seq is never populated by the database itself under the sqlite
# test fixture. Assign it client-side here, sqlite only; Postgres keeps generating it
# server-side via Identity(always=True) untouched.
_sqlite_change_seq = count(1)


@event.listens_for(SyncMixin, "before_insert", propagate=True)
def _assign_sqlite_change_seq(mapper: object, connection: AsyncConnection, target: object) -> None:
    if connection.dialect.name == "sqlite" and getattr(target, "change_seq", None) is None:
        target.change_seq = next(_sqlite_change_seq)  # type: ignore[attr-defined]


@pytest_asyncio.fixture
async def db_connection() -> AsyncIterator[AsyncConnection]:
    engine = create_test_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(bind=db_connection, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
