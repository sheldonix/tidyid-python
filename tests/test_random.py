import unittest
from typing import Optional
from unittest.mock import patch

from tidyid import DIGITS, LETTERS, LETTERS_WITH_UPPERCASE
from tidyid._random import (
    _DIGIT_BYTE_CODES,
    _LETTER_BYTE_CODES,
    _UPPERCASE_LETTER_BYTE_CODES,
    generate_id,
)


class RecordingSource:
    def __init__(self, blocks: Optional[list[bytes]] = None) -> None:
        self.blocks = list(blocks or [])
        self.sizes: list[int] = []

    def __call__(self, size: int) -> bytes:
        self.sizes.append(size)
        if self.blocks:
            return self.blocks.pop(0)
        return bytes(size)


class RandomSamplingTests(unittest.TestCase):
    def test_letter_lookup_cutoffs_are_uniform(self) -> None:
        for alphabet, table, expected_count, rejected in (
            (LETTERS, _LETTER_BYTE_CODES, 11, 14),
            (LETTERS_WITH_UPPERCASE, _UPPERCASE_LETTER_BYTE_CODES, 5, 36),
        ):
            counts = {character: 0 for character in alphabet}
            rejected_count = 0
            for code in table:
                if code == 0:
                    rejected_count += 1
                else:
                    counts[chr(code)] += 1
            self.assertEqual(set(counts.values()), {expected_count})
            self.assertEqual(rejected_count, rejected)

    def test_digit_lookup_uses_every_character_exactly_32_times(self) -> None:
        counts = {character: 0 for character in DIGITS}
        for code in _DIGIT_BYTE_CODES:
            counts[chr(code)] += 1
        self.assertEqual(set(counts.values()), {32})

    def test_requests_fresh_random_bytes_for_every_id(self) -> None:
        source = RecordingSource()
        with patch("tidyid._random.urandom", source):
            self.assertEqual(generate_id(32), "aa2aa2aa2aa2aa2aa2aa2aa2aa2aa2aa")
            self.assertEqual(generate_id(8, True), "AA2AA2AA")
        self.assertEqual(source.sizes, [64, 16])

    def test_rejection_refills_only_the_current_id(self) -> None:
        source = RecordingSource([bytes([255]) * 6, bytes(6)])
        with patch("tidyid._random.urandom", source):
            self.assertEqual(generate_id(3), "aa2")
        self.assertEqual(source.sizes, [6, 6])

    def test_uppercase_sampling_vector(self) -> None:
        source = RecordingSource([bytes((0, 22, 0, 0, 0, 0))])
        with patch("tidyid._random.urandom", source):
            self.assertEqual(generate_id(3, True), "Aa2")

    def test_csprng_failures_propagate_without_fallback(self) -> None:
        failure = RuntimeError("CSPRNG unavailable")

        def fail(_: int) -> bytes:
            raise failure

        with (
            patch("tidyid._random.urandom", fail),
            self.assertRaises(RuntimeError) as raised,
        ):
            generate_id(3)
        self.assertIs(raised.exception, failure)


if __name__ == "__main__":
    unittest.main()
