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
        self.sanity_checks()

    def sanity_checks(self):
        """
        Perform various checks to ensure the input, output, and solver paths are valid.
        Raises appropriate exceptions if any checks fail.
        """
        # check the input file
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file \"{self.input_path}\" does not exist")
        if os.path.isdir(self.input_path):
            raise IsADirectoryError(f"Input path \"{self.input_path}\" is a directory, not a file")
        if not os.access(self.input_path, os.R_OK):
            raise PermissionError(f"Input file \"{self.input_path}\" is not readable")
        if os.path.getsize(self.input_path) == 0:
            raise ValueError(f"Input file \"{self.input_path}\" is empty")

        # check the output file
        if os.path.isdir(self.output_path):
            raise IsADirectoryError(f"Output path \"{self.output_path}\" is a directory, not a file")
        if os.path.exists(self.output_path) and not os.access(self.output_path, os.W_OK):
            raise PermissionError(f"Output file \"{self.output_path}\" is not writable")

        # check the solver path
        if not any(os.access(os.path.join(path, self.solver_path), os.X_OK)
                   for path in os.environ["PATH"].split(os.pathsep)):
            if not os.path.exists(self.solver_path):
                raise FileNotFoundError(f"Solver path \"{self.solver_path}\" does not exist")
            if os.path.isdir(self.solver_path):
                raise IsADirectoryError(f"Solver path \"{self.solver_path}\" is a directory, not a file")
            if not os.access(self.solver_path, os.X_OK):
                raise PermissionError(f"Solver path \"{self.solver_path}\" is not executable")

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
