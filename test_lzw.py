"""Unit tests for the LZW compressor."""

import unittest

from lzw_compress import lzw_compress, substitute_codes, validate_input


class TestLZWCompress(unittest.TestCase):
    """Check expected encodings, dictionary additions, and reconstruction."""

    def test_known_encodings(self) -> None:
        """Verify the hand-checked example strings and their dictionaries."""
        cases = {
            "abababab": ([0, 1, 3, 5, 1], {"ab": 3, "ba": 4, "aba": 5, "abab": 6}),
            "aaaaaa": ([0, 3, 4], {"aa": 3, "aaa": 4}),
            "abcabcabc": ([0, 1, 2, 3, 5, 4], {"ab": 3, "bc": 4, "ca": 5, "abc": 6, "cab": 7}),
            "a": ([0], {}),
        }
        for text, (expected_codes, expected_additions) in cases.items():
            with self.subTest(text=text):
                codes, dictionary, _ = lzw_compress(text)
                self.assertEqual(codes, expected_codes)
                self.assertEqual({key: value for key, value in dictionary.items() if value >= 3}, expected_additions)
                self.assertEqual("".join(substitute_codes(codes, dictionary)), text)

    def test_invalid_inputs(self) -> None:
        """Reject empty input and characters outside the alphabet."""
        for text in ("abd", ""):
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_input(text)


if __name__ == "__main__":
    unittest.main()
