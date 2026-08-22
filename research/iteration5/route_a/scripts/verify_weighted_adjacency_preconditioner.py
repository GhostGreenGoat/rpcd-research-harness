"""Exact finite reconstruction of the weighted-adjacency preconditioner lemma.

The quantified proof is in ``weighted_adjacency_dual.md``.  This verifier
checks the permutation average formula on rational matrices and reconstructs
the cubic Bernstein coefficients symbolically.  It is not an audit of the
still-open Q inequality.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import sympy as sp


def order_factor(matrix: sp.Matrix, order: tuple[int, ...]) -> sp.Matrix:
    n = matrix.rows
    position = {coordinate: k for k, coordinate in enumerate(order)}
    factor = sp.eye(n)
    for i in range(n):
        for j in range(n):
            if position[j] < position[i]:
                factor[i, j] = matrix[i, j]
    return factor


def adjacency_difference(matrix: sp.Matrix, order: tuple[int, ...]) -> sp.Matrix:
    result = sp.eye(matrix.rows)
    for k in range(1, matrix.rows):
        current, previous = order[k], order[k - 1]
        result[current, previous] = -matrix[current, previous]
    return result


def exact_average_check() -> dict[str, object]:
    matrix = sp.Matrix(
        [
            [1, sp.Rational(1, 4), sp.Rational(-1, 5), sp.Rational(1, 7)],
            [sp.Rational(1, 4), 1, sp.Rational(1, 6), sp.Rational(-1, 8)],
            [sp.Rational(-1, 5), sp.Rational(1, 6), 1, sp.Rational(1, 9)],
            [sp.Rational(1, 7), sp.Rational(-1, 8), sp.Rational(1, 9), 1],
        ]
    )
    assert matrix.is_positive_definite
    n = matrix.rows
    average = sp.zeros(n)
    direct_average = sp.zeros(n)
    direct_q = sp.zeros(n)
    q_moment = sp.zeros(n)
    for order in itertools.permutations(range(n)):
        triangular = order_factor(matrix, order)
        difference = adjacency_difference(matrix, order)
        frame = difference.T * difference
        average += frame
        direct_average += difference.T
        direct_defect = difference * triangular
        direct_q += direct_defect * direct_defect.T
        q_moment += frame * triangular * triangular.T * frame
    average /= math.factorial(n)
    q_moment /= math.factorial(n)
    direct_average /= math.factorial(n)
    direct_q /= math.factorial(n)
    diagonal = sp.diag(*[(matrix * matrix)[i, i] for i in range(n)])
    closed = ((n + 1) * sp.eye(n) - 2 * matrix + diagonal) / n
    assert sp.simplify(average - closed) == sp.zeros(n)
    direct_closed = ((n + 1) * sp.eye(n) - matrix) / n
    assert sp.simplify(direct_average - direct_closed) == sp.zeros(n)
    assert q_moment.is_positive_definite
    assert direct_q.is_positive_definite
    return {
        "dimension": n,
        "orders": math.factorial(n),
        "average_formula_exact": True,
        "direct_average_formula_exact": True,
        "q_positive_definite": True,
    }


def bernstein_check() -> dict[str, object]:
    n, mu, lam, theta = sp.symbols(
        "n mu lambda theta", integer=False, positive=True
    )
    upper = n - (n - 1) * mu
    polynomial = lam * ((n - lam) ** 2 + n + (n - 1) * mu**2) - n**2 * mu
    substituted = sp.Poly(
        sp.expand(polynomial.subs(lam, mu + theta * (upper - mu))), theta
    )
    # Bernstein control coefficients can be reconstructed from endpoint
    # values and endpoint derivatives for a cubic.
    width = upper - mu
    b0 = sp.factor(polynomial.subs(lam, mu))
    b1 = sp.factor(b0 + width * sp.diff(polynomial, lam).subs(lam, mu) / 3)
    b3 = sp.factor(polynomial.subs(lam, upper))
    b2 = sp.factor(b3 - width * sp.diff(polynomial, lam).subs(lam, upper) / 3)
    bernstein = sp.expand(
        b0 * (1 - theta) ** 3
        + 3 * b1 * theta * (1 - theta) ** 2
        + 3 * b2 * theta**2 * (1 - theta)
        + b3 * theta**3
    )
    assert sp.expand(bernstein - substituted.as_expr()) == 0
    expected = [
        n * mu * (1 - mu) ** 2,
        n
        * (1 - mu)
        * (mu**2 * (n - 1) - mu * (4 * n - 3) + n**2 + n)
        / 3,
        n
        * (1 - mu)
        * (-mu**2 * (n - 1) + mu * (2 * n**2 - 5 * n + 3) + 2 * n)
        / 3,
        n * (1 - mu) * (mu**2 * (n - 1) ** 2 - mu * (n - 1) + n),
    ]
    for actual, target in zip((b0, b1, b2, b3), expected):
        assert sp.factor(actual - target) == 0
    return {
        "symbolic_identity": True,
        "bernstein_coefficients": [str(sp.factor(value)) for value in expected],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_a/evidence/weighted_adjacency_preconditioner.json"
        ),
    )
    args = parser.parse_args()
    result = {
        "schema_version": "1.0",
        "evidence_level": "E3 proof-draft finite reconstruction",
        "claim": "P_B=E[D_pi^T D_pi] >= mu B^{-1}",
        "average_check": exact_average_check(),
        "bernstein_check": bernstein_check(),
        "open_target": "Q_B <= (2/mu) P_B B P_B",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
