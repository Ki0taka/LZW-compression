# LZW compression (Project n°2)

A standard-library-only implementation of LZW compression for strings over the alphabet `{a, b, c}`. It prints a per-step trace, the final dictionary, output codes, a substitution-based reconstruction check, and a compression ratio.

## Run

```sh
python3 lzw_compress.py abababab
```

Or run without an argument to enter a string at the prompt:

```sh
python3 lzw_compress.py
```

Run the unit tests with:

```sh
python3 -m unittest -v
```

## Example

Actual output for `python3 lzw_compress.py abababab`:

```text
Input: abababab

Compression trace:
Step | Current w | Read char k | w+k in dict? | Output code | New dict entry
-----+-----------+-------------+--------------+-------------+---------------
1    | a         | b           | False        | 0           | ab = 3
2    | b         | a           | False        | 1           | ba = 4
3    | a         | b           | True         | —           | —
4    | ab        | a           | False        | 3           | aba = 5
5    | a         | b           | True         | —           | —
6    | ab        | a           | True         | —           | —
7    | aba       | b           | False        | 5           | abab = 6
8    | b         | END         | —            | 1           | —

Codes: [0, 1, 3, 5, 1]

Final dictionary:
Index | Substring | Kind
------+-----------+----------------------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | ab        | added
    4 | ba        | added
    5 | aba       | added
    6 | abab      | added

Substitution: a | b | ab | aba | b  ->  abababab  (Verification OK)
Compression summary: original length = 8, number of codes = 5, ratio = 0.625
```
