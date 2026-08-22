"""Exact finite reconstruction of the equicorrelation half-prefix theorem.

The analytic proof is in ``docs/ITER5_EQUICORRELATION_HALF_PREFIX.md``.  This
script uses only ``fractions.Fraction`` and all permutations through n=6 to
check the triangular-solve orientation, the two invariant eigenvalues, and the
closed recurrences.  It is a finite verifier, not the quantified proof.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path


def prefix_solve(order: tuple[int, ...], rho: F, right: list[F], steps: int) -> list[F]:
    values = [F(0) for _ in order]
    accumulated = F(0)
    for position, coordinate in enumerate(order[:steps]):
        values[position] = right[coordinate] - rho * accumulated
        accumulated += values[position]
    return values[:steps]


def brute_eigenvalues(n: int, steps: int, rho: F) -> tuple[F, F]:
    parallel = [F(1) for _ in range(n)]
    transverse = [F(1), F(-1)] + [F(0) for _ in range(n - 2)]
    parallel_energy = F(0)
    transverse_energy = F(0)
    orders = list(itertools.permutations(range(n)))
    for order in orders:
        parallel_energy += sum(x * x for x in prefix_solve(order, rho, parallel, steps))
        transverse_energy += sum(x * x for x in prefix_solve(order, rho, transverse, steps))
    parallel_eigenvalue = parallel_energy / (len(orders) * n)
    transverse_eigenvalue = transverse_energy / (len(orders) * 2)
    return transverse_eigenvalue, parallel_eigenvalue


def recurrence_eigenvalues(n: int, steps: int, rho: F) -> tuple[F, F]:
    transverse = F(0)
    parallel = F(0)
    for size in range(n - steps + 1, n + 1):
        parent_parallel = F(1, size) + F(size - 1, size) * (1 - rho) ** 2 * parallel
        parent_lambda = 1 + (size - 1) * rho
        parent_transverse = (
            F(1, size)
            + F(size - 2, size - 1) * transverse
            + parent_lambda**2 * parallel / F(size * (size - 1))
        )
        transverse, parallel = parent_transverse, parent_parallel
    return transverse, parallel


def target_margins(n: int, steps: int, rho: F, transverse: F, parallel: F):
    transverse_lambda = 1 - rho
    parallel_lambda = 1 + (n - 1) * rho
    mu = min(transverse_lambda, parallel_lambda)
    target = F(steps, n) * mu
    return {
        "transverse": transverse_lambda * transverse - target,
        "parallel": parallel_lambda * parallel - target,
    }


def exact_record(max_n: int = 6) -> dict[str, object]:
    records: list[dict[str, object]] = []
    for n in range(2, max_n + 1):
        steps = (n + 1) // 2
        correlations = [F(1, 3), F(-1, 2 * (n - 1))]
        for rho in correlations:
            brute = brute_eigenvalues(n, steps, rho)
            recurrence = recurrence_eigenvalues(n, steps, rho)
            assert brute == recurrence
            margins = target_margins(n, steps, rho, *brute)
            assert margins["transverse"] >= 0
            assert margins["parallel"] >= 0
            records.append(
                {
                    "n": n,
                    "steps": steps,
                    "rho": str(rho),
                    "transverse_prefix_eigenvalue": str(brute[0]),
                    "parallel_prefix_eigenvalue": str(brute[1]),
                    "transverse_target_margin": str(margins["transverse"]),
                    "parallel_target_margin": str(margins["parallel"]),
                    "permutations_enumerated": math.factorial(n),
                }
            )
    return {
        "schema_version": "1.0",
        "status": "E3 exact finite orientation and recurrence reconstruction; quantified proof is in the document",
        "max_n": max_n,
        "records": records,
        "checks": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER5_EQUICORRELATION_HALF_PREFIX_EXACT.json"),
    )
    args = parser.parse_args()
    record = exact_record(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": record["checks"]}, indent=2))


if __name__ == "__main__":
    main()
