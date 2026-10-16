# LZW compression (Project n°2)

This project provides a clear, standard-library-only implementation of the **Lempel–Ziv–Welch (LZW)** lossless compression algorithm for strings over the alphabet `{a, b, c}`. It demonstrates dictionary-based encoding by printing a step-by-step compression trace, the final dictionary, generated output codes, and a substitution-based reconstruction to verify that the original input is preserved.

## Run

```sh
python3 lzw_compress.py abababab
```

Or run without an argument to enter a string at the prompt:

```sh
python3 lzw_compress.py
```

**Accepted input:** only the characters `a`, `b`, and `c`. Surrounding whitespace and newlines are stripped automatically; whitespace inside the string is rejected.

Run the unit tests with:

```sh
python3 -m unittest -v
```

## Example 1 — `abababab`

Actual output for `python3 lzw_compress.py abababab`:

```text
Entrée : abababab

Trace de compression :
Étape | w courant | Caractère lu k | w+k dans le dico ? | Code émis | Nouvelle entrée
------+-----------+----------------+--------------------+-----------+----------------
1     | a         | b              | non                | 0         | ab = 3
2     | b         | a              | non                | 1         | ba = 4
3     | a         | b              | oui                | -         | -
4     | ab        | a              | non                | 3         | aba = 5
5     | a         | b              | oui                | -         | -
6     | ab        | a              | oui                | -         | -
7     | aba       | b              | non                | 5         | abab = 6
8     | b         | FIN            | -                  | 1         | -

Codes : [0, 1, 3, 5, 1]

Dictionnaire final :
Indice | Sous-chaîne | Type
-------+-------------+---------
     0 | a           | initiale
     1 | b           | initiale
     2 | c           | initiale
     3 | ab          | ajoutée
     4 | ba          | ajoutée
     5 | aba         | ajoutée
     6 | abab        | ajoutée

Substitution : a | b | ab | aba | b  ->  abababab  (Vérification OK)
Résumé de la compression : longueur originale = 8, nombre de codes = 5, ratio = 0.625
```

## Example 2 — `aaaaaa` (repeated character)

Actual output for `python3 lzw_compress.py aaaaaa`:

```text
Entrée : aaaaaa

Trace de compression :
Étape | w courant | Caractère lu k | w+k dans le dico ? | Code émis | Nouvelle entrée
------+-----------+----------------+--------------------+-----------+----------------
1     | a         | a              | non                | 0         | aa = 3
2     | a         | a              | oui                | -         | -
3     | aa        | a              | non                | 3         | aaa = 4
4     | a         | a              | oui                | -         | -
5     | aa        | a              | oui                | -         | -
6     | aaa       | FIN            | -                  | 4         | -

Codes : [0, 3, 4]

Dictionnaire final :
Indice | Sous-chaîne | Type
-------+-------------+---------
     0 | a           | initiale
     1 | b           | initiale
     2 | c           | initiale
     3 | aa          | ajoutée
     4 | aaa         | ajoutée

Substitution : a | aa | aaa  ->  aaaaaa  (Vérification OK)
Résumé de la compression : longueur originale = 6, nombre de codes = 3, ratio = 0.500
```
