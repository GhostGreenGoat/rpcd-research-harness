#!/usr/bin/env python3
"""Independent original-coordinate re-evaluation of the n=14 E1 separator.

This uses the dual recursion conditioned on the first coordinate update,
without forming energy-coordinate square roots or projection congruences.
It is an independent floating-point formulation, not an interval certificate;
the result remains E1.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
MATCH_TOLERANCE = 2e-10


def update_dual_both_sides(matrix: np.ndarray, row: np.ndarray, index: int) -> np.ndarray:
    column = matrix[:, index]
    result = (
        matrix
        - np.outer(row, column)
        - np.outer(column, row)
        + matrix[index, index] * np.outer(row, row)
    )
    return (result + result.T) / 2


def average_dual_subset(initial: np.ndarray, a: np.ndarray) -> np.ndarray:
    n = len(a)
    states = np.zeros((1 << n, n, n), dtype=np.float64)
    states[0] = initial
    for mask in range(1, 1 << n):
        accumulator = np.zeros((n, n), dtype=np.float64)
        remaining = mask
        while remaining:
            bit = remaining & -remaining
            index = bit.bit_length() - 1
            accumulator += update_dual_both_sides(states[mask ^ bit], a[index, :], index)
            remaining ^= bit
        states[mask] = accumulator / mask.bit_count()
    return states[-1]


def inverse_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(matrix)
    return (vectors * (1 / np.sqrt(values))) @ vectors.T


def main() -> None:
    inherited = json.loads((HERE / "subset_warm_attack.json").read_text(encoding="utf-8"))
    record = inherited["global_best"]
    a = np.asarray(record["best"]["matrix"], dtype=np.float64)
    reference = record["best"]["diagnostic"]
    mu = float(np.linalg.eigvalsh(a)[0])
    h1 = average_dual_subset(a, a)
    h2 = average_dual_subset(h1, a)

    h1_inverse_sqrt = inverse_sqrt(h1)
    warm_relative = h1_inverse_sqrt @ h2 @ h1_inverse_sqrt
    warm_relative = (warm_relative + warm_relative.T) / 2
    warm_ratio = float(np.linalg.eigvalsh(warm_relative)[-1])
    warm_difference = (1 - mu) * h1 - h2
    normalized_warm = h1_inverse_sqrt @ warm_difference @ h1_inverse_sqrt
    normalized_warm = (normalized_warm + normalized_warm.T) / 2

    a_inverse_sqrt = inverse_sqrt(a)
    one_epoch_loss = a - h1
    one_epoch_relative = a_inverse_sqrt @ one_epoch_loss @ a_inverse_sqrt
    one_epoch_relative = (one_epoch_relative + one_epoch_relative.T) / 2
    diagnostic = {
        "mu": mu,
        "warm_ratio": warm_ratio,
        "effective_c": (1 - warm_ratio) / mu,
        "normalized_margin": float(np.linalg.eigvalsh(normalized_warm)[0]),
        "absolute_margin": float(np.linalg.eigvalsh(warm_difference)[0]),
        "one_epoch_c": float(np.linalg.eigvalsh(one_epoch_relative)[0]) / mu,
    }
    invariant_keys = ["mu", "warm_ratio", "effective_c", "normalized_margin", "one_epoch_c"]
    discrepancies = {
        key: abs(diagnostic[key] - reference[key])
        for key in invariant_keys
    }
    passed = max(discrepancies.values()) <= MATCH_TOLERANCE
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "independent original-coordinate re-evaluation of subset-DP separator",
        "evidence_level": "E1",
        "source_artifact": "subset_warm_attack.json",
        "source_record": {"n": record["n"], "boundary_rank": record["boundary_rank"], "target_mu": record["target_mu"]},
        "formulation": "G_S(H)=|S|^{-1} sum_{i in S} U_i^T G_(S minus {i})(H) U_i, conditioned on the first update",
        "reference_energy_coordinate_diagnostic": reference,
        "original_coordinate_diagnostic": diagnostic,
        "absolute_discrepancies": discrepancies,
        "coordinate_dependent_absolute_margin_note": (
            "Raw minimum eigenvalues of congruent warm-difference matrices are not invariant; "
            "both displayed absolute margins are positive but are deliberately excluded from the match test."
        ),
        "match_tolerance": MATCH_TOLERANCE,
        "formulations_match_within_tolerance": passed,
        "full_psd_shortcut_failure_candidate": diagnostic["one_epoch_c"] < 1,
        "reachable_warm_candidate_survives": diagnostic["effective_c"] > 1,
        "scope": (
            "This independent formulation checks orientation and the numerical separation only. "
            "It is not exact or interval-certified, remains E1, and does not refute the warm inequality, locked block lemma, C051 with a smaller constant, or C050."
        ),
    }
    output_path = HERE / "subset_candidate_reevaluation.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
