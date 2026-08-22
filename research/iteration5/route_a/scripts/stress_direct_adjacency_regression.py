"""E1 exhaustive-order stress test for the direct adjacency regression.

This script is deliberately a falsifier.  A nonnegative search is not a
proof of the quantified Q inequality.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np


def symmetric_root(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
    return (vectors * np.sqrt(values)) @ vectors.T


def moments(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = matrix.shape[0]
    p_moment = np.zeros_like(matrix)
    q_moment = np.zeros_like(matrix)
    count = 0
    for order in itertools.permutations(range(n)):
        position = np.empty(n, dtype=int)
        for place, coordinate in enumerate(order):
            position[coordinate] = place
        triangular = np.eye(n)
        for i in range(n):
            for j in range(n):
                if position[j] < position[i]:
                    triangular[i, j] = matrix[i, j]
        difference = np.eye(n)
        for place in range(1, n):
            current, previous = order[place], order[place - 1]
            difference[current, previous] = -matrix[current, previous]
        p_moment += difference.T
        defect = difference @ triangular
        q_moment += defect @ defect.T
        count += 1
    return p_moment / count, q_moment / count


def record(matrix: np.ndarray, family: str) -> dict[str, object]:
    n = matrix.shape[0]
    eigenvalues = np.linalg.eigvalsh(matrix)
    mu = float(eigenvalues[0])
    p_moment, q_moment = moments(matrix)
    closed_p = ((n + 1) * np.eye(n) - matrix) / n
    p_residual = float(np.linalg.eigvalsh(p_moment - closed_p)[0])
    certificate = p_moment @ np.linalg.inv(q_moment) @ p_moment.T
    root = symmetric_root(matrix)
    normalized = root @ certificate @ root
    ratio = float(np.linalg.eigvalsh((normalized + normalized.T) / 2)[0] / mu)
    q_target = 2 / mu * p_moment @ matrix @ p_moment.T - q_moment
    return {
        "family": family,
        "n": n,
        "mu": mu,
        "certificate_over_mu": ratio,
        "margin_over_one_half": ratio - 0.5,
        "q_inequality_min_eigenvalue": float(np.linalg.eigvalsh(q_target)[0]),
        "p_formula_min_residual": p_residual,
    }


def run(seed: int, samples: int, n_max: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []
    started = time.time()
    for n in range(3, n_max + 1):
        for mu in (0.01, 0.5, 0.9, 0.99):
            matrix = mu * np.eye(n) + (1 - mu) * np.ones((n, n))
            records.append(record(matrix, f"positive_equicorrelation_mu_{mu}"))
        for sample in range(samples):
            rank = int(rng.integers(1, n))
            vectors = rng.normal(size=(n, rank))
            vectors /= np.linalg.norm(vectors, axis=1)[:, None]
            requested_mu = float(10 ** rng.uniform(-4, -0.001))
            matrix = (
                requested_mu * np.eye(n)
                + (1 - requested_mu) * vectors @ vectors.T
            )
            records.append(record(matrix, f"random_rank_{rank}_sample_{sample}"))
    return {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 exhaustive-order null search",
        "seed": seed,
        "samples_per_dimension": samples,
        "n_max": n_max,
        "elapsed_seconds": time.time() - started,
        "evaluations": len(records),
        "minimum_certificate_over_mu": min(
            item["certificate_over_mu"] for item in records
        ),
        "minimum_q_margin": min(
            item["q_inequality_min_eigenvalue"] for item in records
        ),
        "warning": "No violation is not a proof of the Q inequality.",
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026082151)
    parser.add_argument("--samples", type=int, default=30)
    parser.add_argument("--n-max", type=int, default=7)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_a/evidence/direct_adjacency_stress.json"
        ),
    )
    args = parser.parse_args()
    result = run(args.seed, args.samples, args.n_max)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "minimum_certificate_over_mu": result[
                    "minimum_certificate_over_mu"
                ],
                "minimum_q_margin": result["minimum_q_margin"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
