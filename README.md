# LZW compression and decompression

## What it does

`lzw.py` combines Project 2 (LZW compression) and Project 3 (LZW decompression) for strings over `{a, b, c}`. It prints step-by-step traces, dictionaries, codes or decoded text, and verification results. The decompressor rebuilds its dictionary from the codes alone. The compression-only `lzw_compress.py` entry point remains available for Project 2.

## How to run

```sh
python3 lzw.py compress "abababab"
python3 lzw.py decompress "0 1 3 5 1"
python3 lzw.py roundtrip "abababab"
```

If the value is omitted, that subcommand prompts for it. Run `python3 lzw.py` without arguments to open the interactive menu, which loops until you choose `0) Quit`.

The legacy compression-only entry point is:

```sh
python3 lzw_compress.py abababab
```

Run all tests with `python3 -m unittest -v`.

## Accepted code formats

The decompressor accepts whitespace-separated, comma-separated, or bracketed codes, with an optional label before a colon. For example: `0 1 3 5 1`, `0,1,3,5,1`, `[0, 1, 3, 5, 1]`, and `Codes: [0, 1, 3, 5, 1]`. Codes must be non-negative integers.

## Real example runs

The output blocks below were captured directly from the listed commands.

### Compression: abababab

Command: `python3 lzw.py compress "abababab"`

```text
Input: abababab

Compression trace:
Step | Current w | Read char k | w+k in dict? | Output code | New dict entry
-----+-----------+-------------+--------------+-------------+---------------
1    | a         | b           | no           | 0           | ab = 3        
2    | b         | a           | no           | 1           | ba = 4        
3    | a         | b           | yes          | -           | -             
4    | ab        | a           | no           | 3           | aba = 5       
5    | a         | b           | yes          | -           | -             
6    | ab        | a           | yes          | -           | -             
7    | aba       | b           | no           | 5           | abab = 6      
8    | b         | END         | -            | 1           | -             

Codes: [0, 1, 3, 5, 1]

Final dictionary:
Index | Substring | Kind   
------+-----------+--------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | ab        | added
    4 | ba        | added
    5 | aba       | added
    6 | abab      | added

Substitution: a | b | ab | aba | b  ->  abababab  (Verification OK)
Compression summary: original length = 8, number of codes = 5, ratio = 0.625
Round-trip OK
```

### Decompression: 0 1 3 5 1

Command: `python3 lzw.py decompress "0 1 3 5 1"`

```text
Decompression trace:
Step | Code read | Case                             | Entry | Output so far | New dictionary entry
-----+-----------+----------------------------------+-------+---------------+---------------------
1    | 0         | first code                       | a     | a             | -                   
2    | 1         | in dictionary                    | b     | ab            | ab = 3              
3    | 3         | in dictionary                    | ab    | abab          | ba = 4              
4    | 5         | special case (code = next index) | aba   | abababa       | aba = 5             
5    | 1         | in dictionary                    | b     | abababab      | abab = 6            

Decompressed text: abababab

Final dictionary:
Index | Substring | Kind   
------+-----------+--------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | ab        | added
    4 | ba        | added
    5 | aba       | added
    6 | abab      | added
Verification OK
Summary: number of codes = 5, output length = 8, ratio = 0.625
```

### Decompression special case: [0, 3, 4]

Command: `python3 lzw.py decompress "[0, 3, 4]"`

```text
Decompression trace:
Step | Code read | Case                             | Entry | Output so far | New dictionary entry
-----+-----------+----------------------------------+-------+---------------+---------------------
1    | 0         | first code                       | a     | a             | -                   
2    | 3         | special case (code = next index) | aa    | aaa           | aa = 3              
3    | 4         | special case (code = next index) | aaa   | aaaaaa        | aaa = 4             

Decompressed text: aaaaaa

Final dictionary:
Index | Substring | Kind   
------+-----------+--------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | aa        | added
    4 | aaa       | added
Verification OK
Summary: number of codes = 3, output length = 6, ratio = 0.500
```

### Round trip: abcabcabc

Command: `python3 lzw.py roundtrip abcabcabc`

```text
Input: abcabcabc

Compression trace:
Step | Current w | Read char k | w+k in dict? | Output code | New dict entry
-----+-----------+-------------+--------------+-------------+---------------
1    | a         | b           | no           | 0           | ab = 3        
2    | b         | c           | no           | 1           | bc = 4        
3    | c         | a           | no           | 2           | ca = 5        
4    | a         | b           | yes          | -           | -             
5    | ab        | c           | no           | 3           | abc = 6       
6    | c         | a           | yes          | -           | -             
7    | ca        | b           | no           | 5           | cab = 7       
8    | b         | c           | yes          | -           | -             
9    | bc        | END         | -            | 4           | -             

Codes: [0, 1, 2, 3, 5, 4]

Final dictionary:
Index | Substring | Kind   
------+-----------+--------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | ab        | added
    4 | bc        | added
    5 | ca        | added
    6 | abc       | added
    7 | cab       | added

Substitution: a | b | c | ab | ca | bc  ->  abcabcabc  (Verification OK)
Compression summary: original length = 9, number of codes = 6, ratio = 0.667
Round-trip OK
Decompression trace:
Step | Code read | Case          | Entry | Output so far | New dictionary entry
-----+-----------+---------------+-------+---------------+---------------------
1    | 0         | first code    | a     | a             | -                   
2    | 1         | in dictionary | b     | ab            | ab = 3              
3    | 2         | in dictionary | c     | abc           | bc = 4              
4    | 3         | in dictionary | ab    | abcab         | ca = 5              
5    | 5         | in dictionary | ca    | abcabca       | abc = 6             
6    | 4         | in dictionary | bc    | abcabcabc     | cab = 7             

Decompressed text: abcabcabc

Final dictionary:
Index | Substring | Kind   
------+-----------+--------
    0 | a         | initial
    1 | b         | initial
    2 | c         | initial
    3 | ab        | added
    4 | bc        | added
    5 | ca        | added
    6 | abc       | added
    7 | cab       | added
Verification OK
Summary: number of codes = 6, output length = 9, ratio = 0.667

Final comparison: OK
```
