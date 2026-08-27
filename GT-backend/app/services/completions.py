import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import CommitmentType
from app.models.completion import Completion
from app.schemas.completion import CompletionUpsert
from app.services.commitments import get_owned_commitment


async def upsert_completion(
    session: AsyncSession, user_id: uuid.UUID, payload: CompletionUpsert
) -> Completion:
    commitment = await get_owned_commitment(session, user_id, payload.commitment_id)

    is_numeric = commitment.type == CommitmentType.numeric
    if is_numeric and payload.value is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "value is required for numeric commitments"
        )
    if not is_numeric and payload.value is not None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "value is only valid for numeric commitments"
        )

    completion = await session.scalar(
        select(Completion).where(
            Completion.commitment_id == payload.commitment_id,
            Completion.local_date == payload.local_date,
        )
    )
    if completion is None:
        completion = Completion(
            id=payload.id,
            user_id=user_id,
            commitment_id=payload.commitment_id,
            local_date=payload.local_date,
        )
        session.add(completion)

    completion.status = payload.status
    completion.value = payload.value
    completion.deleted_at = None

    await session.commit()
    await session.refresh(completion)
    return completion
