"""Two-scalar determinant-tail recurrence on the signed rank-one family.

Outputs floating diagnostics only.  The recurrence itself follows exactly from
exchangeability; finite-precision minimization over mu is E1 evidence.
"""

from __future__ import annotations

import argparse
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np


def lift_coefficients(size: int, mu: float, child_transverse: float, child_parallel: float):
    off = 1.0 - mu
    parallel_eigenvalue = size - (size - 1) * mu
    total_weight = (
        size - 1 + 2.0 * off + (size - 1) * off * off
    ) / size
    parallel_weight = parallel_eigenvalue**2 / (size * (size - 1))
    transverse = (
        1.0 / size
        + (total_weight - parallel_weight) * child_transverse
        + parallel_weight * child_parallel
    )
    parallel = (
        1.0 / size
        + (size - 1) * mu * mu * child_parallel / size
    )
    return transverse, parallel


def determinant_tail_coefficient(size: int, depth: int, mu: float) -> float:
    @lru_cache(maxsize=None)
    def recurse(local_size: int, local_depth: int):
        if local_size == 1:
            return 1.0, 1.0
        parallel_eigenvalue = local_size - (local_size - 1) * mu
        if local_depth == 0:
            # det(B)B^{-1}: ordinary eigenvalues on 1^perp and span(1).
            return (
                mu ** (local_size - 2) * parallel_eigenvalue,
                mu ** (local_size - 1),
            )
        return lift_coefficients(
            local_size, mu, *recurse(local_size - 1, local_depth - 1)
        )

    transverse, parallel = recurse(size, depth)
    parallel_eigenvalue = size - (size - 1) * mu
    return min(mu * transverse, parallel_eigenvalue * parallel)


def scan_dimension(size: int, grid_size: int):
    depth = (size + 1) // 2
    grid = np.unique(
        np.concatenate(
            [
                np.geomspace(1e-12, 1e-2, max(50, grid_size // 5)),
                np.linspace(1e-2, 1.0 - 1e-8, grid_size),
                1.0 - np.geomspace(1e-8, 0.5, max(100, grid_size // 2)),
            ]
        )
    )
    ratios = np.asarray(
        [determinant_tail_coefficient(size, depth, float(mu)) / mu for mu in grid]
    )
    index = int(np.argmin(ratios))
    near_identity_mu = 1.0 - size ** (-0.5)
    return {
        "size": size,
        "depth": depth,
        "grid_minimizer_mu": float(grid[index]),
        "grid_minimum_c_over_mu": float(ratios[index]),
        "near_identity_mu_one_minus_n_to_minus_half": near_identity_mu,
        "near_identity_c_over_mu": determinant_tail_coefficient(
            size, depth, near_identity_mu
        )
        / near_identity_mu,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="6,8,10,20,50,100,200,500,1000")
    parser.add_argument("--grid-size", type=int, default=1600)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T085_RANK_ONE_HALF_DEPTH.json"),
    )
    args = parser.parse_args()
    sizes = [int(value) for value in args.sizes.split(",")]
    result = {
        "evidence_level": "E1 float64 grid minimization of an algebraically exact two-scalar recurrence",
        "grid_size": args.grid_size,
        "results": [scan_dimension(size, args.grid_size) for size in sizes],
        "warning": "The observed approach to 1/2 is not a proof of a universal lower bound.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
