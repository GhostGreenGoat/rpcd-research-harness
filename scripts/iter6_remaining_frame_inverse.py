"""Targeted diagnostic for the remaining-frame inverse potential.

The candidate is
  mean_i P_i (I + sum_{j != i} Q_j)^(-1) P_i
    <= (I + sum_j Q_j)^(-1),
where Q_i are orthogonal projections and P_i=I-Q_i.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def random_projection(dimension: int, rank: int, rng: np.random.Generator) -> np.ndarray:
    basis, _ = np.linalg.qr(rng.normal(size=(dimension, rank)))
    return basis @ basis.T


def gap(projections: list[np.ndarray]) -> np.ndarray:
    dimension = projections[0].shape[0]
    identity = np.eye(dimension)
    frame = sum(projections, np.zeros_like(identity))
    rhs = np.linalg.inv(identity + frame)
    lhs = np.zeros_like(identity)
    for projection in projections:
        complement = identity - projection
        child = np.linalg.inv(identity + frame - projection)
        lhs += complement @ child @ complement / len(projections)
    return (rhs - lhs + (rhs - lhs).T) / 2


def parallel_sum_anticommutator_gaps(projections: list[np.ndarray]) -> list[np.ndarray]:
    """Return P:F - (P phi(F)+phi(F)P)/2 for every complement P."""
    dimension = projections[0].shape[0]
    identity = np.eye(dimension)
    frame = sum(projections, np.zeros_like(identity))
    phi = frame @ np.linalg.inv(identity + frame)
    answers = []
    for projection in projections:
        complement = identity - projection
        parallel = complement - complement @ np.linalg.inv(frame + complement) @ complement
        candidate = parallel - (complement @ phi + phi @ complement) / 2
        answers.append((candidate + candidate.T) / 2)
    return answers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=606101)
    parser.add_argument("--samples", type=int, default=240)
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)
    worst = {"min_eigenvalue": float("inf")}
    worst_parallel = {"min_eigenvalue": float("inf")}
    violations = 0
    evaluated = 0
    for count in range(2, 7):
        for dimension in range(2, 9):
            for _ in range(args.samples):
                ranks = rng.integers(1, dimension, size=count)
                projections = [
                    random_projection(dimension, int(rank), rng) for rank in ranks
                ]
                minimum = float(np.linalg.eigvalsh(gap(projections))[0])
                parallel_minimum = min(
                    float(np.linalg.eigvalsh(item)[0])
                    for item in parallel_sum_anticommutator_gaps(projections)
                )
                evaluated += 1
                if minimum < worst["min_eigenvalue"]:
                    worst = {
                        "min_eigenvalue": minimum,
                        "count": count,
                        "dimension": dimension,
                        "ranks": [int(rank) for rank in ranks],
                        "projections": [matrix.tolist() for matrix in projections],
                    }
                violations += minimum < -1e-9
                if parallel_minimum < worst_parallel["min_eigenvalue"]:
                    worst_parallel = {
                        "min_eigenvalue": parallel_minimum,
                        "count": count,
                        "dimension": dimension,
                        "ranks": [int(rank) for rank in ranks],
                    }
    result = {
        "kind": "targeted falsification diagnostic",
        "candidate": "mean P_i(I+sum_{j!=i}Q_j)^-1P_i <= (I+sum_jQ_j)^-1",
        "seed": args.seed,
        "evaluated": evaluated,
        "violations": violations,
        "worst": worst,
        "parallel_sum_anticommutator_worst": worst_parallel,
        "scope": "Float64 diagnostic for arbitrary projections; any negative margin must be exactified before refutation.",
    }
    path = Path("research/iteration6/root/evidence/REMAINING_FRAME_INVERSE_SCOUT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "worst"}, indent=2))
    print(json.dumps({"worst_summary": {key: value for key, value in worst.items() if key != "projections"}}, indent=2))


if __name__ == "__main__":
    main()
