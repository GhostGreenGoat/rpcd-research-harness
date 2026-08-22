"""Exact checks for the two-pole plus k-simplex T080 counterexample family.

The proof-draft consequence is asymptotic: for fixed rational 0<a<1, the
kernel Rayleigh coefficient converges to 1+1/(2-a^2).  Sending a down to zero
after k tends to infinity shows that no dimension-uniform inequality of the
form K0(C) >= c P_ker(C) can hold with c>3/2.

This script checks the finite word formula against a structurally independent
state recurrence using Fraction arithmetic.  The limit itself is justified in
the accompanying document by an explicit O(1/k) boundary-composition bound.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def word_energy_recurrence(k: int, a: Fraction, before: int, middle: int, after: int) -> Fraction:
    """Direct state recurrence for a positive-first category word."""
    assert before + middle + after == k
    rho = (k * a * a - 1) / (k - 1)
    symbols = ["R"] * before + ["+"] + ["R"] * middle + ["-"] + ["R"] * after
    pole_sum = Fraction(0)
    ring_sum = Fraction(0)
    energy = Fraction(0)
    for symbol in symbols:
        if symbol == "+":
            value = 1 - pole_sum - a * ring_sum
            pole_sum += value
        elif symbol == "-":
            value = -1 - pole_sum - a * ring_sum
            pole_sum += value
        else:
            value = -a * pole_sum - rho * ring_sum
            ring_sum += value
        energy += value * value
    return energy


def word_energy_formula(k: int, a: Fraction, middle: int, after: int) -> Fraction:
    """Closed geometric-run formula; requires nonzero rho."""
    rho = (k * a * a - 1) / (k - 1)
    assert rho != 0
    q = 1 - rho
    denominator = 1 - q * q
    q_middle = q**middle
    return (
        1
        + a * a * (1 - q ** (2 * middle)) / denominator
        + (-2 + a * a * (1 - q_middle) / rho) ** 2
        + a
        * a
        / denominator
        * (2 - q_middle - a * a * (1 - q_middle) / rho) ** 2
        * (1 - q ** (2 * after))
    )


def exact_lambda(k: int, a: Fraction) -> Fraction:
    """Average over the 2*C(k+2,2) pole/ring category words, divided by ||u||^2."""
    total = Fraction(0)
    compositions = 0
    for middle in range(k + 1):
        for after in range(k - middle + 1):
            before = k - middle - after
            direct = word_energy_recurrence(k, a, before, middle, after)
            closed = word_energy_formula(k, a, middle, after)
            assert direct == closed
            total += closed
            compositions += 1
    assert compositions == (k + 1) * (k + 2) // 2
    # The negative-first words have identical energy.  Averaging both
    # orientations and dividing by ||e_1-e_2||^2=2 leaves total/(2*C).
    return total / (2 * compositions)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T080_POLE_SIMPLEX_ASYMPTOTIC_2026_08_21.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = exact_lambda(6, Fraction(2, 3))
    assert base == Fraction(1057837, 531441)

    finite_checks = []
    for k, a in [
        (3, Fraction(1, 2)),
        (4, Fraction(2, 3)),
        (6, Fraction(2, 3)),
        (10, Fraction(1, 2)),
        (20, Fraction(1, 3)),
    ]:
        # Avoid the removable rho=0 representation in this checker.
        if k * a * a == 1:
            continue
        value = exact_lambda(k, a)
        rho = (k * a * a - 1) / (k - 1)
        finite_checks.append(
            {
                "k": k,
                "n": k + 2,
                "a": str(a),
                "rho": str(rho),
                "lambda": str(value),
                "lambda_decimal": float(value),
            }
        )

    limits = []
    for a in [Fraction(2, 3), Fraction(1, 2), Fraction(1, 3), Fraction(1, 5), Fraction(1, 10)]:
        limit = 1 + 1 / (2 - a * a)
        assert limit > Fraction(3, 2)
        limits.append(
            {
                "a": str(a),
                "fixed_a_k_to_infinity_limit": str(limit),
                "decimal": float(limit),
                "gap_above_three_halves": str(limit - Fraction(3, 2)),
            }
        )
    assert limits[-1]["fixed_a_k_to_infinity_limit"] == "299/199"

    payload = {
        "status": "exact finite checks supporting an E3 asymptotic proof draft",
        "family": {
            "coordinates": "two identical poles plus k regular-simplex ring points",
            "pole_ring": "a",
            "ring_off_diagonal": "(k*a^2-1)/(k-1)",
            "spectrum": "0 mult 2; k(1-a^2)/(k-1) mult k-1; 2+k*a^2 mult 1",
        },
        "base_n8_coefficient": str(base),
        "finite_formula_vs_recurrence_checks": finite_checks,
        "fixed_a_limits": limits,
        "iterated_limit": "lim_(a down to 0) lim_(k to infinity) lambda_(k,a) = 3/2",
        "quantifier_consequence": (
            "For every c>3/2, choose positive rational a with "
            "1+1/(2-a^2)<c, then sufficiently large k; hence no universal c>3/2."
        ),
        "scope_warning": (
            "This is only an upper bound on the best possible universal kernel constant; "
            "it does not prove a 3/2 lower bound or refute the original RPCD complexity conjecture."
        ),
        "arithmetic": "Python fractions.Fraction; no floating-point decisions",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "base_n8": str(base),
                "smallest_displayed_limit": limits[-1]["fixed_a_k_to_infinity_limit"],
                "checks": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
