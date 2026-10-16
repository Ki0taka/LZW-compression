"""Compress strings over {a, b, c} with the LZW algorithm."""

from __future__ import annotations

import argparse
import sys
from typing import Any

INITIAL_ALPHABET = ("a", "b", "c")


def validate_input(text: str) -> None:
    """Raise ValueError unless text is non-empty and uses only a, b, and c."""
    if not text:
        raise ValueError("Input must not be empty.")
    invalid = sorted(set(text) - set(INITIAL_ALPHABET))
    if invalid:
        raise ValueError(
            "Input may contain only the characters a, b, and c; "
            f"invalid character(s): {', '.join(repr(char) for char in invalid)}."
        )


def lzw_compress(text: str) -> tuple[list[int], dict[str, int], list[dict[str, Any]]]:
    """Return LZW codes, the final substring-to-code dictionary, and step trace."""
    validate_input(text)
    dictionary = {char: index for index, char in enumerate(INITIAL_ALPHABET)}
    codes: list[int] = []
    trace_steps: list[dict[str, Any]] = []
    next_code = len(dictionary)
    w = text[0]

    for step_number, k in enumerate(text[1:], start=1):
        candidate = w + k
        found = candidate in dictionary
        if found:
            trace_steps.append({
                "step": step_number, "current_w": w, "read_char": k,
                "in_dictionary": "oui", "output_code": "-", "new_entry": "-",
            })
            w = candidate
        else:
            emitted = dictionary[w]
            dictionary[candidate] = next_code
            trace_steps.append({
                "step": step_number, "current_w": w, "read_char": k,
                "in_dictionary": "non", "output_code": emitted,
                "new_entry": f"{candidate} = {next_code}",
            })
            codes.append(emitted)
            next_code += 1
            w = k

    codes.append(dictionary[w])
    trace_steps.append({
        "step": len(text), "current_w": w, "read_char": "FIN",
        "in_dictionary": "-", "output_code": dictionary[w], "new_entry": "-",
    })
    return codes, dictionary, trace_steps


def print_trace(trace_steps: list[dict[str, Any]]) -> None:
    """Print the compression trace in aligned plain-text columns."""
    columns = [
        ("Étape", "step"), ("w courant", "current_w"), ("Caractère lu k", "read_char"),
        ("w+k dans le dico ?", "in_dictionary"), ("Code émis", "output_code"),
        ("Nouvelle entrée", "new_entry"),
    ]
    widths = [max(len(title), *(len(str(row[key])) for row in trace_steps)) for title, key in columns]
    print(" | ".join(title.ljust(width) for (title, _), width in zip(columns, widths)))
    print("-+-".join("-" * width for width in widths))
    for row in trace_steps:
        print(" | ".join(str(row[key]).ljust(width) for (_, key), width in zip(columns, widths)))


def print_dictionary(dictionary: dict[str, int]) -> None:
    """Print entries sorted by code, identifying initial and added entries."""
    entries = sorted(dictionary.items(), key=lambda item: item[1])
    labels = [("initiale" if index < len(INITIAL_ALPHABET) else "ajoutée")
              for _, index in entries]
    w_idx = max(len("Indice"), *(len(str(index)) for _, index in entries))
    w_sub = max(len("Sous-chaîne"), *(len(substring) for substring, _ in entries))
    w_kind = max(len("Type"), *(len(label) for label in labels))
    print(f"{'Indice'.ljust(w_idx)} | {'Sous-chaîne'.ljust(w_sub)} | {'Type'.ljust(w_kind)}")
    print(f"{'-' * w_idx}-+-{'-' * w_sub}-+-{'-' * w_kind}")
    for (substring, index), label in zip(entries, labels):
        print(f"{str(index).rjust(w_idx)} | {substring.ljust(w_sub)} | {label}")


def substitute_codes(codes: list[int], dictionary: dict[str, int]) -> list[str]:
    """Return the substring represented by each code in the final dictionary."""
    inverse = {code: substring for substring, code in dictionary.items()}
    try:
        return [inverse[code] for code in codes]
    except KeyError as error:
        raise ValueError(f"Unknown dictionary code: {error.args[0]}") from error


def main() -> None:
    """Parse input, run compression, and print trace, dictionary, and verification."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Compresse une chaîne sur {a, b, c} avec LZW.",
    )
    parser.add_argument("text", nargs="?",
                        help="texte en entrée (si omis, une invite s'affiche)")
    args = parser.parse_args()
    text = (args.text.strip() if args.text is not None
            else input("Entrez une chaîne sur {a, b, c} : ").strip())

    try:
        codes, dictionary, trace_steps = lzw_compress(text)
    except ValueError as error:
        print(f"Erreur : {error}", file=sys.stderr)
        raise SystemExit(1) from None

    print(f"Entrée : {text}")
    print("\nTrace de compression :")
    print_trace(trace_steps)
    print("\nCodes :", codes)
    print("\nDictionnaire final :")
    print_dictionary(dictionary)

    pieces = substitute_codes(codes, dictionary)
    reconstructed = "".join(pieces)
    status = "Vérification OK" if reconstructed == text else "Vérification ÉCHEC"
    print(f"\nSubstitution : {' | '.join(pieces)}  ->  {reconstructed}  ({status})")
    ratio = len(codes) / len(text)
    print(f"Résumé de la compression : longueur originale = {len(text)}, "
          f"nombre de codes = {len(codes)}, ratio = {ratio:.3f}")


if __name__ == "__main__":
    main()
