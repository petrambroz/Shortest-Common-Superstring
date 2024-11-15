# Example inputs

This directory contains several sample inputs to demonstrate the functionality.

## simple1, simple2
These two examples show very simple inputs where it's easy to find the superstring even without the program.
Use:
```
./solver.py -v -i examples/simple1.txt
./solver.py -v -i examples/simple2.txt
```

## simple with no solution
Since it's impossible to have a set of strings wihtout a common superstrig (we can always simply join all of the strings into one large superstring), I've created this example to demonstrate the use with given *k*. The strings `1111` and `1100` certainly have a superstring for *k=6*: `111100`, but not for *k=5*.
Use:
```
./solver.py -v -k 4 -i examples/simple_nonexistent_for_k=4
```
## non-trivial example
The input consists of 11 strings of a combined length of 118 characters and the longest string being 16 characters. The shortest superstring is certainly between 16 and 108 characters long. The program starts with k=62 and then continues to search for the lowest possible *k* using binary search. The resulting superstring should be 66 characters long and should be found in 7 steps.
Use:
```
./solver.py -v -i examples/nontrivial.txt
```