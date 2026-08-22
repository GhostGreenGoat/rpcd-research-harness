"""Hostile E1 search for an exact third-prefix SOS candidate.

Candidate:

    J3(A) - J2(A)/2 >= (2*mu/m) A^{-1}.

Together with the exact J2 lower bound, this would imply
J3 >= (3*mu/m) A^{-1}.  A null search is not a proof.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


def j2(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    diagonal_square = np.diag(np.diag(matrix @ matrix))
    return (
        (2 * size - 1) * np.eye(size) - 2 * matrix + diagonal_square
    ) / (size * (size - 1))


def third_frame(matrix: np.ndarray) -> np.ndarray:
    """The exact PSD codimension-two frame T(A) in the J3 formula."""
    size = matrix.shape[0]
    square_diagonal = np.diag(matrix @ matrix)
    result = np.zeros_like(matrix)
    identity = np.eye(size)
    for first in range(size):
        for second in range(size):
            if first == second:
                continue
            weight = square_diagonal[second] - matrix[first, second] ** 2
            vector = identity[:, second] - matrix[first, second] * identity[:, first]
            result += weight * np.outer(vector, vector)
    return result


def j3_closed(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    square = matrix @ matrix
    cube = square @ matrix
    diagonal_square = np.diag(np.diag(square))
    diagonal_cube = np.diag(np.diag(cube))
    q = size * np.eye(size) - 2 * matrix + diagonal_square
    r = size * matrix - 2 * square + diagonal_cube
    value = np.eye(size) / size + (
        (2 * size - 3) * q - 2 * r + third_frame(matrix)
    ) / (size * (size - 1) * (size - 2))
    return (value + value.T) / 2


def normalized_minimum(matrix: np.ndarray, certificate: np.ndarray) -> float:
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
    root = (vectors * np.sqrt(np.maximum(values, 0.0))) @ vectors.T
    normalized = root @ certificate @ root
    return float(np.linalg.eigvalsh((normalized + normalized.T) / 2)[0])


def correlation_from_gram(raw: np.ndarray) -> np.ndarray:
    gram = raw @ raw.T
    scale = np.sqrt(np.diag(gram))
    return gram / scale[:, None] / scale[None, :]


def signed_rank_one(size: int, mu: float) -> np.ndarray:
    return mu * np.eye(size) + (1 - mu) * np.ones((size, size))


def simplex(size: int, mu: float) -> np.ndarray:
    boundary = np.full((size, size), -1 / (size - 1))
    np.fill_diagonal(boundary, 1.0)
    return mu * np.eye(size) + (1 - mu) * boundary


def candidate_margin(matrix: np.ndarray) -> tuple[float, float, float]:
    mu = float(np.linalg.eigvalsh(matrix)[0])
    certificate = j3_closed(matrix) - j2(matrix) / 2
    ratio = normalized_minimum(matrix, certificate) / mu
    target = 2 / matrix.shape[0]
    return ratio - target, ratio, mu


def run(args: argparse.Namespace) -> dict[str, object]:
    rng = np.random.default_rng(args.seed)
    started = time.time()
    by_dimension: dict[str, object] = {}
    total = 0
    for size in range(args.n_min, args.n_max + 1):
        cases: list[tuple[str, np.ndarray]] = []
        for sample in range(args.samples):
            rank = int(rng.integers(1, size + 3))
            boundary = correlation_from_gram(rng.normal(size=(size, rank)))
            eta = 10 ** rng.uniform(args.log10_mu_min, -0.0001)
            matrix = eta * np.eye(size) + (1 - eta) * boundary
            cases.append((f"random_rank_{rank}_{sample}", matrix))
        for eta in np.geomspace(10 ** args.log10_mu_min, 0.999, 40):
            cases.append((f"signed_rank_one_{eta:.12g}", signed_rank_one(size, eta)))
            cases.append((f"simplex_{eta:.12g}", simplex(size, eta)))

        best = {"margin": math.inf}
        for label, matrix in cases:
            margin, ratio, mu = candidate_margin(matrix)
            total += 1
            if margin < best["margin"]:
                best = {
                    "margin": float(margin),
                    "ratio": float(ratio),
                    "target": 2 / size,
                    "mu": float(mu),
                    "label": label,
                    "matrix": matrix.tolist(),
                }
        by_dimension[str(size)] = best
        print(json.dumps({"size": size, "best": best}), flush=True)

    return {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 hostile null search",
        "scope_warning": "A nonnegative finite search is not a proof.",
        "candidate": "J3-J2/2 >= (2mu/m) A^{-1}",
        "seed": args.seed,
        "samples_per_dimension": args.samples,
        "log10_mu_min": args.log10_mu_min,
        "dimensions": [args.n_min, args.n_max],
        "evaluations": total,
        "elapsed_seconds": time.time() - started,
        "best_by_dimension": by_dimension,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-min", type=int, default=3)
    parser.add_argument("--n-max", type=int, default=12)
    parser.add_argument("--samples", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=20260905)
    parser.add_argument("--log10-mu-min", type=float, default=-6.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_c/evidence/J3_SOS_HOSTILE_SEARCH.json"
        ),
    )
    args = parser.parse_args()
    record = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "evaluations": record["evaluations"]}))


if __name__ == "__main__":
    main()
