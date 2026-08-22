"""Exact algebra checks for the Iteration-5 weighted prefix/SOS route.

The accompanying markdown contains the quantified proofs.  This script checks
finite formulae and symbolic factorizations; it is not a formal proof system.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def deletion_data(matrix: sp.Matrix, index: int) -> tuple[sp.Matrix, sp.Matrix]:
    size = matrix.rows
    keep = [j for j in range(size) if j != index]
    child = matrix.extract(keep, keep)
    lift = sp.zeros(size - 1, size)
    for local, original in enumerate(keep):
        lift[local, original] = 1
        lift[local, index] = -matrix[original, index]
    return child, lift


def j2(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    diagonal_square = sp.diag(*[(matrix * matrix)[i, i] for i in range(size)])
    return ((2 * size - 1) * sp.eye(size) - 2 * matrix + diagonal_square) / (
        size * (size - 1)
    )


def j3_bellman(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    result = sp.eye(size) / size
    for index in range(size):
        child, lift = deletion_data(matrix, index)
        result += lift.T * j2(child) * lift / size
    return sp.simplify(result)


def third_frame(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    square = matrix * matrix
    result = sp.zeros(size)
    for first in range(size):
        for second in range(size):
            if first == second:
                continue
            weight = square[second, second] - matrix[first, second] ** 2
            vector = sp.eye(size)[:, second] - matrix[first, second] * sp.eye(size)[:, first]
            result += weight * vector * vector.T
    return sp.simplify(result)


def j3_closed(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    square = matrix * matrix
    cube = square * matrix
    diagonal_square = sp.diag(*[square[i, i] for i in range(size)])
    diagonal_cube = sp.diag(*[cube[i, i] for i in range(size)])
    q = size * sp.eye(size) - 2 * matrix + diagonal_square
    r = size * matrix - 2 * square + diagonal_cube
    return sp.simplify(
        sp.eye(size) / size
        + ((2 * size - 3) * q - 2 * r + third_frame(matrix))
        / (size * (size - 1) * (size - 2))
    )


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol, degree: int):
    expanded = sp.Poly(sp.expand(polynomial), variable)
    powers = [expanded.nth(index) for index in range(degree + 1)]
    return [
        sp.factor(
            sum(
                powers[index]
                * sp.binomial(position, index)
                / sp.binomial(degree, index)
                for index in range(position + 1)
            )
        )
        for position in range(degree + 1)
    ]


def symbolic_compound_check() -> dict[str, object]:
    m = sp.symbols("m", integer=True, positive=True)
    a = sp.symbols("a", real=True)
    b = sp.symbols("b", nonnegative=True)
    r = sp.symbols("r", integer=True, nonnegative=True)
    c = sp.symbols("c", nonnegative=True)

    d2 = 1 + (m - 1) * a**2
    d3 = 1 + 3 * (m - 1) * a**2 + (m - 1) * (m - 2) * a**3
    weight = 1 + (m - 2) * a**2
    lambda_perp = 1 - a
    lambda_parallel = 1 + (m - 1) * a
    frame_perp = weight * ((m - 1) * (1 + a**2) + 2 * a)
    frame_parallel = weight * (m - 1) * (1 - a) ** 2

    def weighted_eigenvalue(lam, frame):
        j2_value = (2 * m - 1 - 2 * lam + d2) / (m * (m - 1))
        j3_value = sp.Rational(1, 1) / m + (
            (2 * m - 3) * (m - 2 * lam + d2)
            - 2 * (m * lam - 2 * lam**2 + d3)
            + frame
        ) / (m * (m - 1) * (m - 2))
        return sp.factor(j3_value - j2_value / 2)

    c_perp = weighted_eigenvalue(lambda_perp, frame_perp)
    c_parallel = weighted_eigenvalue(lambda_parallel, frame_parallel)

    positive_perp_gap = sp.factor(
        lambda_perp * c_perp - 2 * (1 - a) / m
    )
    expected_positive_perp = sp.factor(
        -a
        * (a - 1)
        * (2 * a**2 - 4 * a + 5)
        * (a * m - a + 2)
        / (2 * m * (m - 1))
    )
    assert sp.simplify(positive_perp_gap - expected_positive_perp) == 0

    positive_parallel_gap = sp.factor(
        lambda_parallel * c_parallel - 2 * (1 - a) / m
    )
    positive_polynomial = sp.factor(2 * m * positive_parallel_gap / a)
    positive_b = sp.expand(positive_polynomial.subs(a, 1 - b).subs(m, r + 3))
    positive_bernstein = bernstein_coefficients(positive_b, b, 4)
    expected_positive_bernstein = [
        r + 3,
        (4 * r + 9) / 4,
        (7 * r + 9) / 6,
        (6 * r + 1) / 4,
        2 * (2 * r + 1),
    ]
    assert all(
        sp.simplify(left - right) == 0
        for left, right in zip(positive_bernstein, expected_positive_bernstein)
    )

    negative_parallel_gap = sp.factor(
        lambda_parallel * c_parallel - 2 * lambda_parallel / m
    )
    expected_negative_parallel = sp.factor(
        a
        * (a - 2)
        * (2 * a**2 - 4 * a + 5)
        * (a * m - a + 1)
        / (2 * m)
    )
    assert sp.simplify(negative_parallel_gap - expected_negative_parallel) == 0

    negative_perp_gap = sp.factor(lambda_perp * c_perp - 2 * lambda_parallel / m)
    negative_q = sp.factor(-2 * m * (m - 1) * negative_perp_gap / a)
    negative_substituted = sp.factor(
        (m - 1) ** 3 * negative_q.subs(a, -c / (m - 1))
    ).subs(m, r + 3)
    negative_bernstein = bernstein_coefficients(negative_substituted, c, 4)
    # Every coefficient below expands with positive coefficients in r.
    for coefficient in negative_bernstein:
        assert all(value > 0 for value in sp.Poly(sp.expand(coefficient), r).all_coeffs())

    # The stronger sufficient state L3 from the adaptive child polynomial.
    h_perp = -a
    h_parallel = (m - 1) * a
    h_diagonal_square = (m - 1) * a**2
    h_diagonal_cube = (m - 1) * (m - 2) * a**3
    f_off = a + (m - 2) * a**2

    def adaptive_s(h_eigen):
        return sp.expand(
            (m - 3) * h_eigen**2
            - 2 * h_eigen**3
            + 2 * h_diagonal_square * h_eigen
            + (m - 1) * f_off**2
        )

    def adaptive_l(h_eigen):
        numerator = (
            4 * (m - 1) * (m - 2)
            - 10 * (m - 2) * h_eigen
            + 8 * h_eigen**2
            + (3 * m - 14) * h_diagonal_square
            - 4 * h_diagonal_cube
            + 2 * adaptive_s(h_eigen) / (m - 2)
        )
        return sp.factor(numerator / (2 * m * (m - 1) * (m - 2)))

    adaptive_perp = adaptive_l(h_perp)
    adaptive_parallel = adaptive_l(h_parallel)
    # Positive a: mu=1-a.  Negative a: mu=1+(m-1)a.
    adaptive_positive_perp = sp.factor(adaptive_perp - 2 / m)
    adaptive_positive_parallel = sp.factor(
        (1 + (m - 1) * a) * adaptive_parallel - 2 * (1 - a) / m
    )
    adaptive_negative_parallel = sp.factor(adaptive_parallel - 2 / m)
    adaptive_negative_perp = sp.factor(
        (1 - a) * adaptive_perp - 2 * (1 + (m - 1) * a) / m
    )

    pos_perp_poly = sp.factor(
        adaptive_positive_perp * 2 * m * (m - 1) * (m - 2) / a
    )
    pos_parallel_poly = sp.factor(adaptive_positive_parallel * 2 * m / a)
    adaptive_pos_perp_bernstein = bernstein_coefficients(
        sp.expand(pos_perp_poly.subs(m, r + 3)), a, 3
    )
    adaptive_pos_parallel_bernstein = bernstein_coefficients(
        sp.expand(pos_parallel_poly.subs(m, r + 3)), a, 4
    )
    for coefficient in adaptive_pos_perp_bernstein + adaptive_pos_parallel_bernstein:
        assert all(value > 0 for value in sp.Poly(sp.expand(coefficient), r).all_coeffs())

    expected_negative_parallel = sp.factor(
        a * (a - 2) * (2 * a**2 - 4 * a + 5) / (2 * m)
    )
    assert sp.simplify(adaptive_negative_parallel - expected_negative_parallel) == 0
    neg_perp_poly = sp.factor(
        -adaptive_negative_perp * 2 * m * (m - 1) * (m - 2) / a
    )
    adaptive_neg_perp_scaled = sp.factor(
        (m - 1) ** 4 * neg_perp_poly.subs(a, -c / (m - 1))
    ).subs(m, r + 3)
    adaptive_neg_perp_bernstein = bernstein_coefficients(
        sp.expand(adaptive_neg_perp_scaled), c, 4
    )
    for coefficient in adaptive_neg_perp_bernstein:
        assert all(value > 0 for value in sp.Poly(sp.expand(coefficient), r).all_coeffs())

    return {
        "c_perp": str(c_perp),
        "c_parallel": str(c_parallel),
        "positive_a_bernstein_coefficients": [str(x) for x in positive_bernstein],
        "negative_a_bernstein_coefficients_after_positive_scaling": [
            str(x) for x in negative_bernstein
        ],
        "adaptive_L3_compound_certificate": True,
        "adaptive_positive_perp_bernstein": [
            str(x) for x in adaptive_pos_perp_bernstein
        ],
        "adaptive_positive_parallel_bernstein": [
            str(x) for x in adaptive_pos_parallel_bernstein
        ],
        "adaptive_negative_perp_bernstein_after_positive_scaling": [
            str(x) for x in adaptive_neg_perp_bernstein
        ],
    }


def exact_formula_checks() -> list[dict[str, object]]:
    matrices = [
        sp.Matrix(
            [
                [1, Q(1, 5), Q(-1, 6), Q(1, 7)],
                [Q(1, 5), 1, Q(1, 8), Q(-1, 9)],
                [Q(-1, 6), Q(1, 8), 1, Q(1, 10)],
                [Q(1, 7), Q(-1, 9), Q(1, 10), 1],
            ]
        ),
        sp.Matrix(
            [
                [1, Q(1, 4), Q(-1, 7), Q(1, 8), Q(-1, 9)],
                [Q(1, 4), 1, Q(1, 6), Q(-1, 10), Q(1, 11)],
                [Q(-1, 7), Q(1, 6), 1, Q(1, 9), Q(-1, 12)],
                [Q(1, 8), Q(-1, 10), Q(1, 9), 1, Q(1, 13)],
                [Q(-1, 9), Q(1, 11), Q(-1, 12), Q(1, 13), 1],
            ]
        ),
    ]
    records = []
    for matrix in matrices:
        residual = sp.simplify(j3_bellman(matrix) - j3_closed(matrix))
        assert residual == sp.zeros(matrix.rows)
        h = matrix - sp.eye(matrix.rows)
        row_square_gap = sp.diag(*[(h * h)[i, i] for i in range(matrix.rows)]) - (
            h * h
        ) / (matrix.rows - 1)
        # Exact LDL confirms the finite test instance of the general SOS lemma.
        assert all(entry >= 0 for entry in row_square_gap.cholesky(hermitian=False).diagonal())

        size = matrix.rows
        diagonal_h2 = sp.diag(*[(h * h)[i, i] for i in range(size)])
        diagonal_h3 = sp.diag(*[(h**3)[i, i] for i in range(size)])
        f = h + h**2 - diagonal_h2
        s_closed = (
            (size - 3) * h**2
            - 2 * h**3
            + h * diagonal_h2
            + diagonal_h2 * h
            + sp.diag(*[(f**2)[i, i] for i in range(size)])
        )
        s_direct = sp.zeros(size)
        adaptive_lift = sp.eye(size) / (2 * size)
        for index in range(size):
            child, lift = deletion_data(matrix, index)
            child_h = child - sp.eye(size - 1)
            s_direct += lift.T * child_h**2 * lift
            child_polynomial = (
                (3 * (size - 1) + 1) * sp.eye(size - 1)
                - 4 * child
                + 2 * child_h**2 / (size - 2)
            ) / (2 * (size - 1) * (size - 2))
            adaptive_lift += lift.T * child_polynomial * lift / size
        assert sp.simplify(s_direct - s_closed) == sp.zeros(size)

        adaptive_numerator = (
            4 * (size - 1) * (size - 2) * sp.eye(size)
            - 10 * (size - 2) * h
            + 8 * h**2
            + (3 * size - 14) * diagonal_h2
            - 4 * diagonal_h3
            + 2 * s_closed / (size - 2)
        )
        adaptive_closed = adaptive_numerator / (
            2 * size * (size - 1) * (size - 2)
        )
        assert sp.simplify(adaptive_lift - adaptive_closed) == sp.zeros(size)
        records.append(
            {
                "size": matrix.rows,
                "j3_closed_equals_bellman": True,
                "zero_diagonal_square_check": True,
                "adaptive_square_state_identity": True,
                "adaptive_lift_closed_formula": True,
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_c/evidence/WEIGHTED_PREFIX_EXACT_CHECKS.json"
        ),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E3 exact symbolic/fraction checks supporting a proof draft",
        "scope_warning": "The markdown proof carries the universal quantifiers.",
        "finite_formula_checks": exact_formula_checks(),
        "compound_symbolic_check": symbolic_compound_check(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "PASS"}))


if __name__ == "__main__":
    main()
