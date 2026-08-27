from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.commitment import Commitment
from app.models.user import User
from app.schemas.commitment import CommitmentCreate, CommitmentRead
from app.services.commitments import create_commitment

router = APIRouter(prefix="/commitments", tags=["commitments"])


@router.post("", response_model=CommitmentRead, status_code=status.HTTP_201_CREATED)
async def create_commitment_endpoint(
    payload: CommitmentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CommitmentRead:
    commitment = await create_commitment(session, current_user.id, payload)
    return CommitmentRead.model_validate(commitment)


@router.get("", response_model=list[CommitmentRead])
async def list_commitments(
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[Commitment]:
    query = select(Commitment).where(
        Commitment.user_id == current_user.id, Commitment.deleted_at.is_(None)
    )
    if active_only:
        query = query.where(Commitment.archived_at.is_(None))
    result = await session.scalars(query)
    return list(result)
