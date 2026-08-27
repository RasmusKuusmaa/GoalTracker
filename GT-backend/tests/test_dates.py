from datetime import date

import pytest

from app.core.dates import iso_week_key, parse_local_date, week_bounds


def test_parse_local_date() -> None:
    assert parse_local_date("2024-01-15") == date(2024, 1, 15)


def test_parse_local_date_rejects_bad_format() -> None:
    with pytest.raises(ValueError):
        parse_local_date("15-01-2024")


def test_iso_week_key_regular_date() -> None:
    assert iso_week_key(date(2024, 1, 1)) == (2024, 1)


def test_iso_week_key_year_rolls_backward_at_start_of_year() -> None:
    # 2023-01-01 is a Sunday, part of ISO week 52 of the *previous* ISO year.
    assert iso_week_key(date(2023, 1, 1)) == (2022, 52)


def test_iso_week_key_week_53() -> None:
    assert iso_week_key(date(2020, 12, 31)) == (2020, 53)


def test_iso_week_key_year_rolls_forward_into_next_years_week_53() -> None:
    # 2021-01-01 is a Friday, still part of ISO week 53 of 2020.
    assert iso_week_key(date(2021, 1, 1)) == (2020, 53)


def test_week_bounds_monday_start() -> None:
    start, end = week_bounds(date(2024, 1, 10), week_start=1)
    assert start == date(2024, 1, 8)
    assert end == date(2024, 1, 14)


def test_week_bounds_sunday_start() -> None:
    start, end = week_bounds(date(2024, 1, 10), week_start=7)
    assert start == date(2024, 1, 7)
    assert end == date(2024, 1, 13)


def test_week_bounds_on_boundary_day() -> None:
    start, end = week_bounds(date(2024, 1, 8), week_start=1)
    assert start == date(2024, 1, 8)
    assert end == date(2024, 1, 14)


def test_week_bounds_rejects_invalid_week_start() -> None:
    with pytest.raises(ValueError):
        week_bounds(date(2024, 1, 10), week_start=0)
