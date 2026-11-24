# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- ChatGPT GPT-6

## Conversation links

- https://chatgpt.com/share/6b05f118-869c-83ed-8d82-6ee6635eae1d

## What I used them for

- to read a CSV, skipping the header, blank lines and # comment lines, while keeping correct 1-based line numbers
- for strict validation
- to write a function that checks a row against 11 ordered rules and returns the error code of 1st failing rule
- to flag a row as a duplicate if an earlier valid row has the same flight_id
- to build an argparse CLI
- to write warnings to errors.log with Python's logging module using a FileHandler and a custom format
- filter a list of dicts with AND conditions
## Which parts of the code were AI-generated or substantially AI-assisted

| validator.py | validate_row | explained |
| query.py | _is_valid_datetime | explained |
| flight_parser.py | _build_parser | explained |

## Key prompts

1.How I validate "YYYY-MM-DD HH:MM" and 3 uppercase ASCII letters
2.I parse several CSV files and must flag a row as a duplicate if an earlier valid row, in the same or an earlier file, has the same flight_id and departure_datetime. 

I need a set of tuples for this

## What I changed or verified myself

I applied strict validation for datetime formats, airport codes, numeric values, and query parameters.
Then, I added CSV filtering, sorting, and result limiting, with stable sorting and input validation.

I implemented command-line argument handling, JSON database operations, and warning logging to errors.log.
and so on.