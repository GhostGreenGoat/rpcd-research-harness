"""Exact symbolic attack on an S3-symmetric n=4 corank-one family.

The first three coordinates have common correlation a, and the fourth has
common correlation b with them.  Singularity imposes a=(3 b^2-1)/2.
"""

from __future__ import annotations

import argparse
import json
from itertools import permutations
from pathlib import Path

import sympy as sp


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol, degree: int) -> list[sp.Expr]:
    coefficients = sp.symbols(f"beta0:{degree + 1}")
    expansion = sum(
        coefficients[index]
        * sp.binomial(degree, index)
        * variable**index
        * (1 - variable) ** (degree - index)
        for index in range(degree + 1)
    )
    solution = sp.solve(
        sp.Poly(sp.expand(polynomial - expansion), variable).all_coeffs(),
        coefficients,
        dict=True,
    )[0]
    return [sp.factor(solution[value]) for value in coefficients]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T080_N4_S3_CORANK_ONE_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    b = sp.symbols("b", real=True)
    a = (3 * b**2 - 1) / 2
    c = sp.Matrix(
        [
            [1, a, a, b],
            [a, 1, a, b],
            [a, a, 1, b],
            [b, b, b, 1],
        ]
    )
    k = sp.zeros(4)
    for order in permutations(range(4)):
        p = sp.eye(4)[:, list(order)]
        cp = p.T * c * p
        lower = sp.Matrix(4, 4, lambda i, j: cp[i, j] if i >= j else 0)
        m = p * lower * p.T
        inverse = m.inv()
        k += inverse.T * inverse / 24
    u = sp.Matrix([1, 1, 1, -3 * b])
    assert sp.simplify(c * u) == sp.zeros(4, 1)
    schur_coefficient = sp.factor(u.dot(u) / (u.T * k.inv() * u)[0])
    gap_numerator, gap_denominator = sp.fraction(sp.factor(schur_coefficient - 2))
    s = sp.symbols("s", nonnegative=True)
    numerator_s = sp.Poly(gap_numerator, b).as_dict()
    denominator_core = sp.factor(gap_denominator / 192)
    # Both polynomials are even in b; map b^(2k) to s^k exactly.
    numerator_in_s = sum(coefficient * s ** (power[0] // 2) for power, coefficient in numerator_s.items())
    denominator_in_s = sum(
        coefficient * s ** (power[0] // 2)
        for power, coefficient in sp.Poly(denominator_core, b).as_dict().items()
    )
    numerator_bernstein = bernstein_coefficients(numerator_in_s, s, 11)
    denominator_bernstein = bernstein_coefficients(denominator_in_s, s, 6)
    assert all(value > 0 for value in numerator_bernstein)
    assert all(value > 0 for value in denominator_bernstein)
    print("schur_coefficient=")
    print(schur_coefficient)
    print("gap_numerator_factor=")
    print(sp.factor(gap_numerator))
    print("gap_denominator_factor=")
    print(sp.factor(gap_denominator))
    print("endpoint_b0=", sp.factor(schur_coefficient.subs(b, 0)))
    print("endpoint_b1=", sp.factor(sp.limit(schur_coefficient, b, 1, dir="-")))
    payload = {
        "status": "E2 exact symbolic artifact supporting an E3 n=4 symmetric-family proof draft",
        "family": "first three exchangeable; a=(3b^2-1)/2; fourth correlations b; 0<=b<=1",
        "kernel_vector": "(1,1,1,-3b)",
        "schur_coefficient": str(schur_coefficient),
        "gap_numerator_in_s": str(sp.factor(numerator_in_s)),
        "gap_denominator_without_192_in_s": str(sp.factor(denominator_in_s)),
        "numerator_bernstein_coefficients": [str(value) for value in numerator_bernstein],
        "denominator_bernstein_coefficients": [str(value) for value in denominator_bernstein],
        "endpoint_b0": str(sp.factor(schur_coefficient.subs(b, 0))),
        "endpoint_b1": str(sp.factor(sp.limit(schur_coefficient, b, 1, dir="-"))),
        "checks": {
            "24_order_exact_average": True,
            "kernel_vector_exact": True,
            "full_schur_coefficient": True,
            "gap_numerator_bernstein_positive": True,
            "gap_denominator_bernstein_positive": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("evidence=", args.output)


if __name__ == "__main__":
    main()
