"""Independent exact-algebra audit of the n=3 T080 proof draft.

This checks the six-order formula, the invariant numerator reduction modulo
``det(C)=0``, both endpoint factorizations, and the Bernstein coefficients.
The accompanying audit document separately checks the feasible-set argument.
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
        default=Path("research/evidence/ITER4_T080_N3_HOSTILE_AUDIT_2026_08_21.json"),
    )
    return parser.parse_args()


def exact_k() -> tuple[sp.Matrix, tuple[sp.Symbol, sp.Symbol, sp.Symbol]]:
    a, b, c = sp.symbols("a b c", real=True)
    correlation = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])
    result = sp.zeros(3)
    for order in permutations(range(3)):
        permutation = sp.eye(3)[:, list(order)]
        permuted = permutation.T * correlation * permutation
        lower = sp.Matrix(
            3,
            3,
            lambda row, column: permuted[row, column] if row >= column else 0,
        )
        factor = permutation * lower * permutation.T
        inverse = factor.inv()
        result += inverse.T * inverse / 6
    return sp.simplify(result), (a, b, c)


def main() -> None:
    args = parse_args()
    k, (a, b, c) = exact_k()
    correlation = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])

    claimed_k11 = 1 + (a**2 + b**2) / 3 + ((a - b * c) ** 2 + (a * c - b) ** 2) / 6
    claimed_k12 = -a - a * (b**2 + c**2) / 6 + 2 * b * c / 3
    assert sp.factor(k[0, 0] - claimed_k11) == 0
    assert sp.factor(k[0, 1] - claimed_k12) == 0

    adj_c = correlation.adjugate()
    e_expression = sp.expand(
        sp.trace(adj_c) * k.det() - 2 * sp.trace(adj_c * k.adjugate())
    )
    tau = a * b * c
    q = a**2 * b**2 + a**2 * c**2 + b**2 * c**2

    def f(q_value: sp.Expr, tau_value: sp.Expr) -> sp.Expr:
        return (
            -2 * (4 - tau_value) * q_value**2
            + (
                -2 * tau_value**4
                + 5 * tau_value**3
                - tau_value**2
                + 37 * tau_value
                + 39
            )
            * q_value
            + tau_value**5
            - 19 * tau_value**4
            - 15 * tau_value**3
            - 51 * tau_value**2
            - 150 * tau_value
            + 54
        )

    determinant = sp.expand(correlation.det())
    invariant_residual = sp.expand(108 * e_expression - f(q, tau))
    # Exact identity on the singular hypersurface: the remainder after division
    # by det(C), viewed as a polynomial in c over Q(a,b), must vanish.
    coefficient_field = sp.QQ.frac_field(a, b)
    remainder = sp.rem(
        sp.Poly(invariant_residual, c, domain=coefficient_field),
        sp.Poly(determinant, c, domain=coefficient_field),
    ).as_expr()
    assert sp.factor(remainder) == 0

    t, r = sp.symbols("t r", real=True)
    unit_factor = 2 * (1 - t) * (t**2 - 2 * t + 3) * (t**3 + t**2 + 3 * t + 9)
    assert sp.factor(f(t**2 + 2 * t, t) - unit_factor) == 0

    t_equal = r * (2 * r - 1)
    q_equal = r**2 + 2 * r * (2 * r - 1) ** 2
    p7 = 32 * r**7 - 104 * r**6 + 132 * r**5 - 102 * r**4 + 115 * r**3 - 117 * r**2 + 41 * r + 9
    equal_factor = 2 * (1 - r) * (4 * r**3 + 5 * r**2 + 2 * r + 3) * p7
    assert sp.factor(f(q_equal, t_equal) - equal_factor) == 0

    bernstein = [
        sp.Integer(9),
        sp.Rational(104, 7),
        sp.Rational(106, 7),
        sp.Rational(92, 7),
        sp.Rational(323, 35),
        sp.Rational(50, 7),
        sp.Rational(38, 7),
        sp.Integer(6),
    ]
    reconstructed_p7 = sum(
        bernstein[index]
        * sp.binomial(7, index)
        * r**index
        * (1 - r) ** (7 - index)
        for index in range(8)
    )
    assert sp.expand(p7 - reconstructed_p7) == 0
    assert all(value > 0 for value in bernstein)

    payload = {
        "status": "E2 exact audit artifact; supports the separate E4 hostile-audit argument",
        "arithmetic": "sympy exact symbolic arithmetic",
        "checks": {
            "six_order_K11": True,
            "six_order_K12": True,
            "108E_minus_F_divisible_by_detC": True,
            "unit_variable_endpoint_factorization": True,
            "equal_variable_endpoint_factorization": True,
            "bernstein_reconstruction": True,
            "bernstein_coefficients_strictly_positive": True,
        },
        "bernstein_coefficients": [str(value) for value in bernstein],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "passed"}))


if __name__ == "__main__":
    main()
