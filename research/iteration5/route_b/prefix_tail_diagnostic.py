"""Compare the half-prefix J_r with the determinant-tail certificate H_r.

This is a finite float64 diagnostic.  It identifies whether a structured
candidate is hostile because of the prefix itself or because the determinant
leaf is essential; it does not prove a universal comparison.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, _symmetric_sqrt, representation_to_full


def candidate_from(path: Path) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    return document.get(
        "global_best", document.get("best", document.get("best_ratio", document))
    )


def diagnose(path: Path) -> dict[str, object]:
    candidate = candidate_from(path)
    counts = tuple(candidate["counts"])
    within = np.asarray(candidate["within"], dtype=float)
    cross = np.asarray(candidate["cross"], dtype=float)
    depth = int(candidate["depth"])
    h_dp = ExchangeableTailDP(counts, within, cross, "determinant")
    j_dp = ExchangeableTailDP(counts, within, cross, "zero")
    h = h_dp.coefficient(depth)
    j = j_dp.coefficient(depth)
    matrix = h_dp.root_matrix()
    h_full = representation_to_full(counts, h["certificate"])
    j_full = representation_to_full(counts, j["certificate"])
    root = _symmetric_sqrt(matrix)
    h_normalized = root @ h_full @ root
    j_normalized = root @ j_full @ root
    h_values, h_vectors = np.linalg.eigh((h_normalized + h_normalized.T) / 2.0)
    j_values = np.linalg.eigvalsh((j_normalized + j_normalized.T) / 2.0)
    tail_values = np.linalg.eigvalsh(
        (h_normalized - j_normalized + (h_normalized - j_normalized).T) / 2.0
    )
    q = h_vectors[:, 0]
    prefix_on_h_worst = float(q @ j_normalized @ q)
    tail_on_h_worst = float(q @ (h_normalized - j_normalized) @ q)
    mu = float(np.linalg.eigvalsh(matrix)[0])
    return {
        "evidence_level": "E1/E2 finite float diagnostic; not a proof",
        "candidate_source": str(path),
        "n": sum(counts),
        "depth": depth,
        "mu": mu,
        "H": {
            "coefficient": float(h_values[0]),
            "ratio": float(h_values[0] / mu),
            "sector": h["sector"],
        },
        "J": {
            "coefficient": float(j_values[0]),
            "ratio": float(j_values[0] / mu),
            "sector_from_reduction": j["sector"],
        },
        "determinant_tail": {
            "minimum_normalized_eigenvalue": float(tail_values[0]),
            "maximum_normalized_eigenvalue": float(tail_values[-1]),
            "prefix_on_H_worst_direction": prefix_on_h_worst,
            "tail_on_H_worst_direction": tail_on_h_worst,
            "fraction_of_H_worst_quadratic": float(tail_on_h_worst / h_values[0]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidates", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = {
        "candidate_claim_H": "H_ceil(n/2) >= (mu/2) A^{-1}",
        "stronger_prefix_claim_J": "J_ceil(n/2) >= (mu/2) A^{-1}",
        "results": [diagnose(path) for path in args.candidates],
    }
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
