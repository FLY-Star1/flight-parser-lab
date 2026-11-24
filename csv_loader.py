import csv
import os
from validator import to_record, validate_row

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    seen_flights: set[tuple[str, str]] = set()

    for path in paths:
        base_name = os.path.basename(path)
        with open(path, mode="r", encoding="utf-8", newline="") as f:
            for line_num, raw_line in enumerate(f, start=1):
                if line_num == 1:
                    continue

                stripped_line = raw_line.strip()
                if not stripped_line or stripped_line.startswith("#"):
                    continue

                fields = next(csv.reader([raw_line]))
                raw_text = raw_line.rstrip("\r\n")

                error_code = validate_row(fields, airports)
                if error_code is not None:
                    errors.append(f"{base_name}:{line_num}: {error_code} | {raw_text}")
                    continue

                record = to_record(fields)
                flight_key = (record["flight_id"], record["departure_datetime"])
                if flight_key in seen_flights:
                    errors.append(
                        f"{base_name}:{line_num}: DUPLICATE_FLIGHT | {raw_text}"
                    )
                    continue

                seen_flights.add(flight_key)
                records.append(record)

    return records, errors