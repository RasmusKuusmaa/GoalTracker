from datetime import date, timedelta


def parse_local_date(value: str) -> date:
    return date.fromisoformat(value)


def iso_week_key(value: date) -> tuple[int, int]:
    iso_year, iso_week, _ = value.isocalendar()
    return iso_year, iso_week


def week_bounds(value: date, week_start: int) -> tuple[date, date]:
    if not 1 <= week_start <= 7:
        raise ValueError("week_start must be between 1 (Monday) and 7 (Sunday)")

    offset = (value.isoweekday() - week_start) % 7
    start = value - timedelta(days=offset)
    end = start + timedelta(days=6)
    return start, end
