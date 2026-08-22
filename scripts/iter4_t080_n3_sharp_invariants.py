"""Explore the sharp n=3 boundary constant 7/3 in exact invariants.

This is an exact symbolic generator.  Positivity is promoted only if the
endpoint analysis in the accompanying document closes.
"""

from __future__ import annotations

import argparse
import json
from itertools import permutations
from pathlib import Path

import sympy as sp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T080_N3_SHARP_7_OVER_3_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    a, b, c = sp.symbols("a b c", real=True)
    x, y, z = sp.symbols("x y z", nonnegative=True)
    q, tau, r = sp.symbols("q tau r", real=True)
    correlation = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])
    k = sp.zeros(3)
    for order in permutations(range(3)):
        permutation = sp.eye(3)[:, list(order)]
        permuted = permutation.T * correlation * permutation
        lower = sp.Matrix(3, 3, lambda i, j: permuted[i, j] if i >= j else 0)
        factor = permutation * lower * permutation.T
        inverse = factor.inv()
        k += inverse.T * inverse / 6

    adj_c = correlation.adjugate()
    # Multiplication by 324 clears the denominator introduced by alpha=7/3.
    expression = sp.expand(
        324
        * (
            sp.trace(adj_c) * k.det()
            - sp.Rational(7, 3) * sp.trace(adj_c * k.adjugate())
        )
    )
    even = sp.Integer(0)
    odd_quotient = sp.Integer(0)
    for exponents, coefficient in sp.Poly(expression, a, b, c).terms():
        parities = tuple(exponent % 2 for exponent in exponents)
        if parities == (0, 0, 0):
            even += coefficient * x ** (exponents[0] // 2) * y ** (exponents[1] // 2) * z ** (exponents[2] // 2)
        elif parities == (1, 1, 1):
            odd_quotient += (
                coefficient
                * x ** ((exponents[0] - 1) // 2)
                * y ** ((exponents[1] - 1) // 2)
                * z ** ((exponents[2] - 1) // 2)
            )
        else:
            raise AssertionError(f"unexpected parity orbit {exponents}")

    even_symmetric, even_remainder, generators = sp.symmetrize(
        sp.expand(even), [x, y, z], formal=True
    )
    odd_symmetric, odd_remainder, generators_odd = sp.symmetrize(
        sp.expand(odd_quotient), [x, y, z], formal=True
    )
    assert even_remainder == 0
    assert odd_remainder == 0
    assert generators == generators_odd
    substitutions = {
        generators[0][0]: 1 + 2 * tau,
        generators[1][0]: q,
        generators[2][0]: tau**2,
    }
    sharp = sp.factor(
        even_symmetric.subs(substitutions)
        + tau * odd_symmetric.subs(substitutions)
    )
    unit_endpoint = sp.factor(sharp.subs(q, tau**2 + 2 * tau))
    tau_equal = r * (2 * r - 1)
    q_equal = r**2 + 2 * r * (2 * r - 1) ** 2
    equal_endpoint = sp.factor(sharp.subs({tau: tau_equal, q: q_equal}))
    sharp_core = sp.factor(sharp / 3)
    claimed_unit = 6 * (1 - tau) ** 3 * (tau**3 + tau**2 + 3 * tau + 9)
    assert sp.factor(unit_endpoint - claimed_unit) == 0
    p5 = 32 * r**5 - 40 * r**4 + 20 * r**3 - 30 * r**2 + 49 * r + 3
    claimed_equal = 6 * (1 - r) ** 3 * (4 * r**3 + 5 * r**2 + 2 * r + 3) * p5
    assert sp.factor(equal_endpoint - claimed_equal) == 0
    bernstein = [
        sp.Integer(3),
        sp.Rational(64, 5),
        sp.Rational(98, 5),
        sp.Rational(127, 5),
        sp.Rational(121, 5),
        sp.Integer(34),
    ]
    reconstructed_p5 = sum(
        bernstein[index]
        * sp.binomial(5, index)
        * r**index
        * (1 - r) ** (5 - index)
        for index in range(6)
    )
    assert sp.expand(p5 - reconstructed_p5) == 0
    assert all(value > 0 for value in bernstein)
    print("scale=324*E_(7/3)")
    print("sharp_invariant=")
    print(sharp)
    print("degree_in_q=", sp.degree(sharp, q))
    print("q_leading_coefficient=", sp.factor(sp.Poly(sharp, q).LC()))
    print("unit_endpoint=")
    print(unit_endpoint)
    print("equal_endpoint=")
    print(equal_endpoint)
    payload = {
        "status": "E2 exact symbolic artifact supporting an E3 sharp n=3 proof draft",
        "target_constant": "7/3",
        "scale": "sharp invariant = 324 * full-Schur rank-one-downdate numerator",
        "sharp_core": str(sharp_core),
        "q_degree": int(sp.degree(sharp, q)),
        "q_leading_coefficient": str(sp.factor(sp.Poly(sharp, q).LC())),
        "unit_endpoint": str(unit_endpoint),
        "equal_variable_endpoint": str(equal_endpoint),
        "p5_bernstein_coefficients": [str(value) for value in bernstein],
        "checks": {
            "parity_reduction_exact": True,
            "symmetric_remainders_zero": True,
            "unit_endpoint_factorization": True,
            "equal_endpoint_factorization": True,
            "p5_bernstein_reconstruction": True,
            "p5_bernstein_coefficients_positive": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("evidence=", args.output)


if __name__ == "__main__":
    main()
