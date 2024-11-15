#!/usr/bin/env python3
from random import randint
from argparse import ArgumentParser


def gen_strings(max_length: int, num_of_strings: int) -> list[str]:
    strings = []
    for _ in range(num_of_strings):
        length = randint(3, max_length)
        string = ""
        for __ in range(length):
            string += str(randint(0, 1))
        strings.append(string)
    return strings


def save_to_file(strings: list, output_file: str):
    with open(output_file, "w") as file:
        for string in strings:
            file.write(string + "\n")


parser = ArgumentParser()
parser.add_argument(
    "-n",
    "--num-of-strings",
    type=int,
    required=True,
    help="Number of strings to generate.",
    choices=range(2, 100)
)
parser.add_argument(
    "-m",
    "--max-length",
    type=int,
    required=True,
    help="Maximum length of the strings.",
    choices=range(3, 100)
)
args = parser.parse_args()
a = gen_strings(args.max_length, args.num_of_strings)
save_to_file(a, "input.txt")
