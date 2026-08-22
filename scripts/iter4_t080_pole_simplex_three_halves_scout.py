"""Certified finite scout for a possible 3/2 pole-simplex lower bound.

For each 2 <= k <= 15, this script symbolically averages the exact category
word formula, cancels the removable rho=0 singularity, and proves

    lambda_(k,a) > 3/2  for every 0 <= a^2 <= 1

by positivity of every coefficient in the degree-2k Bernstein expansion.
This is a finite family certificate, not an all-k proof.

It also records an exact obstruction to the tempting proof that each cyclic
orbit of the three composition gaps has average word energy at least 3.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


def symbolic_lambda(k: int, b: sp.Symbol) -> sp.Expr:
    """Return lambda_(k,a) as a polynomial in b=a^2."""
    rho = (k * b - 1) / (k - 1)
    q = 1 - rho
    denominator = 1 - q**2
    total = 0
    for middle in range(k + 1):
        q_middle = q**middle
        for after in range(k - middle + 1):
            total += (
                1
                + b * (1 - q ** (2 * middle)) / denominator
                + (-2 + b * (1 - q_middle) / rho) ** 2
                + b
                / denominator
                * (2 - q_middle - b * (1 - q_middle) / rho) ** 2
                * (1 - q ** (2 * after))
            )
    return sp.cancel(total / (2 * sp.binomial(k + 2, 2)))


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol, degree: int) -> list[sp.Expr]:
    """Convert monomial coefficients to fixed-degree Bernstein coefficients."""
    poly = sp.Poly(sp.expand(polynomial), variable)
    monomial = [poly.coeff_monomial(variable**power) for power in range(degree + 1)]
    return [
        sp.factor(
            sum(
                monomial[power]
                * sp.binomial(index, power)
                / sp.binomial(degree, power)
                for power in range(index + 1)
            )
        )
        for index in range(degree + 1)
    ]


def rational_word_energy(k: int, b: Fraction, middle: int, after: int) -> Fraction:
    rho = (k * b - 1) / (k - 1)
    q = 1 - rho
    denominator = 1 - q * q
    q_middle = q**middle
    return (
        1
        + b * (1 - q ** (2 * middle)) / denominator
        + (-2 + b * (1 - q_middle) / rho) ** 2
        + b
        / denominator
        * (2 - q_middle - b * (1 - q_middle) / rho) ** 2
        * (1 - q ** (2 * after))
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T080_POLE_SIMPLEX_THREE_HALVES_SCOUT_2026_08_21.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    b = sp.symbols("b", real=True)
    certificates = []
    lambda_by_k: dict[int, sp.Expr] = {}
    for k in range(2, 16):
        lam = symbolic_lambda(k, b)
        lambda_by_k[k] = lam
        gap = sp.cancel(lam - sp.Rational(3, 2))
        numerator, denominator = sp.fraction(gap)
        assert denominator.is_number and denominator > 0
        assert sp.degree(numerator, b) <= 2 * k
        coefficients = bernstein_coefficients(numerator, b, 2 * k)
        assert all(coefficient > 0 for coefficient in coefficients)
        normalized = [sp.factor(coefficient / denominator) for coefficient in coefficients]
        certificates.append(
            {
                "k": k,
                "n": k + 2,
                "degree": 2 * k,
                "positive_bernstein_coefficients_normalized": [
                    str(coefficient) for coefficient in normalized
                ],
                "minimum_coefficient_decimal": str(min(sp.N(value, 18) for value in normalized)),
                "gap_at_b_zero": str(sp.factor(gap.subs(b, 0))),
                "gap_at_b_one": str(sp.factor(gap.subs(b, 1))),
            }
        )

    stronger_fixed_k = []
    for k in range(2, 16):
        # R_k>=0 is equivalent to lambda_k>=1+1/(2-b).
        remainder = sp.cancel((2 - b) * (lambda_by_k[k] - 1) - 1)
        numerator, denominator = sp.fraction(remainder)
        assert denominator.is_number and denominator > 0
        coefficients = bernstein_coefficients(numerator, b, 2 * k + 1)
        normalized = [sp.factor(value / denominator) for value in coefficients]
        assert all(value > 0 for value in normalized)
        assert all(normalized[index] >= normalized[index + 1] for index in range(2 * k + 1))
        assert normalized[-1] == sp.Rational(1, k + 2)
        stronger_fixed_k.append(
            {
                "k": k,
                "bernstein_degree": 2 * k + 1,
                "all_coefficients_strictly_positive": True,
                "coefficients_monotonically_nonincreasing": True,
                "last_coefficient": str(normalized[-1]),
            }
        )

    dimension_monotonicity = []
    for k in range(2, 13):
        difference = sp.cancel(lambda_by_k[k] - lambda_by_k[k + 1])
        numerator, denominator = sp.fraction(difference)
        assert denominator.is_number and denominator > 0
        coefficients = bernstein_coefficients(numerator, b, 2 * k + 2)
        normalized = [sp.factor(value / denominator) for value in coefficients]
        assert normalized[0] == 0
        assert all(value > 0 for value in normalized[1:])
        assert normalized[-1] == sp.Rational(1, (k + 2) * (k + 3))
        dimension_monotonicity.append(
            {
                "k_to_k_plus_one": k,
                "bernstein_degree": 2 * k + 2,
                "coefficient_at_b_zero": "0",
                "all_other_coefficients_strictly_positive": True,
                "coefficient_at_b_one": str(normalized[-1]),
            }
        )

    # A natural local grouping is false: cyclically rotate the three gap
    # counts (before,middle,after)=(17,17,18).  With a=2/5 (b=4/25), the
    # average of the three word energies is strictly below 3.
    k = 52
    b_value = Fraction(4, 25)
    gaps = (17, 17, 18)
    cyclic_energies = [
        rational_word_energy(k, b_value, gaps[1], gaps[2]),
        rational_word_energy(k, b_value, gaps[2], gaps[0]),
        rational_word_energy(k, b_value, gaps[0], gaps[1]),
    ]
    cyclic_average = sum(cyclic_energies, Fraction(0)) / 3
    cyclic_gap = cyclic_average - 3
    assert cyclic_gap < 0

    payload = {
        "status": "E2 exact finite Bernstein scout; no all-k theorem",
        "statement_certified_finitely": (
            "For the pole-simplex family and every 2<=k<=15, "
            "lambda_(k,a)>3/2 for all 0<=a^2<=1."
        ),
        "certificates": certificates,
        "stronger_fixed_k_certificates": {
            "statement": "lambda_(k,a)>=1+1/(2-a^2) for every 2<=k<=15 and 0<=a^2<=1",
            "records": stronger_fixed_k,
        },
        "finite_dimension_monotonicity_certificates": {
            "statement": "lambda_(k,a)>=lambda_(k+1,a) for every 2<=k<=12 and 0<=a^2<=1",
            "records": dimension_monotonicity,
        },
        "failed_proof_route": {
            "claim_refuted": "every cyclic orbit of composition gaps has average word energy >=3",
            "k": k,
            "a": "2/5",
            "b_equals_a_squared": str(b_value),
            "gaps_before_middle_after": list(gaps),
            "cyclic_average_energy": str(cyclic_average),
            "gap_to_three": str(cyclic_gap),
            "gap_to_three_decimal": float(cyclic_gap),
        },
        "scope_warning": (
            "Positive Bernstein coefficients through k=15 do not prove the conjectured "
            "3/2 lower bound for arbitrary k or arbitrary correlation matrices."
        ),
        "arithmetic": "SymPy exact rationals and Python Fraction; no floating-point decisions",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "k_range": [2, 15],
                "all_bernstein_coefficients_positive": True,
                "cyclic_grouping_gap": str(cyclic_gap),
                "checks": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
