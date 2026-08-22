"""Two-parameter scan of a hierarchical regular-simplex block family.

There are ``G`` equal exchangeable groups.  Their group-constant Gram vectors
form a regular ``G``-point simplex, while ``theta`` controls how much of each
coordinate lies in that group-constant mode.  The boundary correlation has a
one-dimensional nullspace.  Results are E1 float64 evidence only.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import evaluate_family


def simplex_directions(groups: int) -> np.ndarray:
    # Project the standard basis onto 1-perp and express the result in an
    # orthonormal basis obtained by an SVD.
    projector = np.eye(groups) - np.ones((groups, groups)) / groups
    u, _, _ = np.linalg.svd(projector)
    values = projector @ u[:, : groups - 1]
    values /= np.linalg.norm(values, axis=1)[:, None]
    return values


def scan(groups: int, group_size: int, grid: int) -> dict[str, object]:
    directions = simplex_directions(groups)
    theta_values = np.linspace(0.05, 0.995, grid)
    # Combine an ordinary grid with extra resolution near the high-floor
    # region where the global half constant is known to be sharp.
    mu_values = np.unique(
        np.concatenate(
            (
                np.linspace(0.05, 0.95, grid),
                1.0 - np.logspace(-3.0, -1.0, max(4, grid // 3)),
            )
        )
    )
    counts = (group_size,) * groups
    best = None
    started = time.time()
    evaluations = 0
    for theta in theta_values:
        masses = [float(theta)] * groups
        for mu in mu_values:
            item = evaluate_family(
                "hierarchical_simplex",
                counts,
                directions,
                masses,
                float(mu),
                {"theta": float(theta)},
            )
            evaluations += 1
            if best is None or item["ratio"] < best["ratio"]:
                best = item
    return {
        "evidence_level": "E1 float64 structured grid; a null result is not proof",
        "family": "equal exchangeable groups whose prototypes form a regular simplex",
        "groups": groups,
        "group_size": group_size,
        "grid": grid,
        "evaluations": evaluations,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", type=int, default=3)
    parser.add_argument("--group-size", type=int, default=20)
    parser.add_argument("--grid", type=int, default=14)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = scan(args.groups, args.group_size, args.grid)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best": result["best"]}, indent=2))


if __name__ == "__main__":
    main()
