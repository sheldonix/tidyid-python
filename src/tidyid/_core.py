"""Native Python implementation of TidyID's public API."""

from __future__ import annotations

import math
from typing import Optional

from ._constants import (
    DEFAULT_LENGTH,
    DIGITS,
    LETTERS,
    LETTERS_WITH_UPPERCASE,
    MAX_LENGTH,
    MIN_LENGTH,
)
from ._random import _has_valid_id_format, generate_id

_DIGIT_ALPHABET_BITS = 3
_LOWERCASE_LETTER_ENTROPY = math.log2(len(LETTERS))
_UPPERCASE_LETTER_ENTROPY = math.log2(len(LETTERS_WITH_UPPERCASE))
_DIGIT_ENTROPY = math.log2(len(DIGITS))


class InvalidIdLengthError(ValueError):
    """Raised when an ID length is outside the supported range."""

    def __init__(self) -> None:
        super().__init__("length must be between 3 and 256")


class InvalidIdFormatError(TypeError):
    """Raised when a value is not a structurally valid TidyID."""

    def __init__(self) -> None:
        super().__init__("value is not a valid TidyID")


def _is_valid_length(length: object) -> bool:
    return type(length) is int and MIN_LENGTH <= length <= MAX_LENGTH


def _assert_valid_length(length: object) -> None:
    if not _is_valid_length(length):
        raise InvalidIdLengthError


def tidyid(length: int = DEFAULT_LENGTH, allow_uppercase: bool = False) -> str:
    """Generate a secure, uniformly sampled TidyID from fresh CSPRNG bytes."""

    _assert_valid_length(length)
    return generate_id(length, allow_uppercase)


def is_valid_id(
    value: object,
    length: Optional[int] = None,
    allow_uppercase: bool = False,
) -> bool:
    """Return whether ``value`` has valid TidyID structure and length."""

    if type(value) is not str:
        return False
    value_length = len(value)
    if length is not None and (not _is_valid_length(length) or value_length != length):
        return False
    if value_length < MIN_LENGTH or value_length > MAX_LENGTH:
        return False
    return _has_valid_id_format(value, allow_uppercase)


def ensure_valid_id(
    value: object,
    length: Optional[int] = None,
    allow_uppercase: bool = False,
) -> None:
    """Raise an explicit exception unless ``value`` is a valid TidyID."""

    if length is not None:
        _assert_valid_length(length)
    if not is_valid_id(value, length, allow_uppercase):
        raise InvalidIdFormatError


def get_id_capacity(
    length: int = DEFAULT_LENGTH,
    allow_uppercase: bool = False,
) -> int:
    """Return the exact number of IDs available for the requested mode."""

    _assert_valid_length(length)
    digit_count = length // 3
    letter_count = length - digit_count
    letter_base = len(LETTERS_WITH_UPPERCASE if allow_uppercase else LETTERS)
    capacity: int = letter_base**letter_count
    return capacity << digit_count * _DIGIT_ALPHABET_BITS


def get_id_entropy(
    length: int = DEFAULT_LENGTH,
    allow_uppercase: bool = False,
) -> float:
    """Return the entropy of the requested ID space in bits."""

    _assert_valid_length(length)
    digit_count = length // 3
    letter_count = length - digit_count
    letter_entropy = (
        _UPPERCASE_LETTER_ENTROPY if allow_uppercase else _LOWERCASE_LETTER_ENTROPY
    )
    return letter_count * letter_entropy + digit_count * _DIGIT_ENTROPY
