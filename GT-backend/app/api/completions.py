from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.completion import Completion
from app.models.user import User
from app.schemas.completion import CompletionRead, CompletionUpsert
from app.services.completions import upsert_completion

router = APIRouter(prefix="/completions", tags=["completions"])


@router.put("", response_model=CompletionRead)
async def upsert_completion_endpoint(
    payload: CompletionUpsert,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Completion:
    return await upsert_completion(session, current_user.id, payload)
