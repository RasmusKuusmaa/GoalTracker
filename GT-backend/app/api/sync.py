from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.schemas.sync import SyncPullResponse, SyncPushRequest
from app.services.sync import pull_sync
from app.services.sync_push import push_sync

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("", response_model=SyncPullResponse)
async def pull_sync_endpoint(
    cursor: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> SyncPullResponse:
    return await pull_sync(session, current_user.id, cursor)


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
async def push_sync_endpoint(
    payload: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    await push_sync(session, current_user.id, payload)
