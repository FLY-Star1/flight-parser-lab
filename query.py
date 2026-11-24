from datetime import datetime
import math
import re

_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
_RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}

_ALLOWED_QUERY_KEYS = _RECORD_KEYS | {
    "min_price",
    "sort_by",
    "order",
    "limit",
}

def _is_valid_datetime(value: object) -> bool:
    if not isinstance(value, str) or not _DATETIME_RE.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def _is_valid_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)

def _is_valid_int(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int)

def _validate_query(query: object) -> bool:
    if not isinstance(query, dict):
        return False

    if any(k not in _ALLOWED_QUERY_KEYS for k in query):
        return False

    for str_key in ("flight_id", "origin", "destination"):
        if str_key in query and not isinstance(query[str_key], str):
            return False

    for dt_key in ("departure_datetime", "arrival_datetime"):
        if dt_key in query and not _is_valid_datetime(query[dt_key]):
            return False

    for num_key in ("price", "min_price"):
        if num_key in query and not _is_valid_number(query[num_key]):
            return False

    if "sort_by" in query:
        if query["sort_by"] not in _RECORD_KEYS:
            return False

    if "order" in query:
        if "sort_by" not in query:
            return False
        if query["order"] not in ("asc", "desc"):
            return False

    if "limit" in query:
        if not _is_valid_int(query["limit"]) or query["limit"] < 0:
            return False

    return True

def run_query(db: list[dict], query: dict) -> dict:
    if not _validate_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches: list[dict] = []
    for record in db:
        if "flight_id" in query and record["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and record["origin"] != query["origin"]:
            continue
        if "destination" in query and record["destination"] != query["destination"]:
            continue
        if (
            "departure_datetime" in query
            and record["departure_datetime"] < query["departure_datetime"]
        ):
            continue
        if (
            "arrival_datetime" in query
            and record["arrival_datetime"] > query["arrival_datetime"]
        ):
            continue
        if "price" in query and record["price"] > query["price"]:
            continue
        if "min_price" in query and record["price"] < query["min_price"]:
            continue
        matches.append(record)

    if "sort_by" in query:
        sort_key = query["sort_by"]
        descending = query.get("order", "asc") == "desc"
        if descending:
            matches = [
                rec
                for _, rec in sorted(
                    enumerate(matches),
                    key=lambda item: (item[1][sort_key], -item[0]),
                    reverse=True,
                )
            ]
        else:
            matches = [
                rec
                for _, rec in sorted(
                    enumerate(matches),
                    key=lambda item: (item[1][sort_key], item[0]),
                )
            ]

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}

def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        return [run_query(db, queries)]
    return [run_query(db, q) for q in queries]