"""Finite checks of the exact fixed-two-satellite limit formula."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np

from reproducer import evaluate_family


def exact_limit(mu: Fraction, t_squared: Fraction) -> Fraction:
    alpha = 1 - mu
    eta = alpha * (1 - t_squared)
    return (8 - eta**3) / (8 * (1 + mu))


def main() -> None:
    parameter_pairs = [
        (Fraction(1, 5), Fraction(0)),
        (Fraction(4, 5), Fraction(0)),
        (Fraction(19, 20), Fraction(0)),
        (Fraction(19, 20), Fraction(1, 4)),
        (Fraction(19, 20), Fraction(1)),
    ]
    exact = []
    for mu, t_squared in parameter_pairs:
        value = exact_limit(mu, t_squared)
        assert value > Fraction(1, 2)
        exact.append(
            {
                "mu": str(mu),
                "t_squared": str(t_squared),
                "limit": str(value),
                "margin_over_half": str(value - Fraction(1, 2)),
            }
        )

    finite = []
    for mu in (0.2, 0.8, 0.95):
        limit = float(exact_limit(Fraction(str(mu)), Fraction(0)))
        for n in (100, 300, 1000, 2000):
            directions = np.array([[1.0, 0.0], [0.0, 1.0]])
            item = evaluate_family(
                "orthogonal_two_satellite",
                (n - 2, 2),
                directions,
                (1.0, 1.0),
                mu,
            )
            finite.append(
                {
                    "n": n,
                    "mu": mu,
                    "ratio": item["ratio"],
                    "exact_limit": limit,
                    "finite_minus_limit": item["ratio"] - limit,
                    "sector": item["result"]["sector"],
                    "states_evaluated": item["result"]["states_evaluated"],
                    "leaf_underflows": item["result"]["leaf_underflows"],
                }
            )
    result = {
        "evidence_level": "E2 exact rational formula evaluations plus E1 float64 finite convergence",
        "formula": "R2=(8-eta^3)/(8(1+mu)), eta=(1-mu)(1-t^2)",
        "exact": exact,
        "finite": finite,
    }
    output = Path(__file__).with_name("satellite_asymptotic_check.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
