"""Low-level TidyID generation and format validation."""

from os import urandom

from ._constants import (
    DIGITS,
    LETTERS,
    LETTERS_WITH_UPPERCASE,
)

_LETTER_BYTES = LETTERS.encode("ascii")
_UPPERCASE_LETTER_BYTES = LETTERS_WITH_UPPERCASE.encode("ascii")
_DIGIT_BYTES = DIGITS.encode("ascii")


def _make_letter_byte_codes(alphabet: bytes) -> bytes:
    return (alphabet * (256 // len(alphabet))).ljust(256, b"\0")


_LETTER_BYTE_CODES = _make_letter_byte_codes(_LETTER_BYTES)
_UPPERCASE_LETTER_BYTE_CODES = _make_letter_byte_codes(_UPPERCASE_LETTER_BYTES)
_DIGIT_BYTE_CODES = _DIGIT_BYTES * (256 // len(_DIGIT_BYTES))


def generate_id(
    length: int,
    allow_uppercase: bool = False,
) -> str:
    """Generate one ID from fresh CSPRNG bytes without retaining state."""

    digit_count = length // 3
    letter_count = length - digit_count
    random_size = length * 2
    letter_codes = (
        _UPPERCASE_LETTER_BYTE_CODES if allow_uppercase else _LETTER_BYTE_CODES
    )

    random = urandom(random_size)
    letters = random[:-digit_count].translate(letter_codes).replace(b"\0", b"")
    while len(letters) < letter_count:
        random = urandom(random_size)
        letters += random[:-digit_count].translate(letter_codes).replace(b"\0", b"")

    letters = letters[:letter_count]
    digits = random[-digit_count:].translate(_DIGIT_BYTE_CODES)
    output = bytearray(length)
    output[0::3] = letters[0::2]
    output[1::3] = letters[1::2]
    output[2::3] = digits
    return output.decode("ascii")


def _has_valid_id_format(value: str, allow_uppercase: bool) -> bool:
    if not value.isascii():
        return False
    encoded = value.encode("ascii")
    letters = _UPPERCASE_LETTER_BYTES if allow_uppercase else _LETTER_BYTES
    return not (encoded[0::3] + encoded[1::3]).translate(
        None,
        letters,
    ) and not encoded[2::3].translate(None, _DIGIT_BYTES)
