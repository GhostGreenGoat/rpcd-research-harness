#!/usr/bin/env python3
"""Adversarial float64 search for the T143 reachable two-epoch inequality.

This is a scout only (E1).  It searches unit-diagonal SPD matrices of the
form A=mu I+(1-mu)G where G is a singular correlation Gram matrix.  Every
reported objective averages all epoch permutations.  Any apparent violation
must be reconstructed with exact or interval arithmetic before it is used as
decisive evidence.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SEED = 2026082503
VIOLATION_TOLERANCE = 5e-10
SPD_TOLERANCE = 5e-11


def normalize_columns(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=0)
    if np.min(norms) < 1e-12:
        raise ValueError("degenerate synthesis column")
    return x / norms


def boundary_from_parameters(parameters: np.ndarray, rank: int, n: int) -> np.ndarray:
    synthesis = normalize_columns(parameters.reshape(rank, n))
    gram = synthesis.T @ synthesis
    return (gram + gram.T) / 2


def epoch_products(a: np.ndarray, orders: list[tuple[int, ...]]) -> np.ndarray:
    n = len(a)
    identity = np.eye(n)
    updates = [identity - np.outer(identity[:, i], a[i, :]) for i in range(n)]
    products = []
    for order in orders:
        product = identity
        for index in order:
            product = updates[index] @ product
        products.append(product)
    return np.asarray(products)


def warm_diagnostic(a: np.ndarray, orders: list[tuple[int, ...]]) -> dict[str, float]:
    products = epoch_products(a, orders)
    h1 = np.einsum("pji,jk,pkl->il", products, a, products) / len(products)
    h1 = (h1 + h1.T) / 2
    h2 = np.einsum("pji,jk,pkl->il", products, h1, products) / len(products)
    h2 = (h2 + h2.T) / 2
    mu = float(np.linalg.eigvalsh(a)[0])
    h1_values, h1_vectors = np.linalg.eigh(h1)
    if np.min(h1_values) <= 1e-13:
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
    margin_matrix = (1 - mu) * h1 - h2
    margin_relative = inverse_sqrt @ margin_matrix @ inverse_sqrt
    margin_relative = (margin_relative + margin_relative.T) / 2
    order_unit_loss = a - h1
    a_values, a_vectors = np.linalg.eigh(a)
    a_inverse_sqrt = (a_vectors * (1 / np.sqrt(a_values))) @ a_vectors.T
    one_relative = a_inverse_sqrt @ order_unit_loss @ a_inverse_sqrt
    one_relative = (one_relative + one_relative.T) / 2
    return {
        "mu": mu,
        "warm_ratio": ratio,
        "effective_c": (1 - ratio) / mu,
        "normalized_margin": float(np.linalg.eigvalsh(margin_relative)[0]),
        "absolute_margin": float(np.linalg.eigvalsh(margin_matrix)[0]),
        "one_epoch_c": float(np.linalg.eigvalsh(one_relative)[0]) / mu,
    }


def matrix_from_parameters(parameters: np.ndarray, rank: int, n: int, mu: float) -> np.ndarray:
    boundary = boundary_from_parameters(parameters, rank, n)
    return mu * np.eye(n) + (1 - mu) * boundary


def search_case(
    generator: np.random.Generator,
    n: int,
    rank: int,
    mu: float,
    restarts: int,
    steps: int,
    objective_key: str = "effective_c",
) -> dict[str, object]:
    orders = list(itertools.permutations(range(n)))
    best_parameters = None
    best_matrix = None
    best_diagnostic = None
    evaluations = 0
    accepted = 0
    restart_summaries = []
    for restart in range(restarts):
        parameters = generator.normal(size=rank * n)
        matrix = matrix_from_parameters(parameters, rank, n, mu)
        diagnostic = warm_diagnostic(matrix, orders)
        evaluations += 1
        local_best = diagnostic[objective_key]
        initial_scale = 0.35
        for step in range(steps):
            scale = initial_scale * (0.02 / initial_scale) ** (step / max(steps - 1, 1))
            proposal = parameters + scale * generator.normal(size=parameters.shape)
            proposal_matrix = matrix_from_parameters(proposal, rank, n, mu)
            proposal_diagnostic = warm_diagnostic(proposal_matrix, orders)
            evaluations += 1
            delta = proposal_diagnostic[objective_key] - diagnostic[objective_key]
            temperature = 0.01 * (1 - step / max(steps, 1))
            if delta < 0 or (temperature > 0 and generator.random() < math.exp(-delta / temperature)):
                parameters = proposal
                matrix = proposal_matrix
                diagnostic = proposal_diagnostic
                accepted += 1
            local_best = min(local_best, diagnostic[objective_key])
            if best_diagnostic is None or diagnostic[objective_key] < best_diagnostic[objective_key]:
                best_parameters = parameters.copy()
                best_matrix = matrix.copy()
                best_diagnostic = dict(diagnostic)
        restart_summaries.append({"restart": restart, "best_objective_seen": local_best})
    assert best_parameters is not None and best_matrix is not None and best_diagnostic is not None
    return {
        "n": n,
        "boundary_rank": rank,
        "target_mu": mu,
        "all_permutations_averaged": True,
        "restarts": restarts,
        "steps_per_restart": steps,
        "evaluations": evaluations,
        "accepted_proposals": accepted,
        "objective_key": objective_key,
        "best_parameters": best_parameters.tolist(),
        "best_matrix": best_matrix.tolist(),
        "best_diagnostic": best_diagnostic,
        "restart_summaries": restart_summaries,
        "potential_violation": best_diagnostic[objective_key] < 1 - VIOLATION_TOLERANCE,
    }


def main() -> None:
    generator = np.random.default_rng(SEED)
    cases = [
        # High mu is the tight regime found in phase 2.
        (4, 2, 0.95, 10, 600),
        (4, 3, 0.95, 10, 600),
        (5, 2, 0.95, 8, 450),
        (5, 3, 0.95, 8, 450),
        (5, 4, 0.95, 8, 450),
        # Intermediate and singular-boundary regimes probe a distinct mechanism.
        (4, 2, 0.70, 8, 500),
        (4, 3, 0.30, 8, 500),
        (5, 2, 0.10, 6, 350),
        (5, 3, 0.03, 6, 350),
        (6, 2, 0.90, 4, 180),
        (6, 3, 0.10, 4, 180),
        (6, 5, 0.90, 4, 180),
        # Dimension seven is substantially dearer (5040 products per evaluation),
        # so use a short attack that still averages every permutation.
        (7, 2, 0.90, 2, 40),
        (7, 6, 0.70, 2, 40),
    ]
    records = [
        search_case(generator, n, rank, mu, restarts, steps)
        for n, rank, mu, restarts, steps in cases
    ]
    best = min(records, key=lambda item: item["best_diagnostic"]["effective_c"])
    violations = [record for record in records if record["potential_violation"]]
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "adversarial float64 warm-start search",
        "evidence_level": "E1",
        "seed": SEED,
        "numpy_version": np.__version__,
        "violation_tolerance": VIOLATION_TOLERANCE,
        "spd_tolerance": SPD_TOLERANCE,
        "objective": "minimize (1-lambda_max(H1^{-1/2}H2H1^{-1/2}))/mu",
        "records": records,
        "global_best": best,
        "potential_violations": violations,
        "conclusion": (
            "A float64 warm-start candidate was found and requires exact reconstruction."
            if violations
            else "No violation was found; this adversarial null search remains E1 only."
        ),
    }
    output_path = HERE / "warm_start_attack.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": SEED,
        "cases": len(records),
        "global_best": best,
        "potential_violation_count": len(violations),
        "output": str(output_path),
    }, indent=2))


if __name__ == "__main__":
    main()
