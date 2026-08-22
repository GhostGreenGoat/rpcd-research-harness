"""Independent finite diagnostics for a Route-B structured candidate.

The symmetry DP is checked in two ways: full n-by-n spectral reconstruction,
and Monte Carlo evaluation of the pathwise prefix-plus-determinant-tail
quadratic form in the worst reconstructed direction.  These are float64 E1/E2
diagnostics, not certified inequalities.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, _symmetric_sqrt, representation_to_full


def load_candidate(path: Path) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return document.get("global_best", document.get("best", document))


def sample_path_value(
    matrix: np.ndarray, rhs: np.ndarray, depth: int, permutation: np.ndarray
) -> float:
    active = np.ones(matrix.shape[0], dtype=bool)
    residual = rhs.copy()
    energy = 0.0
    for pivot in permutation[:depth]:
        value = residual[pivot]
        energy += value * value
        active[pivot] = False
        remaining = np.flatnonzero(active)
        residual[remaining] -= matrix[remaining, pivot] * value
    remaining = np.flatnonzero(active)
    leaf = matrix[np.ix_(remaining, remaining)]
    sign, logdet = np.linalg.slogdet(leaf)
    if sign <= 0:
        raise ValueError("nonpositive determinant leaf")
    leaf_energy = float(residual[remaining] @ np.linalg.solve(leaf, residual[remaining]))
    return energy + math.exp(logdet) * leaf_energy


def validate(path: Path, samples: int, seed: int) -> dict[str, object]:
    candidate = load_candidate(path)
    counts = tuple(candidate["counts"])
    within = np.asarray(candidate["within"], dtype=float)
    cross = np.asarray(candidate["cross"], dtype=float)
    depth = int(candidate["depth"])
    dp = ExchangeableTailDP(counts, within, cross)
    reduced_result = dp.coefficient(depth)
    matrix = dp.root_matrix()
    certificate = representation_to_full(counts, reduced_result["certificate"])
    root = _symmetric_sqrt(matrix)
    normalized = root @ certificate @ root
    full_values, full_vectors = np.linalg.eigh((normalized + normalized.T) / 2.0)
    q = full_vectors[:, 0]
    rhs = root @ q
    denominator = float(rhs @ np.linalg.solve(matrix, rhs))
    exact_quadratic = float(rhs @ certificate @ rhs)

    rng = np.random.default_rng(seed)
    values = np.empty(samples)
    for sample in range(samples):
        values[sample] = sample_path_value(
            matrix, rhs, depth, rng.permutation(matrix.shape[0])
        )
    mean = float(np.mean(values))
    standard_error = float(np.std(values, ddof=1) / math.sqrt(samples))
    return {
        "evidence_level": "E1/E2 finite float diagnostics; Monte Carlo is not a proof",
        "candidate_source": str(path),
        "n": matrix.shape[0],
        "depth": depth,
        "symmetry_reduced_coefficient": float(reduced_result["coefficient"]),
        "full_matrix_coefficient": float(full_values[0]),
        "full_vs_reduced_absolute_gap": float(abs(full_values[0] - reduced_result["coefficient"])),
        "generalized_denominator": denominator,
        "dp_worst_direction_quadratic": exact_quadratic,
        "monte_carlo": {
            "seed": seed,
            "samples": samples,
            "mean": mean,
            "standard_error": standard_error,
            "mean_minus_dp": mean - exact_quadratic,
            "z_score": (mean - exact_quadratic) / standard_error,
            "sample_min": float(np.min(values)),
            "sample_max": float(np.max(values)),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--samples", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=202608219)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.candidate, args.samples, args.seed)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
