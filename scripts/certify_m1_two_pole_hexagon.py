"""Exact certificate for the M1 two-pole/hexagonal-ring boundary family.

The computation uses only ``fractions.Fraction`` in the quadratic field
Q(sqrt(21)).  It enumerates all 8! orders and evaluates the slow-boundary
Schur-complement coefficient from ITER3_M1_STRONG_ONE_EPOCH_ENERGY.md.

This is a finite exact computation, not a proof of the universal M1 boundary
inequality.  Runtime is intentionally not part of the default unit-test suite.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations
import json
from math import factorial
from pathlib import Path


Scalar = tuple[Fraction, Fraction]
ZERO: Scalar = (Fraction(0), Fraction(0))
ONE: Scalar = (Fraction(1), Fraction(0))
SQRT_21 = 21


def add(left: Scalar, right: Scalar) -> Scalar:
    return left[0] + right[0], left[1] + right[1]


def subtract(left: Scalar, right: Scalar) -> Scalar:
    return left[0] - right[0], left[1] - right[1]


def multiply(left: Scalar, right: Scalar) -> Scalar:
    return (
        left[0] * right[0] + SQRT_21 * left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def scale(value: Fraction, scalar: Scalar) -> Scalar:
    return value * scalar[0], value * scalar[1]


def dot(left: list[Scalar], right: list[Scalar]) -> Scalar:
    result = ZERO
    for left_value, right_value in zip(left, right, strict=True):
        result = add(result, multiply(left_value, right_value))
    return result


def matrix_vector(matrix: list[list[Scalar]], vector: list[Scalar]) -> list[Scalar]:
    return [dot(row, vector) for row in matrix]


def correlation_matrix() -> list[list[Scalar]]:
    """Return C for two poles and the a=4/sqrt(21) latitude hexagon."""
    n = 8
    pole_ring = (Fraction(0), Fraction(4, 21))
    cosines = [
        Fraction(1),
        Fraction(1, 2),
        Fraction(-1, 2),
        Fraction(-1),
        Fraction(-1, 2),
        Fraction(1, 2),
    ]
    matrix = [[ZERO for _ in range(n)] for _ in range(n)]
    for row in range(n):
        for column in range(n):
            if row == column or (row < 2 and column < 2):
                value = ONE
            elif (row < 2) != (column < 2):
                value = pole_ring
            else:
                separation = ((row - 2) - (column - 2)) % 6
                value = (
                    Fraction(16, 21) + Fraction(5, 21) * cosines[separation],
                    Fraction(0),
                )
            matrix[row][column] = value
    return matrix


def triangular_solve(
    correlation: list[list[Scalar]],
    order: tuple[int, ...],
    vector: list[Scalar],
) -> list[Scalar]:
    result: list[Scalar] = []
    for position, row in enumerate(order):
        value = vector[row]
        for earlier in range(position):
            value = subtract(
                value,
                multiply(correlation[row][order[earlier]], result[earlier]),
            )
        result.append(value)
    return result


def exact_coefficients() -> dict[str, Fraction]:
    correlation = correlation_matrix()
    pole_ring = (Fraction(0), Fraction(4, 21))
    vectors = {
        "pole_difference": [ONE, (Fraction(-1), Fraction(0))] + [ZERO] * 6,
        "ring_harmonic_2_cos": [ZERO, ZERO]
        + [(Fraction(value), Fraction(0)) for value in (2, -1, -1, 2, -1, -1)],
        "ring_harmonic_2_sin": [ZERO, ZERO]
        + [(Fraction(value), Fraction(0)) for value in (0, 1, -1, 0, 1, -1)],
        "ring_harmonic_3": [ZERO, ZERO]
        + [(Fraction(value), Fraction(0)) for value in (1, -1, 1, -1, 1, -1)],
        "trivial_null": [scale(Fraction(-3), pole_ring)] * 2 + [ONE] * 6,
        "ring_harmonic_1_cos": [ZERO, ZERO]
        + [(Fraction(value), Fraction(0)) for value in (2, 1, -1, -2, -1, 1)],
        "ring_harmonic_1_sin": [ZERO, ZERO]
        + [(Fraction(value), Fraction(0)) for value in (0, 1, 1, 0, -1, -1)],
        "trivial_range": [ONE, ONE] + [pole_ring] * 6,
    }
    names = list(vectors)

    # These eight mutually orthogonal eigenvectors certify rank three and
    # exhaust both the five-dimensional kernel and three-dimensional range.
    expected_actions = {
        "pole_difference": Fraction(0),
        "ring_harmonic_2_cos": Fraction(0),
        "ring_harmonic_2_sin": Fraction(0),
        "ring_harmonic_3": Fraction(0),
        "trivial_null": Fraction(0),
        "ring_harmonic_1_cos": Fraction(5, 7),
        "ring_harmonic_1_sin": Fraction(5, 7),
        "trivial_range": Fraction(46, 7),
    }
    for left_index, left in enumerate(names):
        norm = dot(vectors[left], vectors[left])
        if norm[1] != 0 or norm[0] <= 0:
            raise AssertionError(f"invalid basis norm for {left}")
        for right in names[left_index + 1 :]:
            if dot(vectors[left], vectors[right]) != ZERO:
                raise AssertionError(f"basis is not orthogonal: {left}, {right}")
        expected = [scale(expected_actions[left], value) for value in vectors[left]]
        if matrix_vector(correlation, vectors[left]) != expected:
            raise AssertionError(f"incorrect correlation action on {left}")

    accumulated = {
        (left, right): ZERO
        for left in names
        for right in names
        if names.index(left) <= names.index(right)
    }

    for order in permutations(range(8)):
        solved = {
            name: triangular_solve(correlation, order, vector)
            for name, vector in vectors.items()
        }
        for left_index, left in enumerate(names):
            for right in names[left_index:]:
                key = left, right
                accumulated[key] = add(accumulated[key], dot(solved[left], solved[right]))

    divisor = Fraction(factorial(8))
    averaged = {key: scale(1 / divisor, value) for key, value in accumulated.items()}
    norms = {name: dot(vector, vector) for name, vector in vectors.items()}
    allowed_irrational_key = ("trivial_null", "trivial_range")
    for key, value in averaged.items():
        if value[1] != 0 and key != allowed_irrational_key:
            raise AssertionError(f"unexpected irrational component at {key}")
    for name, value in norms.items():
        if value[1] != 0:
            raise AssertionError(f"unexpected irrational norm for {name}")

    # Group symmetry predicts that every off-block entry vanishes except the
    # coupling between the two copies of the trivial representation.  Assert
    # this directly so that a future matrix edit cannot silently omit a block.
    for key, value in averaged.items():
        left, right = key
        if left != right and key != allowed_irrational_key and value != ZERO:
            raise AssertionError(f"unexpected nonzero K block at {key}: {value}")

    coefficients: dict[str, Fraction] = {}
    for name in (
        "pole_difference",
        "ring_harmonic_2_cos",
        "ring_harmonic_2_sin",
        "ring_harmonic_3",
    ):
        coefficients[name] = averaged[(name, name)][0] / norms[name][0]
    if coefficients["ring_harmonic_2_cos"] != coefficients["ring_harmonic_2_sin"]:
        raise AssertionError("the second-harmonic partners do not agree")

    null_norm = norms["trivial_null"][0]
    range_norm = norms["trivial_range"][0]
    null_value = averaged[("trivial_null", "trivial_null")][0] / null_norm
    range_value = averaged[("trivial_range", "trivial_range")][0] / range_norm
    cross = averaged[("trivial_null", "trivial_range")]
    cross_squared = multiply(cross, cross)
    if cross_squared[1] != 0:
        raise AssertionError("the squared coupling must be rational")
    coefficients["trivial_schur"] = (
        null_value - cross_squared[0] / (null_norm * range_norm * range_value)
    )
    return coefficients


def check_evidence(coefficients: dict[str, Fraction]) -> None:
    evidence_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "evidence"
        / "M1_TWO_POLE_HEXAGON_EXACT_2026_08_21.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    expected = evidence["boundary_schur_coefficients"]
    mapping = {
        "pole_difference": "pole_difference",
        "ring_harmonic_2": "ring_harmonic_2_cos",
        "ring_harmonic_3": "ring_harmonic_3",
        "trivial_schur": "trivial_schur",
    }
    for evidence_name, coefficient_name in mapping.items():
        if expected[evidence_name] != str(coefficients[coefficient_name]):
            raise AssertionError(f"evidence drift for {evidence_name}")


def main() -> None:
    coefficients = exact_coefficients()
    check_evidence(coefficients)
    minimum_name = min(coefficients, key=coefficients.__getitem__)
    minimum = coefficients[minimum_name]
    if minimum_name != "pole_difference" or minimum <= 2:
        raise AssertionError("the expected exact boundary certificate failed")
    for name, value in coefficients.items():
        print(f"{name}: {value} = {float(value):.15f}; excess_over_2={value - 2}")
    print(f"minimum: {minimum_name}")


if __name__ == "__main__":
    main()
