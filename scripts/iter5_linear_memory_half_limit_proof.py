"""Symbolic verifier for the half-linear equicorrelation limit inequality.

For the q/n -> 1/2 local-inverse dual state, verify

    2(1+c) p(c)^2 - q(c) >= 0,  c>0.

The mathematical sign certificate is the all-order Taylor formula recorded
in ``research/iteration5/route_a/linear_memory_dual.md``.  Finite coefficient
checks below are regression controls, not a replacement for that induction.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

import sympy as sp


def coefficient_bracket(k: int) -> Fraction:
    return (
        Fraction(2**k - k * k + 6 * k - 2)
        - Fraction(k, 2 ** (k - 3))
    )


def build_record(max_coefficient: int) -> dict[str, object]:
    c = sp.symbols("c", positive=True)
    x = sp.exp(-c)
    p = (1 + (c - 1) * x) / (2 * c)
    q = (
        (1 - x) / (2 * c)
        + 3 * x / 2
        - 2 * x * (1 - sp.exp(-c / 2)) / c
        + c**2 * x**2 / 24
    )
    f = sp.factor(2 * (1 + c) * p**2 - q)
    h = sp.expand(24 * c**2 * sp.exp(2 * c) * f)
    expected_h = (
        12 * sp.exp(2 * c)
        + (-12 * c**2 + 60 * c - 24) * sp.exp(c)
        - 48 * c * sp.exp(c / 2)
        - c**4
        + 12 * c**3
        - 12 * c**2
        - 12 * c
        + 12
    )
    assert sp.simplify(h - expected_h) == 0

    low = [sp.expand(h.series(c, 0, 5).removeO()).coeff(c, k) for k in range(5)]
    assert low == [0, 0, 24, 36, 9]

    checked: list[dict[str, object]] = []
    for k in range(5, max_coefficient + 1):
        bracket = coefficient_bracket(k)
        assert 2**k >= k * k
        assert Fraction(6 * k - 2) > Fraction(k, 2 ** (k - 3))
        assert bracket > 0
        exact = sp.expand(h.series(c, 0, k + 1).removeO()).coeff(c, k)
        predicted = sp.Rational(12 * bracket.numerator, math.factorial(k) * bracket.denominator)
        assert sp.simplify(exact - predicted) == 0
        if k <= 12 or k == max_coefficient:
            checked.append(
                {
                    "degree": k,
                    "positive_bracket": str(bracket),
                    "coefficient": str(exact),
                }
            )

    return {
        "schema_version": "1.0",
        "status": "E3 symbolic reconstruction of the analytic Taylor certificate",
        "claim": "2(1+c)p(c)^2-q(c)>0 for every c>0",
        "low_coefficients": [str(value) for value in low],
        "general_coefficient": "12/k! * (2^k-k^2+6k-2-k/2^(k-3)), k>=5",
        "regression_max_degree": max_coefficient,
        "selected_coefficients": checked,
        "checks": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-coefficient", type=int, default=40)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER5_LINEAR_MEMORY_HALF_LIMIT_PROOF.json"
        ),
    )
    args = parser.parse_args()
    record = build_record(args.max_coefficient)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": record["checks"]}))


if __name__ == "__main__":
    main()
