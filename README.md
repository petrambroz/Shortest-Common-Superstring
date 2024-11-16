# Shortest Common Superstring Solver

## Overview
This is a Python implementation of the [Shortest Common Superstring](https://cgi.csc.liv.ac.uk/~ped/teachadmin/COMP202/annotated_np.html/#p16) problem. The input is a finite set of binary strings, and the output is whether a binary string of length at most *k* containing all binary strings from the input exists. This problem is NP-complete.

## What this implementation does
The main Python script accepts an input file with binary strings and an optional argument `k`. If `k` is provided, the script searches for a superstring of length exactly *k*. If `k` is not provided, the script finds the lowest *k* such that a superstring of that length contains all the input binary strings. The problem is encoded into a CNF formula, which is then solved by a SAT solver. The script outputs the superstring or indicates that no such superstring exists.

## User documentation

### Requirements

The user is expected to have Python3 installed on their system. This script was tested on Python version 3.12.
A Glucose SAT solver is required, more in [Glucose SAT solver](#glucose-sat-solver).

### Usage
```
./solver.py [-v] [-o OUTPUT] [-i INPUT] [-s SOLVER] [-k K]
```
Command line arguments:
* `-h`, `--help`: show a help message
* `-i INPUT`, `--input INPUT`: specify the path to the input file, default: `input.txt`
* `-o OUTPUT`, `--output OUTPUT`: specify the path to the output file, default: `formula.cnf`
* `-s SOLVER`, `--solver SOLVER`: specify the path to the glucose solver (either in $PATH or a relative/absolute path to the binary), default: `glucose-syrup`
* `-k K`: an integer indicating the maximum length of the superstring to be found
* `-v`: increase the verbosity

### Two modes of operation
When the argument `k` is provided with a valid integer value, the script solves the problem for a superstring of length exactly *k*, returning either a failure (if a superstring of such length does not exist) or a valid superstring of the given length. This, however, does not guarantee that the selected *k* is the lowest possible.

When no *k* is provided, the program solves the problem for different *k* values, trying to find the lowest possible. This is done using binary search.

We know that *k* is at least equal to the length of the longest string in the input and at most equal to the total length of the input strings. By setting this as the lower and upper bound, a standard binary search is conducted to find the lowest possible *k*.

This approach finds the optimum in `log(h-l)` steps, where `l` is the length of the longest string and `h` is the total length of the strings.

### Glucose SAT solver
This script relies on the [Glucose](https://www.labri.fr/perso/lsimon/research/glucose/) SAT solver, specifically [Glucose 4.2.1](https://github.com/audemard/glucose). The user is responsible for obtaining the `glucose-syrup` or `glucose-simp` binary, ideally by compiling it from source code. The script assumes the presence of `glucose-syrup` in a directory included in `$PATH`, unless a specific path is provided via arguments.
This whole project is assumed to be used under a Linux or MacOS environment. In case you prefer using Windows, it's recommended to use WSL or a virtual machine.

### Input
The input shall be stored in a text file, either in `input.txt` in the script's directory as a default, or in any other file specified in the arguments. It must contain binary strings separated by newline. Empty lines are ignored. Example input:
```
1110101010
10101
11111
```

### String generator
This project also provides a script to generate random binary strings and save them to `input.txt`. It is not mandatory to use it, but it might be useful for testing.
Usage:
```
./generator.py -m MAX_LENGTH -n COUNT
```
where MAX_LENGTH is the maximum number of characters of each string and COUNT is the number of strings to generate. The minimum length of a string is 3 characters.

## Detailed problem description

This is the specification of the problem from [cgi.csc.liv.ac.uk](https://cgi.csc.liv.ac.uk/~ped/teachadmin/COMP202/annotated_np.html/#p16)

**Name:** Shortest Common Superstring [SR9] 3

**Input:** A finite set *R={r<sub>1</sub>,r<sub>2</sub>,...,r<sub>m</sub>}* of binary strings (sequences of *0* and *1*); positive integer *k*.

**Question:** Is there a binary string *w* of length at most *k* such that every string in *R* is a substring of *w*, i.e. for each *r* in *R*, *w* can be decomposed as *w=w<sub>0</sub>rw<sub>1</sub>* where *w<sub>0</sub>*, *w<sub>1</sub>* are (possibly empty) binary strings?

**Comments:** General problem allows more than two symbols (i.e. not just binary), but this simpler version remains NP-complete.

### Encoding into SAT
The encoding process translates the problem of finding the shortest common superstring into a SAT problem. Here is a step-by-step explanation of the encoding:

1. **Variables**:
    - `x[i]`: Represents the character at position `i` in the superstring. Each position can be either 0 or 1.
    - `y[i, j]`: Represents whether the string `i` starts at position `j` in the superstring.

2. **Clauses**:
    - **Every position in the superstring must be either 0 or 1**:
        For each position `i` in the superstring, we add two clauses to ensure that it can only be 0 or 1, but not both.
        ```
        (x[2*i] OR x[2*i+1])
        (NOT x[2*i] OR NOT x[2*i+1])
        ```

    - **Each string has exactly one starting position**:
        For each string `i`, we ensure that it starts at exactly one position `j` in the superstring. This is done by adding a clause that includes all possible starting positions for the string and then adding clauses to ensure that no two starting positions are true simultaneously.
        ```
        (y[i, 0] OR y[i, 1] OR ... OR y[i, k - len(string[i])])
        (NOT y[i, j1] OR NOT y[i, j2]) for all j1 != j2
        ```

    - **Characters after a starting position must match the string**:
        For each string `i` and each possible starting position `j`, we ensure that the characters in the superstring match the characters in the string. This is done by adding clauses that enforce the match.
        ```
        (NOT y[i, j] OR NOT x[2*(j+s) + 1 - char_value]) for each character s in string[i]
        ```

This encoding ensures that the SAT solver can determine whether a superstring of length `k` exists that contains all the input strings as substrings. If a solution exists, the SAT solver provides a model that can be decoded to obtain the superstring. The decoding is done by examining the value of the first 2k variables which determine the value of each bit in the resulting superstring (if one exists).

## Experiments
The program can find a superstring of strings with a total length of about 100 characters in a reasonable time.
When experimenting with different *k* values, it's possible to see that the time needed by Glucose for finding the model (or showing none exists) grows when nearing the actual value of the lowest *k*. It runs very fast for small *k* when such a superstring almost trivially doesn't exist, and for large *k* where the superstring doesn't need to have as much overlap as for smaller (but possible) *k* values.