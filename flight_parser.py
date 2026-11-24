import sys

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB137"
FIRST_NAME = "Giyosiddin"
LAST_NAME = "Kutbiddinov"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    raise NotImplementedError("main() is not written yet")


if __name__ == "__main__":
    sys.exit(main())
