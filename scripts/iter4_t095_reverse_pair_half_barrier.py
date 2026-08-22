"""Exact boundary obstruction to a word-by-reverse-word half proof.

For the rank-one correlation C=11^T in dimension nine, the lower triangular
factor for the identity order is the cumulative-sum matrix.  Its inverse D is
the first-difference matrix.  The reverse-order contribution is D D^T rather
than D^T D.  Their pair average has a kernel Rayleigh quotient 3/8 < 1/2.
"""

from fractions import Fraction as F


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def exact_record() -> dict[str, F]:
    n = 9
    difference = [
        [F(int(i == j)) - F(int(i == j + 1)) for j in range(n)]
        for i in range(n)
    ]
    transpose = [list(row) for row in zip(*difference)]
    vector = [F(-1)] * 4 + [F(0)] + [F(1)] * 4
    assert sum(vector) == 0
    forward = matvec(difference, vector)
    reverse = matvec(transpose, vector)
    numerator = sum(x * x for x in forward) + sum(x * x for x in reverse)
    denominator = 2 * sum(x * x for x in vector)
    quotient = numerator / denominator
    assert quotient == F(3, 8)
    assert quotient < F(1, 2)
    return {
        "reverse_pair_kernel_quotient": quotient,
        "gap_to_one_half": quotient - F(1, 2),
    }


def main() -> None:
    for key, value in exact_record().items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
