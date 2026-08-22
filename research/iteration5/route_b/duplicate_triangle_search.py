"""Hostile search over three groups of duplicate planar Gram vectors.

This contains the replicated regular-simplex family but also permits unequal
group sizes and a frustrated, non-equilateral triangle of prototype vectors.
The matrices are exact PSD Gram lifts by construction.  Search conclusions are
E1 float64 evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, evaluate_family


def counts_from_proportions(total: int, proportions: np.ndarray) -> tuple[int, int, int]:
    raw = proportions / proportions.sum() * (total - 6)
    counts = np.floor(raw).astype(int) + 2
    while counts.sum() < total:
        index = int(np.argmax(raw - np.floor(raw)))
        counts[index] += 1
        raw[index] = math.floor(raw[index])
    while counts.sum() > total:
        index = int(np.argmax(counts))
        counts[index] -= 1
    return tuple(int(x) for x in counts)


def search(seed: int, total: int, evaluations: int, objective: str) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    best = None
    started = time.time()
    history = []
    for evaluation in range(evaluations):
        if evaluation == 0:
            counts = counts_from_proportions(total, np.ones(3))
            angles = np.array([0.0, 2 * math.pi / 3, 4 * math.pi / 3])
            mu = 0.90
        else:
            if best is not None and rng.random() < 0.65:
                base_counts = np.asarray(best["counts"], dtype=float)
                counts = counts_from_proportions(
                    total, np.maximum(0.02, base_counts / total + 0.08 * rng.normal(size=3))
                )
                base_angles = np.arctan2(
                    np.asarray(best["directions"])[:, 1],
                    np.asarray(best["directions"])[:, 0],
                )
                angles = base_angles + rng.normal(scale=0.16, size=3)
                base_mu = float(best["mu_parameter"])
                mu = float(np.clip(base_mu + rng.normal(scale=0.035), 0.02, 0.995))
            else:
                counts = counts_from_proportions(total, rng.dirichlet(np.full(3, 0.7)))
                angles = rng.uniform(0.0, 2 * math.pi, size=3)
                mu = float(1.0 - 10.0 ** rng.uniform(-2.3, -0.25))
        directions = np.column_stack((np.cos(angles), np.sin(angles)))
        item = evaluate_family(
            "duplicate_triangle",
            counts,
            directions,
            (1.0, 1.0, 1.0),
            mu,
            {"evaluation": evaluation, "angles": angles.tolist()},
        )
        cross = np.asarray(item["cross"])
        sign_product = float(cross[0, 1] * cross[0, 2] * cross[1, 2])
        item["metadata"]["cross_sign_product"] = sign_product
        baseline_dp = ExchangeableTailDP(
            (total,), (1.0 - item["actual_mu"],), np.zeros((1, 1))
        )
        baseline = baseline_dp.coefficient((total + 1) // 2)["coefficient"] / item["actual_mu"]
        item["signed_rank_one_baseline_ratio"] = float(baseline)
        item["excess_over_signed_rank_one"] = float(item["ratio"] - baseline)
        score = item["ratio"] if objective == "ratio" else item["excess_over_signed_rank_one"]
        best_score = None if best is None else (
            best["ratio"] if objective == "ratio" else best["excess_over_signed_rank_one"]
        )
        if best is None or score < best_score:
            best = item
            history.append(
                {
                    "evaluation": evaluation,
                    "ratio": item["ratio"],
                    "excess_over_signed_rank_one": item["excess_over_signed_rank_one"],
                    "counts": list(counts),
                }
            )
    return {
        "evidence_level": "E1 float64 stochastic structured search; null result is not proof",
        "family": "three duplicate planar Gram prototypes with unequal multiplicities",
        "seed": seed,
        "n": total,
        "evaluations": evaluations,
        "objective": objective,
        "history": history,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=202608221)
    parser.add_argument("--n", type=int, default=90)
    parser.add_argument("--evaluations", type=int, default=240)
    parser.add_argument("--objective", choices=("ratio", "excess"), default="ratio")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = search(args.seed, args.n, args.evaluations, args.objective)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best": result["best"]}, indent=2))


if __name__ == "__main__":
    main()
