"""Backward-compatible Project n°2 entry point for LZW compression."""

from lzw import INITIAL_ALPHABET, lzw_compress
from lzw import print_dictionary, print_trace, substitute_codes, validate_input


def main() -> None:
    """Run the compression-only command-line interface."""
    import argparse
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Compress a string over {a, b, c} using LZW.")
    parser.add_argument("text", nargs="?", help="input text (if omitted, you will be prompted)")
    args = parser.parse_args()
    text = args.text.strip() if args.text is not None else input("Enter a string over {a, b, c}: ").strip()
    try:
        codes, dictionary, trace_steps = lzw_compress(text)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from None
    print(f"Input: {text}")
    print("\nCompression trace:")
    print_trace(trace_steps)
    print("\nCodes:", codes)
    print("\nFinal dictionary:")
    print_dictionary(dictionary)
    pieces = substitute_codes(codes, dictionary)
    reconstructed = "".join(pieces)
    status = "Verification OK" if reconstructed == text else "Verification FAILED"
    print(f"\nSubstitution: {' | '.join(pieces)}  ->  {reconstructed}  ({status})")
    ratio = len(codes) / len(text)
    print(f"Compression summary: original length = {len(text)}, number of codes = {len(codes)}, ratio = {ratio:.3f}")


if __name__ == "__main__":
    main()
