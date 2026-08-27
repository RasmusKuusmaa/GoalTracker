import uuid
from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.commitment import CommitmentCadence, CommitmentComparator, CommitmentType
from app.schemas.commitment import CommitmentCreate


def _base(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": uuid.uuid4(),
        "title": "Gym",
        "type": CommitmentType.binary,
        "cadence": CommitmentCadence.daily,
        "active_from": date(2026, 1, 1),
    }
    payload.update(overrides)
    return payload


def test_binary_daily_is_valid() -> None:
    CommitmentCreate(**_base())


def test_quota_daily_rejected() -> None:
    with pytest.raises(ValidationError):
        CommitmentCreate(**_base(type=CommitmentType.quota, target_count=3))


def test_quota_weekly_requires_target_count() -> None:
    with pytest.raises(ValidationError):
        CommitmentCreate(**_base(type=CommitmentType.quota, cadence=CommitmentCadence.weekly))


def test_quota_weekly_with_target_count_is_valid() -> None:
    CommitmentCreate(
        **_base(type=CommitmentType.quota, cadence=CommitmentCadence.weekly, target_count=3)
    )


def test_numeric_requires_target_value_and_comparator() -> None:
    with pytest.raises(ValidationError):
        CommitmentCreate(**_base(type=CommitmentType.numeric))


def test_numeric_requires_comparator() -> None:
    with pytest.raises(ValidationError):
        CommitmentCreate(
            **_base(type=CommitmentType.numeric, target_value=Decimal("2600"))
        )


def test_numeric_with_target_and_comparator_is_valid() -> None:
    CommitmentCreate(
        **_base(
            type=CommitmentType.numeric,
            target_value=Decimal("2600"),
            comparator=CommitmentComparator.lte,
        )
    )


def test_journal_requires_journal_id() -> None:
    with pytest.raises(ValidationError):
        CommitmentCreate(**_base(type=CommitmentType.journal))


def test_journal_with_journal_id_is_valid() -> None:
    CommitmentCreate(**_base(type=CommitmentType.journal, journal_id=uuid.uuid4()))
