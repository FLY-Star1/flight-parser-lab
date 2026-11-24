import argparse
from datetime import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: replace STUDENT_ID with your actual RTU student ID (plain ASCII, no spaces/underscores).
STUDENT_ID = "251ADB137"
FIRST_NAME = "Giyosiddin"
LAST_NAME = "Kutbiddinov"

def _error(message: str) -> int:
    clean = message.replace("\n", " ").strip()
    print(f"Error: {clean}", file=sys.stderr)
    return 1

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Validate flight schedule CSVs, build JSON database, and run queries.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", dest="input_file", metavar="FILE", help="Parse a single CSV file.")
    source.add_argument(
        "-d",
        dest="input_dir",
        metavar="FOLDER",
        help="Parse all .csv files in a folder (non-recursive, sorted).",
    )
    source.add_argument(
        "-j",
        dest="json_db",
        metavar="FILE",
        help="Load an existing JSON database instead of parsing CSVs.",
    )

    parser.add_argument(
        "-a",
        dest="airports_file",
        metavar="FILE",
        help="Airport list file (required with -i and -d; ignored with -j).",
    )
    parser.add_argument(
        "-o",
        dest="output_db",
        metavar="FILE",
        help="Output path for the JSON database (default: db.json; only with -i or -d).",
    )
    parser.add_argument(
        "-q",
        dest="query_file",
        metavar="FILE",
        help="Run queries from this JSON file against the database.",
    )
    parser.add_argument(
        "-r",
        dest="response_dir",
        default=".",
        metavar="FOLDER",
        help="Folder for the query response file (default: current directory).",
    )
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if (args.input_file or args.input_dir) and not args.airports_file:
            parser.error("argument -a is required when using -i or -d")
        if args.json_db and args.output_db is not None:
            parser.error("argument -o is not allowed with -j")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        return code

    db: list[dict] = []

    if args.json_db:
        if not os.path.isfile(args.json_db):
            return _error(f"Database file not found: {args.json_db}")
        try:
            with open(args.json_db, mode="r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return _error(f"Failed to read JSON database: {exc}")

        if not isinstance(loaded, list) or not all(isinstance(item, dict) for item in loaded):
            return _error("JSON database must be an array of objects.")
        db = loaded
    else:
        out_db_path = args.output_db if args.output_db is not None else "db.json"
        out_dir = os.path.dirname(out_db_path) or "."
        log_path = os.path.join(out_dir, "errors.log")

        logger = logging.getLogger("flight_parser")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        handler: logging.FileHandler | None = None

        try:
            if not os.path.isfile(args.airports_file):
                return _error(f"Airport list file not found: {args.airports_file}")

            if args.input_file:
                if not os.path.isfile(args.input_file):
                    return _error(f"Input CSV file not found: {args.input_file}")
                csv_paths = [args.input_file]
            else:
                if not os.path.isdir(args.input_dir):
                    return _error(f"Input folder not found: {args.input_dir}")
                try:
                    entries = sorted(os.listdir(args.input_dir))
                except OSError as exc:
                    return _error(f"Cannot read folder {args.input_dir}: {exc}")

                csv_paths = [
                    os.path.join(args.input_dir, name)
                    for name in entries
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.input_dir, name))
                ]
                if not csv_paths:
                    return _error(f"No .csv files found in folder: {args.input_dir}")

            try:
                airports = load_airports(args.airports_file)
                db, errors = parse_files(csv_paths, airports)
            except OSError as exc:
                return _error(f"Failed while reading input files: {exc}")

            try:
                handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
                handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s %(levelname)s %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )
                )
                logger.addHandler(handler)
                for err_msg in errors:
                    logger.warning("%s", err_msg)
            except OSError as exc:
                return _error(f"Failed to write log file: {exc}")

            try:
                with open(out_db_path, mode="w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
            except OSError as exc:
                return _error(f"Failed to write database file: {exc}")
        finally:
            if handler is not None:
                logger.removeHandler(handler)
                handler.close()

    if args.query_file:
        if not os.path.isfile(args.query_file):
            return _error(f"Query file not found: {args.query_file}")
        try:
            with open(args.query_file, mode="r", encoding="utf-8") as f:
                queries = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            return _error(f"Failed to read query file: {exc}")

        if not isinstance(queries, (dict, list)) or (
            isinstance(queries, list) and not all(isinstance(q, dict) for q in queries)
        ):
            return _error("Query file must contain a query object or an array of objects.")

        results = run_queries(db, queries)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        response_filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
        response_path = os.path.join(args.response_dir, response_filename)

        try:
            with open(response_path, mode="w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        except OSError as exc:
            return _error(f"Failed to write response file: {exc}")

    return 0

if __name__ == "__main__":
    sys.exit(main())