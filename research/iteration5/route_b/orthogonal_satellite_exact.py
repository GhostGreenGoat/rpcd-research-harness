"""Exact finite formulas for the tight orthogonal two-satellite direction."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


def probabilities(n: int) -> tuple[Fraction, Fraction, Fraction]:
    r = (n + 1) // 2
    p2 = Fraction(r * (r - 1), n * (n - 1))
    p0 = Fraction((n - r) * (n - r - 1), n * (n - 1))
    p1 = 1 - p0 - p2
    return p0, p1, p2


def prefix_ratio(n: int, mu: Fraction) -> Fraction:
    _, p1, p2 = probabilities(n)
    a = 2 - mu
    expected_energy = p1 + p2 * (1 + a * a)
    return expected_energy / 2


def closed_ratio(n: int, mu: Fraction) -> Fraction:
    a = 2 - mu
    if n % 2 == 0:
        h = n // 2
        return Fraction(1, 2) + Fraction(h - 1, 4 * (2 * h - 1)) * (a * a - 1)
    h = (n - 1) // 2
    return Fraction((h + 1), 4 * (2 * h + 1)) * (3 + a * a)


def main() -> None:
    instances = []
    for n in (5, 6, 9, 10, 100, 1000):
        for mu in (Fraction(1, 5), Fraction(4, 5), Fraction(49, 50)):
            direct = prefix_ratio(n, mu)
            closed = closed_ratio(n, mu)
            assert direct == closed
            assert direct >= Fraction(1, 2)
            instances.append(
                {
                    "n": n,
                    "mu": str(mu),
                    "J_ratio": str(direct),
                    "margin_over_half": str(direct - Fraction(1, 2)),
                    "probabilities": [str(value) for value in probabilities(n)],
                }
            )
    result = {
        "evidence_level": "E2 exact rational finite checks supporting an E3 all-n proof draft",
        "statement": "For the orthogonal two-satellite family, on the satellite-difference direction, J_ceil(n/2)/mu >= 1/2 and hence H_ceil(n/2)/mu >= 1/2.",
        "even_formula": "1/2 + (h-1)((2-mu)^2-1)/(4(2h-1)), n=2h",
        "odd_formula": "(h+1)(3+(2-mu)^2)/(4(2h+1)), n=2h+1",
        "instances": instances,
    }
    output = Path(__file__).with_name("orthogonal_satellite_exact.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
