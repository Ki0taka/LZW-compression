"""Unit tests for the LZW compressor."""

import itertools
import os
import random
import subprocess
import sys
import unittest

from lzw_compress import INITIAL_ALPHABET, lzw_compress, substitute_codes, validate_input

_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Independent reference decoder (written from scratch for round-trip tests)
# ---------------------------------------------------------------------------

def lzw_decompress_reference(codes: list[int]) -> str:
    """Decode LZW codes back to a string, including the special same-code case.

    When the current code equals the next free dictionary index, the entry
    has not been added yet.  The correct value is ``previous + previous[0]``
    (the *cScSc* pattern described in the original Welch paper).
    """
    dictionary: dict[int, str] = {index: char for index, char in enumerate(INITIAL_ALPHABET)}
    next_code = len(dictionary)

    if not codes:
        return ""

    result: list[str] = [dictionary[codes[0]]]
    previous = result[0]

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            # Special case: code is exactly the next free index.
            entry = previous + previous[0]
        else:
            raise ValueError(f"Invalid code during decompression: {code}")

        result.append(entry)
        dictionary[next_code] = previous + entry[0]
        next_code += 1
        previous = entry

    return "".join(result)


# ---------------------------------------------------------------------------
# Original tests (kept as-is)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# New: lzw_compress raises ValueError for bad inputs
# ---------------------------------------------------------------------------

class TestLZWCompressErrors(unittest.TestCase):
    """Verify that lzw_compress itself raises ValueError for bad inputs."""

    def test_empty_string(self) -> None:
        """lzw_compress rejects an empty string."""
        with self.assertRaises(ValueError):
            lzw_compress("")

    def test_invalid_character(self) -> None:
        """lzw_compress rejects characters outside {a, b, c}."""
        with self.assertRaises(ValueError):
            lzw_compress("abd")

    def test_whitespace_inside(self) -> None:
        """lzw_compress rejects strings with whitespace inside."""
        with self.assertRaises(ValueError):
            lzw_compress("ab c")


# ---------------------------------------------------------------------------
# New: trace structure
# ---------------------------------------------------------------------------

class TestTrace(unittest.TestCase):
    """Verify the trace structure for a known input."""

    def test_trace_abababab(self) -> None:
        """The trace for 'abababab' has 8 rows with correct output codes."""
        codes, _, trace_steps = lzw_compress("abababab")

        # 8 characters → 8 trace rows (7 loop iterations + 1 flush)
        self.assertEqual(len(trace_steps), 8)

        # The final (FIN) row must emit code 1 (for 'b')
        last_row = trace_steps[-1]
        self.assertEqual(last_row["read_char"], "FIN")
        self.assertEqual(last_row["output_code"], 1)

        # Collecting non-placeholder output codes reproduces the code list
        emitted = [row["output_code"] for row in trace_steps
                   if row["output_code"] != "-"]
        self.assertEqual(emitted, [0, 1, 3, 5, 1])
        self.assertEqual(emitted, codes)


# ---------------------------------------------------------------------------
# New: round-trip with independent decoder
# ---------------------------------------------------------------------------

class TestRoundTrip(unittest.TestCase):
    """Exhaustive and long-input round-trip tests using an independent decoder."""

    def test_exhaustive_short_strings(self) -> None:
        """compress then decompress == identity for all {a,b,c}^n, n=1..8."""
        for length in range(1, 9):
            for chars in itertools.product("abc", repeat=length):
                s = "".join(chars)
                with self.subTest(s=s):
                    codes, _, _ = lzw_compress(s)
                    self.assertEqual(lzw_decompress_reference(codes), s)

    def test_long_repetitive(self) -> None:
        """A highly repetitive input round-trips and compresses well."""
        text = "abc" * 200
        codes, _, _ = lzw_compress(text)
        self.assertEqual(lzw_decompress_reference(codes), text)
        self.assertLess(len(codes), len(text),
                        "Repetitive input should compress (fewer codes than characters)")

    def test_long_random(self) -> None:
        """A seeded random string of length 1000 round-trips correctly."""
        rng = random.Random(42)
        text = "".join(rng.choice("abc") for _ in range(1000))
        codes, _, _ = lzw_compress(text)
        self.assertEqual(lzw_decompress_reference(codes), text)


# ---------------------------------------------------------------------------
# New: dictionary sanity checks
# ---------------------------------------------------------------------------

class TestDictionarySanity(unittest.TestCase):
    """Verify structural properties of the dictionary."""

    def test_initial_entries(self) -> None:
        """The initial entries are always {a:0, b:1, c:2}."""
        _, dictionary, _ = lzw_compress("abcabc")
        for char, expected_code in zip(INITIAL_ALPHABET, range(len(INITIAL_ALPHABET))):
            self.assertIn(char, dictionary)
            self.assertEqual(dictionary[char], expected_code)

    def test_contiguous_indices(self) -> None:
        """All dictionary indices form a contiguous range starting at 0."""
        _, dictionary, _ = lzw_compress("abcabcabcabc")
        indices = sorted(dictionary.values())
        self.assertEqual(indices, list(range(len(dictionary))))

    def test_added_entries_structure(self) -> None:
        """Every added entry is an existing entry concatenated with one alphabet character."""
        _, dictionary, _ = lzw_compress("abababcbcbca")
        by_code = sorted(dictionary.items(), key=lambda item: item[1])
        known: set[str] = set(INITIAL_ALPHABET)
        for substring, code in by_code:
            if code < len(INITIAL_ALPHABET):
                continue
            prefix = substring[:-1]
            self.assertIn(prefix, known,
                          f"Entry '{substring}'={code}: prefix '{prefix}' not a known entry")
            self.assertIn(substring[-1], set(INITIAL_ALPHABET))
            known.add(substring)


# ---------------------------------------------------------------------------
# New: CLI integration test via subprocess
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):
    """Test the command-line interface end-to-end."""

    def test_valid_input_exit_code_and_output(self) -> None:
        """Valid input returns exit code 0 and output contains the codes."""
        result = subprocess.run(
            [sys.executable, "lzw_compress.py", "abababab"],
            capture_output=True, text=True, cwd=_PROJECT_DIR,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("[0, 1, 3, 5, 1]", result.stdout)

    def test_invalid_input_exit_code_and_stderr(self) -> None:
        """Invalid input returns exit code 1 with a message on stderr, no traceback."""
        result = subprocess.run(
            [sys.executable, "lzw_compress.py", "abd"],
            capture_output=True, text=True, cwd=_PROJECT_DIR,
        )
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stderr.strip(), "stderr should contain an error message")
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
