"""Exact audit of the duplicate-direction child lemma and its size-five failure.

The child lemma is

    ((I+B)e_i)^T K0(B) ((I+B)e_i) >= 3.

This checker reconstructs the m=2 formula and the m=3 completion-of-the-
square/Bernstein certificate used for the n=4 duplicate-nullity-one family.
It also certifies a rational m=5 counterexample to the general child lemma.
"""

from __future__ import annotations

import argparse
import json
from itertools import permutations
from pathlib import Path

import sympy as sp


def expected_inverse_gram(correlation: sp.Matrix) -> sp.Matrix:
    n = correlation.rows
    result = sp.zeros(n)
    for order in permutations(range(n)):
        permutation = sp.eye(n)[:, list(order)]
        permuted = permutation.T * correlation * permutation
        lower = sp.Matrix(
            n,
            n,
            lambda row, column: permuted[row, column] if row >= column else 0,
        )
        factor = permutation * lower * permutation.T
        inverse = factor.inv()
        result += inverse.T * inverse / sp.factorial(n)
    return sp.simplify(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T080_DUPLICATE_CHILD_M3_AUDIT_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    r = sp.symbols("r", real=True)
    b2 = sp.Matrix([[1, r], [r, 1]])
    z2 = (sp.eye(2) + b2)[:, 0]
    d2 = sp.factor((z2.T * expected_inverse_gram(b2) * z2)[0])
    assert sp.factor(d2 - (4 - r**2 + r**4 / 2)) == 0
    # 4-r^2+r^4/2 - 7/2 = (1-r^2)^2/2 on |r|<=1.
    assert sp.factor(d2 - sp.Rational(7, 2) - (1 - r**2) ** 2 / 2) == 0

    a, b, c = sp.symbols("a b c", real=True)
    x, y = sp.symbols("x y", nonnegative=True)
    b3 = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])
    z3 = (sp.eye(3) + b3)[:, 0]
    d3 = sp.factor((z3.T * expected_inverse_gram(b3) * z3)[0])
    n_poly = sp.expand(6 * (d3 - 3))
    n_as_c = sp.Poly(n_poly, c)
    leading = sp.factor(n_as_c.coeff_monomial(c**2))
    claimed_leading = 2 * a**2 * b**2 + 3 * a**2 + 3 * b**2
    assert sp.factor(leading - claimed_leading) == 0
    linear = n_as_c.coeff_monomial(c)
    constant = n_as_c.coeff_monomial(1)
    minimum_n = sp.factor(constant - linear**2 / (4 * leading))
    p_xy = (
        2 * x**3 * y**2
        + 9 * x**3
        + 2 * x**2 * y**3
        - 12 * x**2 * y**2
        + 9 * x**2 * y
        - 18 * x**2
        + 9 * x * y**2
        - 28 * x * y
        + 18 * x
        + 9 * y**3
        - 18 * y**2
        + 18 * y
    )
    denominator_xy = 2 * x * y + 3 * x + 3 * y
    assert sp.factor(
        minimum_n - p_xy.subs({x: a**2, y: b**2}) / denominator_xy.subs({x: a**2, y: b**2})
    ) == 0

    bernstein = [
        [sp.Integer(0), sp.Integer(6), sp.Integer(6), sp.Integer(9)],
        [sp.Integer(6), sp.Rational(80, 9), sp.Rational(61, 9), sp.Rational(26, 3)],
        [sp.Integer(6), sp.Rational(61, 9), sp.Rational(20, 9), sp.Integer(2)],
        [sp.Integer(9), sp.Rational(26, 3), sp.Integer(2), sp.Integer(0)],
    ]
    reconstructed = sum(
        bernstein[i][j]
        * sp.binomial(3, i)
        * x**i
        * (1 - x) ** (3 - i)
        * sp.binomial(3, j)
        * y**j
        * (1 - y) ** (3 - j)
        for i in range(4)
        for j in range(4)
    )
    assert sp.expand(p_xy - reconstructed) == 0
    assert all(value >= 0 for row in bernstein for value in row)
    assert sp.factor(n_poly.subs({a: 0, b: 0}) - 6) == 0

    # Exact m=5 obstruction: two repeated poles and a latitude-4/5 triangle.
    b5 = sp.eye(5)
    b5[0, 1] = b5[1, 0] = 1
    for pole in [0, 1]:
        for ring in [2, 3, 4]:
            b5[pole, ring] = b5[ring, pole] = sp.Rational(4, 5)
    for left, right in [(2, 3), (2, 4), (3, 4)]:
        b5[left, right] = b5[right, left] = sp.Rational(23, 50)
    z5 = (sp.eye(5) + b5)[:, 0]
    d5 = sp.factor((z5.T * expected_inverse_gram(b5) * z5)[0])
    claimed_d5 = sp.Rational(7204453277, 2441406250)
    assert d5 == claimed_d5
    assert sp.factor(d5 - 3) == -sp.Rational(119765473, 2441406250)
    characteristic = sp.factor(b5.charpoly().as_expr())

    payload = {
        "status": (
            "E2 exact artifact: the child lemma holds through m=3 but is refuted in general by "
            "an exact m=5 correlation matrix"
        ),
        "m2_formula": str(d2),
        "m3_quadratic_leading_coefficient": str(leading),
        "m3_completion_square_numerator": str(p_xy),
        "bernstein_coefficients": [[str(value) for value in row] for row in bernstein],
        "checks": {
            "m2_identity_and_bound": True,
            "m3_six_order_reconstruction": True,
            "m3_completion_of_square": True,
            "bicubic_bernstein_reconstruction": True,
            "bicubic_bernstein_nonnegative": True,
            "a_equals_b_equals_zero_case": True,
            "m5_counterexample_exact": True,
        },
        "m5_counterexample": {
            "matrix": [[str(b5[i, j]) for j in range(5)] for i in range(5)],
            "z": [str(value) for value in z5],
            "characteristic_polynomial": str(characteristic),
            "quadratic_value": str(d5),
            "gap_to_3": str(sp.factor(d5 - 3)),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "passed"}))


if __name__ == "__main__":
    main()
