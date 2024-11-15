#!/usr/bin/env python3
import subprocess
import os
from argparse import ArgumentParser


class ShortestCommonSuperstring:
    def __init__(self, solver_path: str, output_path: str, input_path: str, verbose: bool):
        self.x = {}
        self.y = {}
        self.solver_path = solver_path
        self.output_path = output_path
        self.input_path = input_path
        self.verbose = verbose

        self.longest_str = 0
        self.total_length = 0
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
        """
        Loads binary strings from the input file specified by `self.input_path`.

        Each non-empty line is stripped of whitespace and validated to contain only '0' and '1' characters.
        Stores the total length of the strings and the length of the longest string.

        Raises:
            ValueError: If a string contains characters other than '0' and '1'.
        """
        with open(self.input_path, "r") as file:
            for line in file:
                string = line.strip()
                if not string:
                    continue
                if any(c not in '01' for c in string):
                    raise ValueError("Input string contains characters other than '0' and '1'")
                self.strings.append(string)
                self.total_length += len(string)
                self.longest_str = max(self.longest_str, len(string))

    def write_to_file(self, clauses):
        with open(self.output_path, 'w') as f:
            total_vars = max(max(abs(lit) for lit in clause) for clause in clauses)
            total_clauses = len(clauses)
            f.write(f"p cnf {total_vars} {total_clauses}\n")
            for clause in clauses:
                f.write(' '.join(map(str, clause)) + ' 0\n')

    def encode(self):
        clauses = []
        var_count = 1
        self.x = [0] * (2 * self.k)

        # Assign unique variables for each position in the superstring
        for i in range(2 * self.k):
            self.x[i] = var_count
            var_count += 1

        # Assign unique variables for each possible starting position of each string
        for i in range(len(self.strings)):
            for j in range(self.k - len(self.strings[i]) + 1):
                self.y[(i, j)] = var_count
                var_count += 1

        # ensure every position in superstring is either 0 or 1
        for i in range(self.k):
            clauses.append([self.x[(2*i)], self.x[(2*i+1)]])
            clauses.append([-self.x[(2*i)], -self.x[(2*i+1)]])

        # ensuure each string has exactly 1 starting position
        for i, string in enumerate(self.strings):
            valid_positions = [
                self.y[(i, j)]
                for j in range(self.k - len(string) + 1)
            ]
            clauses.append(valid_positions)
            for j in range(self.k - len(string) + 1):
                for k in range(j + 1, self.k - len(string) + 1):
                    clauses.append([-self.y[(i, j)], -self.y[(i, k)]])

        # ensure that characters after a starting position match characters in the given string
        for i, string in enumerate(self.strings):
            for j in range(self.k - len(string) + 1):
                for k in range(len(string)):
                    char_value = int(string[k])
                    clauses.append([-self.y[(i, j)], -self.x[2 * (j + k) + 1 - char_value]])

        self.write_to_file(clauses)

    def decode_result(self, model) -> str | None:
        if model:
            result = [''] * self.k
            for i in range(self.k):
                if (2*i+1) in model:
                    result[i] = '0'
                elif (2*i+2) in model:
                    result[i] = '1'
            return ''.join(result).strip()
        else:
            return None

    def run_solver(self) -> str:
        result = subprocess.run([self.solver_path, "-model", "-verb=0", self.output_path],
                                capture_output=True, text=True)
        return result.stdout

    def solve(self, k: int) -> str | None:
        self.k = k
        if not isinstance(self.k, int) or self.k <= 0:
            raise ValueError("k must be a whole number greater than 0")

        self.load_input()

        if k < self.longest_str:
            raise ValueError(
                f"k must be at least {self.longest_str}, "
                "which is the length of the longest string in the input."
            )

        if self.verbose:
            print("Input successfully loaded.")

        self.encode()

        if self.verbose:
            print("Problem encoded into CNF, starting Glucose...")

        model = self.parse_glucose_output(self.run_solver())
        return self.decode_result(model)

    def find_min(self) -> str:
        self.load_input()

        if self.verbose:
            print("Input successfully loaded.")

        low = self.longest_str
        high = self.total_length
        result = None
        steps = 0

        while low <= high:
            steps += 1
            mid = (low + high) // 2
            self.k = mid
            self.encode()

            if self.verbose:
                print(f"Trying with k={self.k}")

            model = self.parse_glucose_output(self.run_solver())
            decoded_result = self.decode_result(model)

            if decoded_result:
                result = decoded_result
                high = mid - 1

                if self.verbose:
                    print(f"Found a solution for k={self.k}")
                    print()
            else:
                if self.verbose:
                    print(f"Solution for k={self.k} doesn't exist")
                    print()
                low = mid + 1

        if self.verbose:
            print(f"Completed in {steps} steps.")

        return result

    def parse_glucose_output(self, output):
        model = []
        for line in output.splitlines():
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
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help=("Increase output verbosity.")
    )
    return parser.parse_args()


if (__name__ == "__main__"):
    args = parse_args()
    try:
        solver = ShortestCommonSuperstring(args.solver, args.output, args.input, args.verbose)
        if args.k is not None:
            res = solver.solve(args.k)
            if res:
                print(f"The shortest superstring of length {len(res)} is: {res}")
            else:
                print(f"A superstring of length {args.k} doesn't exist.")
        else:
            res = solver.find_min()
            print(f"The shortest superstring has length {len(res)} and is: {res}")
    except Exception as e:
        print(f"An error occurred: {e}")
