"""Command-line entry point for TidyID."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Optional

from . import DEFAULT_LENGTH, MAX_LENGTH, MIN_LENGTH, __version__, tidyid

_HELP = f"""Usage
  $ tidyid [options]

Options
  -s, --size       Generated ID size ({MIN_LENGTH}-{MAX_LENGTH})
  -u, --allow-uppercase
                    Allow uppercase letters
  -v, --version    Show version number
  -h, --help       Show this help

Examples
  $ tidyid
  eb4hv3ej7re9qh2cz9gd6tn5hv4fh8be

  $ tidyid -u
  Dn4Rc2Nv9Cf2Vh6Jj5cY7Pp5Gz3XD8vQ

  $ tidyid -s 16
  vx2rf4zm3mf6vf7j

  $ tidyid -s 16 -u
  Cp8Xw6Fb3Aq2Mn4Y"""
_INVALID_SIZE_MESSAGE = f"Size must be an integer between {MIN_LENGTH} and {MAX_LENGTH}"


def _fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI and return a process exit status."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--version" in arguments or "-v" in arguments:
        print(__version__)
        return 0
    if "--help" in arguments or "-h" in arguments:
        print(_HELP)
        return 0

    size = DEFAULT_LENGTH
    allow_uppercase = False
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in ("--size", "-s"):
            index += 1
            if index == len(arguments):
                return _fail(_INVALID_SIZE_MESSAGE)
            size_argument = arguments[index]
            try:
                if (
                    not size_argument.isascii()
                    or "_" in size_argument
                    or size_argument.strip() != size_argument
                ):
                    raise ValueError
                size = int(size_argument, 10)
            except ValueError:
                return _fail(_INVALID_SIZE_MESSAGE)
            if not MIN_LENGTH <= size <= MAX_LENGTH:
                return _fail(_INVALID_SIZE_MESSAGE)
        elif argument in ("--allow-uppercase", "-u"):
            allow_uppercase = True
        else:
            return _fail(f"Unknown argument {argument}")
        index += 1

    print(tidyid(size, allow_uppercase))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
