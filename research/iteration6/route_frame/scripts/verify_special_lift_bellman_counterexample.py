"""Exact special-RPCD-lift counterexample to the inverse Bellman potential."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def frobenius(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sum(left[i, j] * right[i, j] for i in range(left.rows) for j in range(left.cols))


def outer(vector: sp.Matrix) -> sp.Matrix:
    return vector * vector.T


def main() -> None:
    n = 9
    ambient = n + 1
    identity = sp.eye(ambient)
    zero_matrix = sp.zeros(ambient)

    vectors = []
    rank_one = []
    complements = []
    for label in range(1, n + 1):
        vector = sp.zeros(ambient, 1)
        vector[0] = 1
        vector[label] = 1
        vectors.append(vector)
        projector = outer(vector) / 2
        rank_one.append(projector)
        complements.append(identity - projector)
        assert projector * projector == projector

    gram = sp.Matrix([[frobenius(x, y) / 2 for y in vectors] for x in vectors])
    assert gram == (sp.eye(n) + sp.ones(n)) / 2
    matrix_w = sp.Matrix.hstack(*vectors)
    span_projector = sp.simplify(matrix_w * (matrix_w.T * matrix_w).inv() * matrix_w.T)

    # Seven-dimensional fixed space for permutations of labels 3,...,9.
    orthogonal_vectors = []
    raw_vectors = [vectors[0], vectors[1], sum(vectors[2:], sp.zeros(ambient, 1))]
    for raw in raw_vectors:
        vector = raw
        for previous in orthogonal_vectors:
            vector = sp.simplify(
                vector - previous * frobenius(previous, vector) / frobenius(previous, previous)
            )
        denominator = sp.ilcm(*[sp.denom(entry) for entry in vector])
        orthogonal_vectors.append(sp.simplify(denominator * vector))

    basis7 = [outer(vector) / frobenius(vector, vector) for vector in orthogonal_vectors]
    for first in range(3):
        for second in range(first + 1, 3):
            left, right = orthogonal_vectors[first], orthogonal_vectors[second]
            basis7.append(left * right.T + right * left.T)
    basis7.append(sp.simplify(span_projector - sum(basis7[:3], zero_matrix)))
    gram7 = sp.diag(*[frobenius(item, item) for item in basis7])
    assert all(
        frobenius(basis7[i], basis7[j]) == 0
        for i in range(7)
        for j in range(7)
        if i != j
    )

    def coordinates(matrix: sp.Matrix) -> sp.Matrix:
        return gram7.inv() * sp.Matrix([frobenius(item, matrix) for item in basis7])

    def combine(coefficients: sp.Matrix) -> sp.Matrix:
        return sum((coefficients[i] * basis7[i] for i in range(7)), zero_matrix)

    def pi(index: int, matrix: sp.Matrix) -> sp.Matrix:
        return complements[index] * matrix * complements[index]

    def q(index: int, matrix: sp.Matrix) -> sp.Matrix:
        return matrix - pi(index, matrix)

    def operator_matrix(indices: list[int]) -> sp.Matrix:
        columns = []
        for matrix in basis7:
            image = matrix + sum((q(index, matrix) for index in indices), zero_matrix)
            columns.append(coordinates(sp.simplify(image)))
        return sp.Matrix.hstack(*columns)

    all_indices = list(range(n))
    without_first = list(range(1, n))
    without_second = [index for index in range(n) if index != 1]
    operator_all = operator_matrix(all_indices)
    operator_first = operator_matrix(without_first)
    operator_second = operator_matrix(without_second)

    def solve(operator: sp.Matrix, matrix: sp.Matrix) -> sp.Matrix:
        answer = combine(operator.inv() * coordinates(matrix))
        return sp.simplify(answer)

    # Four-dimensional fixed space for permutations of labels 2,...,9.
    vector_a = vectors[0]
    sum_others = sum(vectors[1:], sp.zeros(ambient, 1))
    vector_t = 2 * sum_others - (n - 1) * vector_a
    basis4 = [
        outer(vector_a) / frobenius(vector_a, vector_a),
        outer(vector_t) / frobenius(vector_t, vector_t),
        vector_a * vector_t.T + vector_t * vector_a.T,
    ]
    basis4.append(sp.simplify(span_projector - basis4[0] - basis4[1]))

    gap4 = sp.zeros(4)
    for row, left in enumerate(basis4):
        for column, right in enumerate(basis4):
            rhs = frobenius(left, solve(operator_all, right))
            first = frobenius(pi(0, left), solve(operator_first, pi(0, right)))
            second = frobenius(pi(1, left), solve(operator_second, pi(1, right)))
            # Labels 2,...,9 are symmetric for every matrix in basis4.
            gap4[row, column] = sp.factor(rhs - (first + (n - 1) * second) / n)

    sum_vector = sum(vectors, sp.zeros(ambient, 1))
    invariant_parallel = outer(sum_vector) / frobenius(sum_vector, sum_vector)
    invariant_transverse = sp.simplify(span_projector - invariant_parallel)
    trivial_pairing = sp.Matrix(
        [
            [frobenius(invariant_parallel, item) for item in basis4],
            [frobenius(invariant_transverse, item) for item in basis4],
        ]
    )
    standard_basis = sp.Matrix.hstack(*trivial_pairing.nullspace())
    expected_standard_basis = sp.Matrix.hstack(
        sp.Matrix([-160, 160, 1, 0]), sp.Matrix([28, -35, 0, 1])
    )
    assert standard_basis == expected_standard_basis
    standard_gap = sp.simplify(standard_basis.T * gap4 * standard_basis)
    expected_gap = sp.Matrix(
        [
            [sp.Rational(-2212480, 7293), sp.Rational(404824, 7293)],
            [sp.Rational(404824, 7293), sp.Rational(-252182, 36465)],
        ]
    )
    assert standard_gap == expected_gap
    assert sp.factor(standard_gap.det()) == sp.Rational(-121894976, 123981)

    coefficients4 = standard_basis * sp.ones(2, 1)
    assert coefficients4 == sp.Matrix([-132, 125, 1, 1])
    test_matrix = sum((coefficients4[i] * basis4[i] for i in range(4)), zero_matrix)
    assert sp.simplify(span_projector * test_matrix * span_projector - test_matrix) == zero_matrix
    assert frobenius(invariant_parallel, test_matrix) == 0
    assert frobenius(invariant_transverse, test_matrix) == 0
    quadratic_gap = sp.factor((sp.ones(1, 2) * standard_gap * sp.ones(2, 1))[0])
    assert quadratic_gap == sp.Rational(-2422114, 12155)

    # Full ambient residual checks ensure the inverses were not artifacts of
    # a non-invariant coordinate restriction.
    rhs_solution = solve(operator_all, test_matrix)
    child_first_input = pi(0, test_matrix)
    child_second_input = pi(1, test_matrix)
    child_first_solution = solve(operator_first, child_first_input)
    child_second_solution = solve(operator_second, child_second_input)

    def apply(indices: list[int], matrix: sp.Matrix) -> sp.Matrix:
        return sp.simplify(matrix + sum((q(index, matrix) for index in indices), zero_matrix))

    assert apply(all_indices, rhs_solution) == test_matrix
    assert apply(without_first, child_first_solution) == child_first_input
    assert apply(without_second, child_second_solution) == child_second_input

    norm_squared = sp.factor(frobenius(test_matrix, test_matrix))
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E3 exact analytic counterexample with independent reconstruction",
        "n": n,
        "A": "(I+J)/2",
        "mu": "1/2",
        "lift_projection_rank": n,
        "standard_gap": [[str(standard_gap[i, j]) for j in range(2)] for i in range(2)],
        "standard_gap_determinant": str(sp.factor(standard_gap.det())),
        "test_coefficients_in_B4": [int(value) for value in coefficients4],
        "test_norm_squared": str(norm_squared),
        "quadratic_gap": str(quadratic_gap),
        "normalized_quadratic_gap": str(sp.factor(quadratic_gap / norm_squared)),
        "full_ambient_residual_checks": "passed exactly",
        "result": "special RPCD covariance-lift Bellman inequality is false",
        "scope": "Refutes this inverse potential, not the RPCD complexity target.",
    }
    target = Path("research/iteration6/route_frame/evidence/special_lift_bellman_counterexample.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
