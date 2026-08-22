"""Exact hostile control of the all-fixed-k transverse moment formula."""

from __future__ import annotations

import itertools
import json
import math
import random
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def enumerate_prefix(k: int, eta: Fraction, z: tuple[int, ...]) -> Fraction:
    total = Fraction(0)
    for size in range(1, k + 1):
        subtotal = Fraction(0)
        for order in itertools.permutations(range(k), size):
            cumulative = Fraction(0)
            energy = Fraction(0)
            for index in order:
                solved = Fraction(z[index]) - eta * cumulative
                energy += solved * solved
                cumulative += solved
            subtotal += energy
        total += subtotal / math.factorial(size)
    norm = sum(value * value for value in z)
    return total / (2 ** k * norm)


def moment_formula(k: int, eta: Fraction) -> Fraction:
    rho = 1 - eta
    total = Fraction(0)
    for j in range(1, k + 1):
        p_j = Fraction(sum(math.comb(k, s) for s in range(j, k + 1)), 2 ** k)
        weights = [rho ** r for r in range(j - 1)]
        W = sum(weights, Fraction(0))
        Q = sum((value * value for value in weights), Fraction(0))
        total += p_j * (
            Fraction(1, k)
            + eta * eta * (k * Q - W * W) / (k * (k - 1))
            + 2 * eta * W / (k * (k - 1))
        )
    return total


def main() -> None:
    seed = 202608226
    rng = random.Random(seed)
    records = []
    for k in range(3, 7):
        for case in range(3):
            prefix = [rng.randint(-5, 5) for _ in range(k - 1)]
            z = tuple(prefix + [-sum(prefix)])
            if not any(z):
                z = (1, -1) + (0,) * (k - 2)
            eta = Fraction(rng.randint(1, 8), rng.randint(9, 17))
            explicit = enumerate_prefix(k, eta, z)
            formula = moment_formula(k, eta)
            records.append({
                "k": k, "case": case, "z": list(z), "eta": str(eta),
                "explicit": str(explicit), "formula": str(formula),
                "difference": str(explicit - formula),
            })
    result = {
        "evidence_level": "E2 exact Fraction hostile control",
        "seed": seed,
        "records": records,
        "all_exact_zero": all(row["difference"] == "0" for row in records),
    }
    (HERE / "fixed_k_random_z_audit.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
