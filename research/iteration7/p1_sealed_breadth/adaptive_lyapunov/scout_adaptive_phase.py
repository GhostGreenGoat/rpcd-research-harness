"""Float64 scouts used only to select exact T143 adaptive-cone certificates.

Every selected candidate is re-evaluated by exact_adaptive_falsifiers.py.  This
file deliberately makes no theorem or infeasibility decision.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


SEED = 20260825
PSD_TOLERANCE = 1.0e-9


def epoch_maps(matrix: np.ndarray) -> list[np.ndarray]:
    n = matrix.shape[0]
    identity = np.eye(n)
    updates: list[np.ndarray] = []
    for index in range(n):
        coordinate = np.zeros((n, 1))
        coordinate[index] = 1.0
        updates.append(identity - coordinate @ (coordinate.T @ matrix))
    maps: list[np.ndarray] = []
    for permutation in itertools.permutations(range(n)):
        epoch = identity.copy()
        for index in permutation:
            epoch = updates[index] @ epoch
        maps.append(epoch)
    return maps


def covariance_adjoint(weight: np.ndarray, maps: list[np.ndarray]) -> np.ndarray:
    return sum(epoch.T @ weight @ epoch for epoch in maps) / len(maps)


def generalized_max(numerator: np.ndarray, denominator: np.ndarray) -> float:
    lower = np.linalg.cholesky(denominator)
    whitened = np.linalg.solve(lower, numerator)
    whitened = np.linalg.solve(lower, whitened.T).T
    return float(np.linalg.eigvalsh((whitened + whitened.T) / 2.0)[-1])


def base_chain() -> np.ndarray:
    return np.array([[1.0, 0.3, 0.0], [0.3, 1.0, 0.4], [0.0, 0.4, 1.0]])


def coupled_ladder_scout() -> list[dict[str, float]]:
    base = base_chain()
    records: list[dict[str, float]] = []
    for delta in (0.0, 0.02, 0.05, 0.1, 0.2, 0.3):
        matrix = np.block([[base, delta * np.eye(3)], [delta * np.eye(3), base]])
        maps = epoch_maps(matrix)
        first = covariance_adjoint(matrix, maps)
        second = covariance_adjoint(first, maps)
        mu = float(np.linalg.eigvalsh(matrix)[0])
        fixed_threshold = generalized_max(first, matrix)
        first_tail_threshold = generalized_max(second, first)
        records.append(
            {
                "delta": delta,
                "mu": mu,
                "fixed_threshold": fixed_threshold,
                "first_tail_threshold": first_tail_threshold,
                "tail_improvement": fixed_threshold - first_tail_threshold,
            }
        )
    return records


def phase_depth_scout() -> dict[str, object]:
    matrix = base_chain()
    maps = epoch_maps(matrix)
    weight = matrix.copy()
    transitions: list[float] = []
    for _ in range(15):
        following = covariance_adjoint(weight, maps)
        transitions.append(generalized_max(following, weight))
        weight = following
    closures = {}
    for rate in (0.16, 0.15, 0.149, 0.148, 0.147):
        closures[str(rate)] = next(
            (index for index, threshold in enumerate(transitions) if threshold <= rate),
            None,
        )
    return {"transition_thresholds": transitions, "first_closing_phase": closures}


def near_singular_grid_scout() -> dict[str, object]:
    worst_terminal = float("inf")
    worst_comparison = float("inf")
    worst_r = None
    for r in np.linspace(0.001, 0.999, 999):
        matrix = np.array(
            [[1.0, 0.6 * r, 0.0], [0.6 * r, 1.0, 0.8 * r], [0.0, 0.8 * r, 1.0]]
        )
        maps = epoch_maps(matrix)
        first = covariance_adjoint(matrix, maps)
        tail = first / r
        terminal_margin = float(
            np.linalg.eigvalsh(r * tail - covariance_adjoint(tail, maps))[0]
        )
        comparison_margin = float(np.linalg.eigvalsh(matrix - tail)[0])
        if min(terminal_margin, comparison_margin) < min(worst_terminal, worst_comparison):
            worst_r = float(r)
        worst_terminal = min(worst_terminal, terminal_margin)
        worst_comparison = min(worst_comparison, comparison_margin)
    return {
        "grid": "r=0.001,...,0.999 in increments of 0.001",
        "worst_r_by_combined_margin": worst_r,
        "minimum_terminal_eigenvalue": worst_terminal,
        "minimum_A_minus_R_eigenvalue": worst_comparison,
        "null_result_only": True,
    }


def random_positive_combination_scout() -> dict[str, object]:
    matrix = base_chain()
    maps = epoch_maps(matrix)
    rate = 0.15
    first = covariance_adjoint(matrix, maps)
    facets: list[np.ndarray] = []
    weight = matrix.copy()
    for _ in range(8):
        weight = covariance_adjoint(weight, maps) / rate
        facets.append(weight)
    generator = np.random.default_rng(SEED)
    for iteration in range(200_000):
        coefficients = np.exp(generator.uniform(-4.0, 3.0, len(facets)))
        candidate = sum(
            coefficient * facet for coefficient, facet in zip(coefficients, facets, strict=True)
        )
        margin = min(
            float(np.linalg.eigvalsh(rate * candidate - first)[0]),
            float(np.linalg.eigvalsh(rate * candidate - covariance_adjoint(candidate, maps))[0]),
        )
        if margin > PSD_TOLERANCE:
            return {
                "iterations_before_hit": iteration + 1,
                "coefficients": coefficients.tolist(),
                "minimum_margin": margin,
                "seed": SEED,
                "tolerance": PSD_TOLERANCE,
                "use": "Scout only; replaced by the exact rational resolvent calculation.",
            }
    return {
        "iterations_before_hit": None,
        "seed": SEED,
        "tolerance": PSD_TOLERANCE,
        "use": "Numerical null result only.",
    }


def block_power_obstruction_scout() -> dict[str, object]:
    matrix = base_chain()
    maps = epoch_maps(matrix)
    rate = 0.14
    kappa = 2.0
    ray = np.array([-2.0, 4.0, -3.0])
    power = matrix.copy()
    records: list[dict[str, float | int]] = []
    for epoch_count in range(1, 20):
        power = covariance_adjoint(power, maps)
        gap = kappa * rate**epoch_count * matrix - power
        ray_value = float(ray @ gap @ ray)
        minimum_eigenvalue = float(np.linalg.eigvalsh(gap)[0])
        records.append(
            {
                "epoch_count": epoch_count,
                "ray_value": ray_value,
                "minimum_eigenvalue": minimum_eigenvalue,
            }
        )
        if ray_value < -PSD_TOLERANCE * 1.0e-3:
            break
    return {
        "q": rate,
        "kappa": kappa,
        "ray": ray.tolist(),
        "records_through_first_tiny_violation": records,
        "use": "Selected the m=11 rational witness; exact_adaptive_falsifiers.py makes the decision with zero tolerance.",
    }


def bounded_tail_metric_scout() -> dict[str, object]:
    matrix = base_chain()
    maps = epoch_maps(matrix)
    rate = 0.15
    kappa = 1.3
    first = covariance_adjoint(matrix, maps)
    canonical = first / rate
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    square_root = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
    inverse_square_root = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
    canonical_whitened = inverse_square_root @ canonical @ inverse_square_root
    capacity = kappa * np.eye(3) - canonical_whitened
    capacity_values, capacity_vectors = np.linalg.eigh(capacity)
    capacity_square_root = (
        capacity_vectors @ np.diag(np.sqrt(np.maximum(capacity_values, 0.0))) @ capacity_vectors.T
    )
    generator = np.random.default_rng(SEED)
    for iteration in range(500_000):
        gaussian = generator.normal(size=(3, 3))
        orthogonal, _ = np.linalg.qr(gaussian)
        levels = generator.random(3)
        increment = capacity_square_root @ (
            orthogonal @ np.diag(levels) @ orthogonal.T
        ) @ capacity_square_root
        candidate = square_root @ (canonical_whitened + increment) @ square_root
        terminal_margin = float(
            np.linalg.eigvalsh(rate * candidate - covariance_adjoint(candidate, maps))[0]
        )
        if terminal_margin > 1.0e-5:
            rounded = np.rint(candidate * 10_000.0).astype(int) / 10_000.0
            return {
                "iterations_before_hit": iteration + 1,
                "terminal_margin": terminal_margin,
                "candidate_float64": candidate.tolist(),
                "candidate_rounded_denominator_10000": rounded.tolist(),
                "seed": SEED,
                "selection_threshold": 1.0e-5,
                "use": "The rounded matrix was then certified exactly with kappa=13/10.",
            }
    return {
        "iterations_before_hit": None,
        "seed": SEED,
        "selection_threshold": 1.0e-5,
        "use": "Numerical null result only.",
    }


def bounded_tail_no_hit_scout() -> dict[str, object]:
    matrix = base_chain()
    maps = epoch_maps(matrix)
    rate = 0.15
    kappa = 1.2
    first = covariance_adjoint(matrix, maps)
    canonical = first / rate
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    square_root = eigenvectors @ np.diag(np.sqrt(eigenvalues)) @ eigenvectors.T
    inverse_square_root = eigenvectors @ np.diag(1.0 / np.sqrt(eigenvalues)) @ eigenvectors.T
    canonical_whitened = inverse_square_root @ canonical @ inverse_square_root
    capacity = kappa * np.eye(3) - canonical_whitened
    capacity_values, capacity_vectors = np.linalg.eigh(capacity)
    capacity_square_root = (
        capacity_vectors @ np.diag(np.sqrt(np.maximum(capacity_values, 0.0))) @ capacity_vectors.T
    )
    generator = np.random.default_rng(SEED)
    best_margin = -float("inf")
    for _ in range(500_000):
        gaussian = generator.normal(size=(3, 3))
        orthogonal, _ = np.linalg.qr(gaussian)
        levels = generator.random(3)
        increment = capacity_square_root @ (
            orthogonal @ np.diag(levels) @ orthogonal.T
        ) @ capacity_square_root
        candidate = square_root @ (canonical_whitened + increment) @ square_root
        terminal_margin = float(
            np.linalg.eigvalsh(rate * candidate - covariance_adjoint(candidate, maps))[0]
        )
        best_margin = max(best_margin, terminal_margin)
    return {
        "trials": 500_000,
        "q": rate,
        "kappa": kappa,
        "seed": SEED,
        "best_terminal_margin": best_margin,
        "hit_above_tolerance": best_margin > PSD_TOLERANCE,
        "tolerance": PSD_TOLERANCE,
        "use": "Numerical null result only; it is not a dual infeasibility certificate and does not prove kappa_tail>6/5.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E1",
        "arithmetic": "numpy float64",
        "seed": SEED,
        "psd_tolerance": PSD_TOLERANCE,
        "warning": "Scouts select candidates only; every decisive result is separately checked over exact rationals or symbolic polynomials.",
        "coupled_ladder_scout": coupled_ladder_scout(),
        "phase_depth_scout": phase_depth_scout(),
        "near_singular_grid_scout": near_singular_grid_scout(),
        "random_positive_combination_scout": random_positive_combination_scout(),
        "block_power_obstruction_scout": block_power_obstruction_scout(),
        "bounded_tail_metric_scout": bounded_tail_metric_scout(),
        "bounded_tail_no_hit_scout": bounded_tail_no_hit_scout(),
    }
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if arguments.output is not None:
        arguments.output.write_bytes(encoded)
        print(
            json.dumps(
                {"output": str(arguments.output), "sha256": hashlib.sha256(encoded).hexdigest()}
            )
        )
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
