#!/usr/bin/env python3
"""E1 optimized/high-dimensional continuation of the subset-DP warm scout."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from scout_subset_warm import diagnostic, matrix_from_parameters


HERE = Path(__file__).resolve().parent
SEED = 2026082505
VIOLATION_TOLERANCE = 5e-9


def make_record(parameters: np.ndarray, rank: int, n: int, mu: float) -> dict[str, object]:
    matrix = matrix_from_parameters(parameters, rank, n, mu)
    return {
        "parameters": parameters.tolist(),
        "matrix": matrix.tolist(),
        "diagnostic": diagnostic(matrix),
    }


def hill_attack(
    generator: np.random.Generator,
    initial: np.ndarray,
    rank: int,
    n: int,
    mu: float,
    steps: int,
) -> dict[str, object]:
    current_parameters = initial.copy()
    current = make_record(current_parameters, rank, n, mu)
    best = current
    accepted = 0
    for step in range(steps):
        scale = 0.20 * (0.01 / 0.20) ** (step / max(steps - 1, 1))
        proposal_parameters = current_parameters + scale * generator.normal(size=current_parameters.shape)
        proposal = make_record(proposal_parameters, rank, n, mu)
        delta = proposal["diagnostic"]["effective_c"] - current["diagnostic"]["effective_c"]
        temperature = 0.002 * (1 - step / steps)
        if delta < 0 or (temperature > 0 and generator.random() < math.exp(-delta / temperature)):
            current_parameters = proposal_parameters
            current = proposal
            accepted += 1
        if current["diagnostic"]["effective_c"] < best["diagnostic"]["effective_c"]:
            best = current
    return {
        "n": n,
        "boundary_rank": rank,
        "target_mu": mu,
        "steps": steps,
        "accepted": accepted,
        "best": best,
        "potential_violation": best["diagnostic"]["effective_c"] < 1 - VIOLATION_TOLERANCE,
    }


def random_attack(
    generator: np.random.Generator,
    rank: int,
    n: int,
    mu: float,
    samples: int,
) -> dict[str, object]:
    records = [make_record(generator.normal(size=rank * n), rank, n, mu) for _ in range(samples)]
    best = min(records, key=lambda record: record["diagnostic"]["effective_c"])
    return {
        "n": n,
        "boundary_rank": rank,
        "target_mu": mu,
        "samples": samples,
        "best": best,
        "potential_violation": best["diagnostic"]["effective_c"] < 1 - VIOLATION_TOLERANCE,
    }


def main() -> None:
    generator = np.random.default_rng(SEED)
    baseline = json.loads((HERE / "subset_warm_scout.json").read_text(encoding="utf-8"))
    initial = np.asarray(baseline["global_best"]["best"]["parameters"], dtype=np.float64)
    records = [
        hill_attack(generator, initial, rank=2, n=12, mu=0.95, steps=160),
        random_attack(generator, rank=2, n=14, mu=0.95, samples=8),
        random_attack(generator, rank=13, n=14, mu=0.95, samples=4),
        random_attack(generator, rank=2, n=14, mu=0.70, samples=4),
    ]
    best = min(records, key=lambda record: record["best"]["diagnostic"]["effective_c"])
    violations = [record for record in records if record["potential_violation"]]
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "optimized float64 subset-DP warm attack",
        "evidence_level": "E1",
        "seed": SEED,
        "violation_tolerance": VIOLATION_TOLERANCE,
        "records": records,
        "global_best": best,
        "potential_violations": violations,
        "conclusion": (
            "A float64 candidate was found and requires exact reconstruction."
            if violations
            else "No violation was found; the optimized/high-dimensional null attack remains E1 only."
        ),
        "scope": "The all-subset recurrence is exact, but matrix synthesis and diagnostics are float64 and finite.",
    }
    output_path = HERE / "subset_warm_attack.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": SEED,
        "record_count": len(records),
        "global_best": best,
        "violation_count": len(violations),
        "output": str(output_path),
    }, indent=2))


if __name__ == "__main__":
    main()
