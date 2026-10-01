"""Secure, human-friendly IDs with a fixed two-letter/one-digit rhythm."""

from ._constants import (
    DEFAULT_LENGTH,
    DIGITS,
    LETTERS,
    LETTERS_WITH_UPPERCASE,
    MAX_LENGTH,
    MIN_LENGTH,
)
from ._core import (
    InvalidIdFormatError,
    InvalidIdLengthError,
    ensure_valid_id,
    get_id_capacity,
    get_id_entropy,
    is_valid_id,
    tidyid,
)

__version__ = "2.1.0"

__all__ = (
    "DEFAULT_LENGTH",
    "DIGITS",
    "LETTERS",
    "LETTERS_WITH_UPPERCASE",
    "MAX_LENGTH",
    "MIN_LENGTH",
    "InvalidIdFormatError",
    "InvalidIdLengthError",
    "ensure_valid_id",
    "get_id_capacity",
    "get_id_entropy",
    "is_valid_id",
    "tidyid",
)
