"""Deterministic regression suite for the exchangeable count-state DP."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from reproducer import (
    ExchangeableTailDP,
    brute_determinant_tail,
    lift_from_reduced_gram,
    representation_to_full,
    vectors_from_directions,
)


def main() -> None:
    rng = np.random.default_rng(202608226)
    cases = []
    worst = 0.0
    for case in range(12):
        counts = [(2, 2, 2), (3, 2, 2), (2, 3, 2)][case % 3]
        directions = rng.normal(size=(3, 2))
        directions /= np.linalg.norm(directions, axis=1)[:, None]
        masses = rng.uniform(0.08, 0.96, size=3)
        vectors = vectors_from_directions(counts, directions, masses)
        mu = float(rng.uniform(0.08, 0.94))
        within, cross = lift_from_reduced_gram(counts, vectors, mu)
        depth = (sum(counts) + 1) // 2
        matrix = ExchangeableTailDP(counts, within, cross).root_matrix()
        modes = {}
        for mode in ("determinant", "zero"):
            dp = ExchangeableTailDP(counts, within, cross, mode)
            reduced = dp.coefficient(depth)
            value = representation_to_full(counts, reduced["certificate"])
            generic = brute_determinant_tail(matrix, depth, mode)
            residual = float(np.max(np.abs(value - generic)))
            worst = max(worst, residual)
            assert residual < 3e-10
            modes[mode] = {
                "max_abs_residual": residual,
                "coefficient": reduced["coefficient"],
                "sector": reduced["sector"],
            }
        cases.append({"case": case, "counts": list(counts), "mu": mu, "modes": modes})

    # Exercise the layered implementation independently of the recursive cache.
    dp = ExchangeableTailDP((48, 2), (0.05, 0.05), np.zeros((2, 2)))
    recursive = dp.bellman(dp.counts, 25)
    layered = dp.bellman_iterative(25)
    layered_residual = max(
        float(np.max(np.abs(recursive.diagonal - layered.diagonal))),
        float(np.max(np.abs(recursive.within - layered.within))),
        float(np.max(np.abs(recursive.cross - layered.cross))),
    )
    assert layered_residual == 0.0
    result = {
        "evidence_level": "E2 deterministic float64 implementation regression",
        "seed": 202608226,
        "cases": cases,
        "worst_generic_subset_residual": worst,
        "recursive_vs_layered_residual": layered_residual,
    }
    output = Path(__file__).with_name("regression_checks.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "worst": worst}, indent=2))


if __name__ == "__main__":
    main()
