"""Check the original RPCD covariance rate on the T080 counterexample ray.

This exhaustive float64 diagnostic separates two statements:

* the stronger one-epoch A-energy inequality is exactly false;
* the original averaged covariance spectral-radius conjecture is not violated
  at the finite ``mu`` values checked here.

Finite positive margins are E1 evidence only.  The energy-coordinate
similarity is essential: the covariance superoperator is self-adjoint there,
not in the original x coordinates.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from itertools import permutations
from pathlib import Path

import numpy as np


def boundary_matrix() -> np.ndarray:
    matrix = np.full((8, 8), 71.0 / 125.0)
    np.fill_diagonal(matrix, 1.0)
    matrix[:2, :2] = 1.0
    matrix[:2, 2:] = 4.0 / 5.0
    matrix[2:, :2] = 4.0 / 5.0
    return matrix


def covariance_record(mu: float) -> dict[str, float]:
    n = 8
    matrix = mu * np.eye(n) + (1.0 - mu) * boundary_matrix()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    square_root = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    inverse_square_root = (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T
    covariance = np.zeros((n * n, n * n))
    started = time.time()
    for order in permutations(range(n)):
        permutation = np.eye(n)[:, order]
        factor = permutation @ np.tril(permutation.T @ matrix @ permutation) @ permutation.T
        transform = np.eye(n) - np.linalg.solve(factor, matrix)
        energy_transform = square_root @ transform @ inverse_square_root
        covariance += np.kron(energy_transform, energy_transform)
    covariance /= math.factorial(n)
    symmetry_error = float(np.max(np.abs(covariance - covariance.T)))
    spectrum = np.linalg.eigvalsh((covariance + covariance.T) / 2.0)
    radius = float(max(abs(spectrum[0]), abs(spectrum[-1])))
    target = max((1.0 - 1.0 / n) ** n, (1.0 - mu / n) ** (2 * n))
    return {
        "mu": mu,
        "spectral_radius": radius,
        "target_q": target,
        "q_minus_radius": target - radius,
        "minimum_superoperator_eigenvalue": float(spectrum[0]),
        "maximum_superoperator_eigenvalue": float(spectrum[-1]),
        "self_adjoint_symmetry_error": symmetry_error,
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mus", default="0.01,0.001")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T080_COUNTEREXAMPLE_COVARIANCE_CHECK_2026_08_21.json"
        ),
    )
    args = parser.parse_args()
    records = [covariance_record(float(raw)) for raw in args.mus.split(",")]
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E1",
        "status": "finite exhaustive covariance-rate check; positive margins are not a proof",
        "scope": (
            "Separates the refuted strong A-energy certificate from the still-open "
            "RPCD covariance spectral-radius conjecture."
        ),
        "permutations_per_mu": math.factorial(8),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": records}, indent=2))


if __name__ == "__main__":
    main()
