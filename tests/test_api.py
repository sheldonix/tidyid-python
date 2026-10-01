import math
import unittest

from tidyid import (
    DEFAULT_LENGTH,
    DIGITS,
    LETTERS,
    LETTERS_WITH_UPPERCASE,
    InvalidIdFormatError,
    InvalidIdLengthError,
    ensure_valid_id,
    get_id_capacity,
    get_id_entropy,
    is_valid_id,
    tidyid,
)


class GenerationTests(unittest.TestCase):
    def test_generates_lld_structure_at_all_boundary_lengths(self) -> None:
        for length in (3, 8, 10, 16, 256):
            for _ in range(25):
                value = tidyid(length)
                self.assertEqual(len(value), length)
                for index, character in enumerate(value):
                    alphabet = DIGITS if (index + 1) % 3 == 0 else LETTERS
                    self.assertIn(character, alphabet)

    def test_every_supported_length_and_mode_round_trips(self) -> None:
        for length in range(3, 257):
            for allow_uppercase in (False, True):
                value = tidyid(length, allow_uppercase)
                self.assertTrue(is_valid_id(value, length, allow_uppercase))

    def test_defaults_to_32_characters(self) -> None:
        self.assertEqual(DEFAULT_LENGTH, 32)
        self.assertEqual(len(tidyid()), 32)

    def test_uppercase_mode_uses_only_unambiguous_characters(self) -> None:
        self.assertEqual(
            LETTERS_WITH_UPPERCASE,
            "ABCDEFGHJKMNPQRTUVWXYZabcdefghjkmnpqrtuvwxyz",
        )
        for length in (3, 16, 32, 256):
            value = tidyid(length, True)
            self.assertEqual(len(value), length)
            for index, character in enumerate(value):
                alphabet = DIGITS if (index + 1) % 3 == 0 else LETTERS_WITH_UPPERCASE
                self.assertIn(character, alphabet)
            self.assertTrue(is_valid_id(value, length, True))

    def test_excludes_every_ambiguous_character(self) -> None:
        self.assertEqual(LETTERS, "abcdefghjkmnpqrtuvwxyz")
        self.assertEqual(DIGITS, "23456789")
        values = "".join(tidyid(16) for _ in range(1_000))
        self.assertFalse(set(values) & set("01ilos"))
        uppercase_values = "".join(tidyid(16, True) for _ in range(1_000))
        self.assertFalse(set(uppercase_values) & set("01ILOSilos"))

    def test_rejects_invalid_lengths(self) -> None:
        for length in (0, float("nan"), 2, 3.5, 8.0, 32.0, 257, True, 2**63):
            with (
                self.subTest(length=length),
                self.assertRaisesRegex(
                    InvalidIdLengthError,
                    "length must be between 3 and 256",
                ),
            ):
                tidyid(length)  # type: ignore[arg-type]


class ValidationTests(unittest.TestCase):
    def test_validates_structure_and_optional_exact_length(self) -> None:
        cases = (
            ("mk7qw2xy", None, False, True),
            ("mk7qw2xy", 8, False, True),
            ("mk7qw2xy", 16, False, False),
            ("mk7qw2x", None, False, True),
            ("mk7qw2x9", None, False, False),
            ("m27qw2xy", None, False, False),
            ("mk7q52xy", None, False, False),
            ("MK7QW2XY", None, False, False),
            ("MK7QW2XY", 8, True, True),
            ("aZ2", 3, True, True),
            ("a2Z", 3, True, False),
            ("aZQ", 3, True, False),
            ("aI2", 3, True, False),
            ("aZ0", 3, True, False),
            ("éa2", None, False, False),
            (None, None, False, False),
            ("mk", 2, False, False),
        )
        for value, length, uppercase, expected in cases:
            with self.subTest(value=value, length=length, uppercase=uppercase):
                self.assertEqual(
                    is_valid_id(value, length, uppercase),
                    expected,
                )

    def test_rejects_embedded_and_trailing_newlines(self) -> None:
        self.assertFalse(is_valid_id("mk7\n"))
        self.assertFalse(is_valid_id("mk7qw2\nxy"))

    def test_accepts_exact_ascii_alphabets_at_each_position(self) -> None:
        for allow_uppercase, letters in (
            (False, LETTERS),
            (True, LETTERS_WITH_UPPERCASE),
        ):
            for code in range(128):
                character = chr(code)
                with self.subTest(
                    code=code,
                    allow_uppercase=allow_uppercase,
                ):
                    self.assertEqual(
                        is_valid_id(f"{character}a2", 3, allow_uppercase),
                        character in letters,
                    )
                    self.assertEqual(
                        is_valid_id(f"a{character}2", 3, allow_uppercase),
                        character in letters,
                    )
                    self.assertEqual(
                        is_valid_id(f"aa{character}", 3, allow_uppercase),
                        character in DIGITS,
                    )

    def test_ensure_valid_id_raises_explicit_errors(self) -> None:
        ensure_valid_id("mk7qw2xy", 8)
        ensure_valid_id("aZ2", 3, True)
        with self.assertRaisesRegex(
            InvalidIdFormatError,
            "value is not a valid TidyID",
        ):
            ensure_valid_id("invalid", 8)
        with self.assertRaises(InvalidIdLengthError):
            ensure_valid_id("mk", 2)


class MetricTests(unittest.TestCase):
    def test_reports_exact_capacities_and_entropy(self) -> None:
        self.assertEqual(get_id_capacity(8), 7_256_313_856)
        self.assertEqual(get_id_capacity(16), 19_146_942_100_646_395_904)
        self.assertTrue(
            math.isclose(
                get_id_entropy(8),
                32.756589711823786,
                abs_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                get_id_entropy(16),
                64.05374780501026,
                abs_tol=1e-12,
            )
        )
        self.assertEqual(get_id_capacity(3, True), 15_488)
        self.assertTrue(
            math.isclose(
                get_id_entropy(3, True),
                13.918863237274595,
                abs_tol=1e-12,
            )
        )

    def test_metrics_reject_invalid_lengths(self) -> None:
        for metric in (get_id_capacity, get_id_entropy):
            with self.assertRaises(InvalidIdLengthError):
                metric(2)

    def test_capacity_matches_reference_formula_at_every_length(self) -> None:
        for length in range(3, 257):
            digit_count = length // 3
            letter_count = length - digit_count
            for allow_uppercase, letters in (
                (False, LETTERS),
                (True, LETTERS_WITH_UPPERCASE),
            ):
                expected = len(letters) ** letter_count * len(DIGITS) ** digit_count
                self.assertEqual(
                    get_id_capacity(length, allow_uppercase),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
