#!/usr/bin/env python3
"""E1 subset-DP scout for the reachable two-epoch warm inequality.

The dynamic program computes the exact uniform permutation average in
floating-point arithmetic using the recurrence

    F_S(X) = |S|^{-1} sum_{i in S} Z_i F_(S minus {i})(X) Z_i.

Thus it avoids factorial enumeration and reaches dimensions 8--12.  The
arithmetic is float64, so every null result remains E1.  A factorial n=5
regression checks the recurrence/orientation before the search.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEED = 2026082504
VIOLATION_TOLERANCE = 5e-9
SPD_TOLERANCE = 5e-11
DP_FACTORIAL_REGRESSION_TOLERANCE = 2e-12


def normalize_columns(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=0)
    if np.min(norms) < 1e-12:
        raise ValueError("degenerate Gram column")
    return matrix / norms


def boundary_gram(parameters: np.ndarray, rank: int, n: int) -> np.ndarray:
    synthesis = normalize_columns(parameters.reshape(rank, n))
    gram = synthesis.T @ synthesis
    return (gram + gram.T) / 2


def matrix_from_parameters(parameters: np.ndarray, rank: int, n: int, mu: float) -> np.ndarray:
    boundary = boundary_gram(parameters, rank, n)
    return mu * np.eye(n) + (1 - mu) * boundary


def energy_normals(a: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(a)
    square_root = (vectors * np.sqrt(values)) @ vectors.T
    return square_root


def project_both_sides(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    matrix_vector = matrix @ vector
    scalar = float(vector @ matrix_vector)
    result = (
        matrix
        - np.outer(vector, matrix_vector)
        - np.outer(matrix_vector, vector)
        + scalar * np.outer(vector, vector)
    )
    return (result + result.T) / 2


def average_epoch_subset(initial: np.ndarray, normals: np.ndarray) -> np.ndarray:
    n = normals.shape[1]
    states = np.zeros((1 << n, n, n), dtype=np.float64)
    states[0] = initial
    for mask in range(1, 1 << n):
        count = mask.bit_count()
        accumulator = np.zeros((n, n), dtype=np.float64)
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            accumulator += project_both_sides(states[mask ^ bit], normals[:, index])
            remaining ^= bit
        states[mask] = accumulator / count
    return states[-1]


def epoch_products(a: np.ndarray) -> list[np.ndarray]:
    n = len(a)
    identity = np.eye(n)
    updates = [identity - np.outer(identity[:, i], a[i, :]) for i in range(n)]
    values, vectors = np.linalg.eigh(a)
    square_root = (vectors * np.sqrt(values)) @ vectors.T
    inverse_square_root = (vectors * (1 / np.sqrt(values))) @ vectors.T
    products = []
    for order in itertools.permutations(range(n)):
        product = identity.copy()
        for index in order:
            product = updates[index] @ product
        products.append(square_root @ product @ inverse_square_root)
    return products


def factorial_average(initial: np.ndarray, products: list[np.ndarray]) -> np.ndarray:
    output = sum((product @ initial @ product.T for product in products), np.zeros_like(initial))
    output /= len(products)
    return (output + output.T) / 2


def diagnostic(a: np.ndarray) -> dict[str, float]:
    normals = energy_normals(a)
    identity = np.eye(len(a))
    h1 = average_epoch_subset(identity, normals)
    h2 = average_epoch_subset(h1, normals)
    mu = float(np.linalg.eigvalsh(a)[0])
    h1_values, h1_vectors = np.linalg.eigh(h1)
    if np.min(h1_values) <= 1e-14:
        return {
            "mu": mu,
            "warm_ratio": math.inf,
            "effective_c": -math.inf,
            "normalized_margin": -math.inf,
            "absolute_margin": -math.inf,
            "one_epoch_c": -math.inf,
        }
    inverse_sqrt = (h1_vectors * (1 / np.sqrt(h1_values))) @ h1_vectors.T
    relative = inverse_sqrt @ h2 @ inverse_sqrt
    relative = (relative + relative.T) / 2
    ratio = float(np.linalg.eigvalsh(relative)[-1])
    warm_difference = (1 - mu) * h1 - h2
    warm_relative = inverse_sqrt @ warm_difference @ inverse_sqrt
    warm_relative = (warm_relative + warm_relative.T) / 2
    loss = identity - h1
    one_relative = (loss + loss.T) / 2
    return {
        "mu": mu,
        "warm_ratio": ratio,
        "effective_c": (1 - ratio) / mu,
        "normalized_margin": float(np.linalg.eigvalsh(warm_relative)[0]),
        "absolute_margin": float(np.linalg.eigvalsh(warm_difference)[0]),
        "one_epoch_c": float(np.linalg.eigvalsh(one_relative)[0]) / mu,
    }


def regression(generator: np.random.Generator) -> dict[str, float | bool]:
    n = 5
    mu = 0.37
    parameters = generator.normal(size=(4, n))
    a = matrix_from_parameters(parameters.reshape(-1), 4, n, mu)
    normals = energy_normals(a)
    products = epoch_products(a)
    h1_dp = average_epoch_subset(np.eye(n), normals)
    h1_factorial = factorial_average(np.eye(n), products)
    h2_dp = average_epoch_subset(h1_dp, normals)
    h2_factorial = factorial_average(h1_factorial, products)
    error_h1 = float(np.linalg.norm(h1_dp - h1_factorial, ord=2))
    error_h2 = float(np.linalg.norm(h2_dp - h2_factorial, ord=2))
    return {
        "n": n,
        "mu": mu,
        "all_120_permutations_averaged_in_reference": True,
        "H1_operator_norm_error": error_h1,
        "H2_operator_norm_error": error_h2,
        "tolerance": DP_FACTORIAL_REGRESSION_TOLERANCE,
        "passed": error_h1 <= DP_FACTORIAL_REGRESSION_TOLERANCE and error_h2 <= DP_FACTORIAL_REGRESSION_TOLERANCE,
    }


def search_case(
    generator: np.random.Generator,
    n: int,
    rank: int,
    mu: float,
    samples: int,
) -> dict[str, object]:
    best = None
    for sample in range(samples):
        parameters = generator.normal(size=rank * n)
        a = matrix_from_parameters(parameters, rank, n, mu)
        result = diagnostic(a)
        record = {
            "sample": sample,
            "parameters": parameters.tolist(),
            "matrix": a.tolist(),
            "diagnostic": result,
        }
        if best is None or result["effective_c"] < best["diagnostic"]["effective_c"]:
            best = record
    assert best is not None
    return {
        "n": n,
        "boundary_rank": rank,
        "target_mu": mu,
        "samples": samples,
        "permutation_average": "subset DP over all subsets; algebraically exact recurrence, float64 arithmetic",
        "best": best,
        "potential_violation": best["diagnostic"]["effective_c"] < 1 - VIOLATION_TOLERANCE,
    }


def main() -> None:
    generator = np.random.default_rng(SEED)
    recurrence_regression = regression(generator)
    if not recurrence_regression["passed"]:
        raise RuntimeError(f"subset recurrence regression failed: {recurrence_regression}")
    cases = []
    for n, samples in ((8, 12), (10, 6), (12, 3)):
        ranks = (2, 3, n - 1)
        for mu in (0.95, 0.7, 0.2, 0.03):
            for rank in ranks:
                cases.append((n, rank, mu, samples))
    records = [search_case(generator, *case) for case in cases]
    global_best = min(records, key=lambda item: item["best"]["diagnostic"]["effective_c"])
    violations = [record for record in records if record["potential_violation"]]
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "float64 subset-DP reachable warm scout",
        "evidence_level": "E1",
        "seed": SEED,
        "numpy_version": np.__version__,
        "violation_tolerance": VIOLATION_TOLERANCE,
        "spd_tolerance": SPD_TOLERANCE,
        "subset_recurrence": "F_S(X)=|S|^{-1} sum_{i in S} Z_i F_{S\\{i}}(X) Z_i",
        "factorial_orientation_regression": recurrence_regression,
        "parameters": {
            "dimensions": [8, 10, 12],
            "boundary_ranks": "2,3,n-1",
            "mu_values": [0.95, 0.7, 0.2, 0.03],
            "case_count": len(records),
            "matrix_count": sum(record["samples"] for record in records),
        },
        "records": records,
        "global_best": global_best,
        "potential_violations": violations,
        "conclusion": (
            "A float64 candidate was found and requires exact reconstruction."
            if violations
            else "No warm violation was found; this higher-dimensional subset-DP null search remains E1 only."
        ),
        "scope": "The subset recurrence removes factorial enumeration but float64 null results do not prove the warm inequality or C050.",
    }
    output_path = HERE / "subset_warm_scout.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": SEED,
        "regression": recurrence_regression,
        "case_count": len(records),
        "matrix_count": output["parameters"]["matrix_count"],
        "global_best": global_best,
        "violation_count": len(violations),
        "output": str(output_path),
    }, indent=2))


if __name__ == "__main__":
    main()
