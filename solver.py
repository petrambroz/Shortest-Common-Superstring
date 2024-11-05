#!/usr/bin/env python3
import subprocess
from argparse import ArgumentParser


class ShortestCommonSuperstring:
    def __init__(self, k: int, solver_path: str, output_path: str, input_path: str):
        self.k = k
        self.solver_path = solver_path
        self.output_path = output_path
        self.input_path = input_path

        self.strings = []

    def load_input(self):
        with open(self.input_path, "r") as file:
            for line in file:
                string = line.strip()
                if string:
                    if not all(c in '01' for c in string):
                        raise ValueError("Input string contains characters other than '0' and '1'")
                    self.strings.append(string)

    def write_to_file(self, clauses):
        with open(self.output_path, 'w') as f:
            total_vars = max(max(abs(lit) for lit in clause) for clause in clauses)
            total_clauses = len(clauses)
            f.write(f"p cnf {total_vars} {total_clauses}\n")
            for clause in clauses:
                f.write(' '.join(map(str, clause)) + ' 0\n')

    def encode(self):
        clauses = []
        self.write_to_file(clauses)

    def decode_result(self):
        pass

    def run_solver(self):
        result = subprocess.run([self.solver_path, "-model", "-verb=0", self.output_path])
        return result.stdout

    def solve(self):
        self.load_input()
        self.encode()
        self.run_solver()
        result = self.decode_result()
        return result

    def parse_glucose_output(self):
        model = []
        for line in self.output_path.splitlines():
            if line.startswith('v'):
                model.extend(map(int, line.split()[1:]))
        return model


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=("Output file for the CNF formula in DIMACS format.")
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=("Path to the SAT solver to be used.")
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.txt",
        type=str,
        help=("Input file with the binary strings separated by newline.")
    )
    parser.add_argument(
        "-k",
        type=int,
        help=("Maximum length of the superstring."),
        required=True
    )
    return parser.parse_args()


if (__name__ == "__main__"):
    args = parse_args()
    try:
        solver = ShortestCommonSuperstring(args.k, args.solver, args.output, args.input)
    except Exception as e:
        print(f"An error occurred: {e}")
