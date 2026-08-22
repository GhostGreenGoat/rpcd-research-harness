"""Exact diagnostic for the Iteration-6 projection-superoperator lift."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def main() -> None:
    n = 3
    vectors = [
        sp.Matrix([1, 0, 0]),
        sp.Matrix([sp.Rational(3, 5), sp.Rational(4, 5), 0]),
        sp.Matrix([0, sp.Rational(3, 5), sp.Rational(4, 5)]),
    ]
    synthesis = sp.Matrix.hstack(*vectors)
    gram = synthesis.T * synthesis
    base_frame = synthesis * synthesis.T
    identity = sp.eye(n)
    z = [identity - vector * vector.T for vector in vectors]
    lifted = [sp.kronecker_product(item, item) for item in z]
    lifted_identity = sp.eye(n * n)
    frame = sum((lifted_identity - item for item in lifted), sp.zeros(n * n))

    sym_product = sp.zeros(n * n)
    direct_covariance = sp.zeros(n * n)
    for order in itertools.permutations(range(n)):
        word = sp.eye(n * n)
        p = sp.eye(n)
        for index in order:
            word = lifted[index] * word
            p = z[index] * p
        sym_product += word
        direct_covariance += sp.kronecker_product(p, p)
    sym_product /= sp.factorial(n)
    direct_covariance /= sp.factorial(n)

    x = sp.Matrix([
        [2, sp.Rational(1, 3), sp.Rational(-2, 5)],
        [sp.Rational(1, 3), -1, sp.Rational(3, 7)],
        [sp.Rational(-2, 5), sp.Rational(3, 7), sp.Rational(4, 3)],
    ])
    vectorized = sp.Matrix(x).reshape(n * n, 1)
    frame_quadratic = (vectorized.T * frame * vectorized)[0]
    formula = 2 * sp.trace(x * x * base_frame) - sum(
        ((vector.T * x * vector)[0]) ** 2 for vector in vectors
    )

    output = {
        "kind": "exact projection-lift diagnostic",
        "gram": [[str(gram[i, j]) for j in range(n)] for i in range(n)],
        "base_frame": [[str(base_frame[i, j]) for j in range(n)] for i in range(n)],
        "unit_diagonal": [str(gram[i, i]) for i in range(n)],
        "symmetrized_product_minus_direct_covariance_is_zero": bool(
            sym_product == direct_covariance
        ),
        "frame_quadratic": str(frame_quadratic),
        "closed_formula": str(formula),
        "frame_formula_residual": str(sp.factor(frame_quadratic - formula)),
        "scope": "Exact identity check for one rational Gram frame; quantified inequalities are proved in the accompanying note.",
    }
    path = Path("research/iteration6/root/evidence/PROJECTION_LIFT_EXACT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
