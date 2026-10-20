"""Tests for LZW decompression, parsing, and combined command-line modes."""

import itertools
import os
import random
import subprocess
import sys
import unittest

from lzw import lzw_compress, lzw_decompress, parse_codes

ROOT = os.path.dirname(os.path.abspath(__file__))


class TestLZWDecompress(unittest.TestCase):
    """Check decoded examples, dictionary reconstruction, and special cases."""

    def test_examples_and_dictionaries(self) -> None:
        """Decode hand-verified examples and verify their rebuilt dictionaries."""
        cases = {
            (0, 1, 3, 5, 1): ("abababab", {"ab": 3, "ba": 4, "aba": 5, "abab": 6}, 1),
            (0, 3, 4): ("aaaaaa", {"aa": 3, "aaa": 4}, 2),
            (0, 1, 2, 3, 5, 4): ("abcabcabc", {"ab": 3, "bc": 4, "ca": 5, "abc": 6, "cab": 7}, 0),
            (0,): ("a", {}, 0),
        }
        for codes, (expected, additions, specials) in cases.items():
            with self.subTest(codes=codes):
                text, dictionary, trace = lzw_decompress(list(codes))
                self.assertEqual(text, expected)
                self.assertEqual({key: value for key, value in dictionary.items() if key >= 3},
                                 {code: substring for substring, code in additions.items()})
                self.assertEqual(sum(row["case"] == "special case (code = next index)" for row in trace), specials)
                compressed, original_dictionary, _ = lzw_compress(text)
                self.assertEqual(compressed, list(codes))
                self.assertEqual(dictionary, {code: substring for substring, code in original_dictionary.items()})

    def test_code_validation(self) -> None:
        """Reject empty, malformed, negative, and impossible code streams."""
        for codes in ([], [5], [0, 4], [0, 7], [0, -1], [0, 1.5]):
            with self.subTest(codes=codes), self.assertRaises(ValueError):
                lzw_decompress(codes)  # type: ignore[arg-type]

    def test_parser_formats(self) -> None:
        """Accept supported whitespace, comma, bracket, and labeled forms."""
        expected = [0, 1, 3, 5, 1]
        for text in ("0 1 3 5 1", "0,1,3,5,1", "[0, 1, 3, 5, 1]", "Codes: [0, 1, 3, 5, 1]", "Codés : [0, 1, 3, 5, 1]"):
            with self.subTest(text=text):
                self.assertEqual(parse_codes(text), expected)

    def test_parser_rejects_invalid_tokens(self) -> None:
        """Reject no codes, non-integers, decimal values, and negatives."""
        for text in ("", "  \n", "x", "-1", "1.5", "[]"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_codes(text)

    def test_exhaustive_and_long_roundtrips(self) -> None:
        """Rebuild the same dictionary for all short and selected long strings."""
        samples = ("".join(chars) for length in range(1, 9) for chars in itertools.product("abc", repeat=length))
        rng = random.Random(42)
        samples = itertools.chain(samples, ["abc" * 200, "".join(rng.choice("abc") for _ in range(1000))])
        for text in samples:
            codes, comp_dict, _ = lzw_compress(text)
            decoded, dec_dict, _ = lzw_decompress(codes)
            self.assertEqual(decoded, text)
            self.assertEqual(dec_dict, {code: value for value, code in comp_dict.items()})


class TestCombinedCLI(unittest.TestCase):
    """Exercise subcommands, clean failures, and the interactive menu."""

    def run_cli(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        """Run lzw.py in a subprocess and capture its console output."""
        return subprocess.run([sys.executable, "lzw.py", *args], cwd=ROOT, input=input_text,
                              capture_output=True, text=True)

    def test_commands(self) -> None:
        """Each mode prints its expected result and exits successfully."""
        for args, expected in ((("compress", "abababab"), "Round-trip OK"),
                               (("decompress", "0 1 3 5 1"), "abababab"),
                               (("roundtrip", "abcabcabc"), "Final comparison: OK")):
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)

    def test_invalid_cli(self) -> None:
        """Invalid streams exit one and print an error without traceback."""
        result = self.run_cli("decompress", "0 7")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_valid_noncanonical_cli(self) -> None:
        """A decodable but noncanonical stream is reported without failure."""
        result = self.run_cli("decompress", "0 0 0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Verification: non-canonical codes", result.stdout)

    def test_menu_flow(self) -> None:
        """The menu accepts multiple modes and exits when asked."""
        result = self.run_cli(input_text="1\nabab\n2\n0 1 3\n0\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Codes: [0, 1, 3]", result.stdout)
        self.assertIn("Decompressed text: abab", result.stdout)
        self.assertIn("0) Quit", result.stdout)

    def test_legacy_entry_point(self) -> None:
        """The Project 2 wrapper retains the previous compression output."""
        result = subprocess.run([sys.executable, "lzw_compress.py", "abababab"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Codes: [0, 1, 3, 5, 1]", result.stdout)
        self.assertNotIn("Round-trip", result.stdout)


if __name__ == "__main__":
    unittest.main()
