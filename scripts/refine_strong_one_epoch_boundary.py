"""Greedy boundary-elliptope refinement for the strong RPCD energy target.

This companion to ``search_strong_one_epoch_energy.py`` starts from a saved
low-rank Gram candidate and performs deterministic-scale random tangent moves
on its unit-vector representation.  Its JSON output is E1 evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from scripts.search_strong_one_epoch_energy import evaluate, lifted, normalize_rows


def gram_vectors(matrix: np.ndarray, mu: float) -> np.ndarray:
    c = (matrix - mu * np.eye(matrix.shape[0])) / (1.0 - mu)
    values, vectors = np.linalg.eigh((c + c.T) / 2.0)
    positive = values > 1e-8
    result = vectors[:, positive] * np.sqrt(values[positive])
    return normalize_rows(result)


def refine(
    vectors: np.ndarray,
    mu: float,
    rng: np.random.Generator,
    scales: list[float],
    attempts_per_scale: int,
) -> tuple[np.ndarray, dict[str, object], list[dict[str, float]]]:
    current = evaluate(lifted(vectors @ vectors.T, mu))
    trace: list[dict[str, float]] = []
    for scale in scales:
        accepted = 0
        for _ in range(attempts_per_scale):
            candidate = vectors.copy()
            if rng.random() < 0.85:
                rows = [int(rng.integers(candidate.shape[0]))]
            else:
                rows = list(rng.choice(candidate.shape[0], size=2, replace=False))
            for row in rows:
                direction = rng.normal(size=candidate.shape[1])
                direction -= np.dot(direction, candidate[row]) * candidate[row]
                norm = np.linalg.norm(direction)
                if norm < 1e-14:
                    continue
                candidate[row] += scale * direction / norm
                candidate[row] /= np.linalg.norm(candidate[row])
            record = evaluate(lifted(candidate @ candidate.T, mu))
            if float(record["gap_rate_minus_target"]) > float(
                current["gap_rate_minus_target"]
            ):
                vectors = candidate
                current = record
                accepted += 1
        trace.append(
            {
                "scale": scale,
                "accepted": accepted,
                "gap": float(current["gap_rate_minus_target"]),
                "small_mu_loss_coefficient": (1.0 - float(current["energy_rate"])) / mu,
            }
        )
    return vectors, current, trace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--candidate-index", type=int, default=0)
    parser.add_argument("--seed", type=int, default=20260824)
    parser.add_argument("--attempts-per-scale", type=int, default=1500)
    parser.add_argument("--scales", default="0.3,0.15,0.07,0.03,0.01,0.003,0.001")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/M1_BOUNDARY_REFINEMENT_2026_08_21.json"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    initial = source["best"][args.candidate_index]
    matrix = np.asarray(initial["matrix"], dtype=float)
    mu = float(initial["mu"])
    vectors = gram_vectors(matrix, mu)
    vectors, best, trace = refine(
        vectors,
        mu,
        np.random.default_rng(args.seed),
        [float(item) for item in args.scales.split(",")],
        args.attempts_per_scale,
    )
    payload = {
        "status": "E1 numerical refinement; no theorem or certified counterexample",
        "source": str(args.input),
        "source_candidate_index": args.candidate_index,
        "seed": args.seed,
        "attempts_per_scale": args.attempts_per_scale,
        "rank": int(vectors.shape[1]),
        "initial": initial,
        "trace": trace,
        "best": best,
        "vectors": vectors.tolist(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "initial_gap": initial["gap_rate_minus_target"],
        "final_gap": best["gap_rate_minus_target"],
        "loss_coefficient": (1.0 - float(best["energy_rate"])) / mu,
    }, indent=2))
