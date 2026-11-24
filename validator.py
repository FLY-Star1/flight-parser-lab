"""Row validation: airport list loading, single-row checks, record building."""

from datetime import datetime
import math
import re

_FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}")
_AIRPORT_RE = re.compile(r"[A-Z]{3}")
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")


def _parse_strict_datetime(value: str) -> datetime | None:
    """Parse YYYY-MM-DD HH:MM strictly (zero-padded, 24-hour, single space)."""
    if not _DATETIME_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def load_airports(path: str) -> set[str]:
    airports: set[str] = set()
    with open(path, mode="r", encoding="utf-8") as f:
        for raw_line in f:
            code = raw_line.strip()
            if not code or code.startswith("#"):
                continue
            airports.add(code)
    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    stripped = [field.strip() for field in fields]
    if any(not field for field in stripped):
        return "MISSING_FIELD"

    flight_id, origin, destination, dep_str, arr_str, price_str = stripped
    if not _FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"

    if not _AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not _AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    dep_dt = _parse_strict_datetime(dep_str)
    if dep_dt is None:
        return "INVALID_DEPARTURE"

    arr_dt = _parse_strict_datetime(arr_str)
    if arr_dt is None:
        return "INVALID_ARRIVAL"

    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_str)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"

    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    flight_id, origin, destination, dep_str, arr_str, price_str = (
        field.strip() for field in fields
    )
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": float(price_str),
    }