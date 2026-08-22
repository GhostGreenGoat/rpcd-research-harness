"""Large-n attack with a rank-two duplicate satellite block.

One group contains ``n-s`` copies of a vector ``p`` and the second contains
``s`` copies of a vector at angle ``theta`` from ``p``.  The boundary Gram
matrix has rank at most two and nullity ``n-2``.  A two-count Bellman state
makes searches through n=1000 inexpensive.  Results are E1 float64 evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, evaluate_family


def signed_baseline(n: int, mu: float) -> float:
    dp = ExchangeableTailDP((n,), (1.0 - mu,), np.zeros((1, 1)))
    return dp.coefficient((n + 1) // 2)["coefficient"] / mu


def search(
    seed: int,
    n: int,
    evaluations: int,
    max_satellite: int | None,
    high_mu_only: bool,
    two_scale: bool,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    best_ratio = None
    best_excess = None
    sector_counts: dict[str, int] = {}
    started = time.time()
    for evaluation in range(evaluations):
        if evaluation == 0:
            satellite = max(2, n // 10)
            angle = 0.0
            mu = 1.0 - 2.0 / math.sqrt(n)
        else:
            # Log-uniform satellite sizes stress both a vanishing exceptional
            # block and a macroscopic second block.
            satellite_cap = min(n / 2, max_satellite or n / 2)
            satellite = int(round(math.exp(rng.uniform(math.log(2), math.log(satellite_cap)))))
            satellite = min(max(2, satellite), n - 2)
            if rng.random() < 0.7:
                angle = float(rng.beta(0.6, 2.5) * math.pi)
            else:
                angle = float(rng.uniform(0.0, math.pi))
            if high_mu_only or rng.random() < 0.8:
                mu = float(1.0 - 10.0 ** rng.uniform(-3.5, -0.25))
            else:
                mu = float(10.0 ** rng.uniform(-4.0, -0.05))
        counts = (n - satellite, satellite)
        directions = np.array([[1.0, 0.0], [math.cos(angle), math.sin(angle)]])
        satellite_mass = (
            float(np.clip(rng.beta(0.55, 0.55), 1e-4, 0.9999))
            if two_scale and evaluation > 0
            else 1.0
        )
        item = evaluate_family(
            "two_group_satellite",
            counts,
            directions,
            (1.0, satellite_mass),
            mu,
            {
                "evaluation": evaluation,
                "angle": angle,
                "satellite": satellite,
                "satellite_mass_fraction": satellite_mass,
            },
        )
        baseline = signed_baseline(n, item["actual_mu"])
        item["signed_rank_one_baseline_ratio"] = baseline
        item["excess_over_signed_rank_one"] = item["ratio"] - baseline
        sector = item["result"]["sector"]
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
        if best_ratio is None or item["ratio"] < best_ratio["ratio"]:
            best_ratio = item
        if best_excess is None or item["excess_over_signed_rank_one"] < best_excess["excess_over_signed_rank_one"]:
            best_excess = item
    return {
        "evidence_level": "E1 float64 stochastic structured search; null result is not proof",
        "family": "rank-two Gram matrix with a large duplicate group and a duplicate satellite group",
        "seed": seed,
        "n": n,
        "evaluations": evaluations,
        "max_satellite": max_satellite,
        "high_mu_only": high_mu_only,
        "two_scale": two_scale,
        "sector_counts": sector_counts,
        "best_ratio": best_ratio,
        "best_excess": best_excess,
        "violation_found_float64": bool(best_ratio["margin_over_half"] < -1e-8),
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=202608223)
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--evaluations", type=int, default=1200)
    parser.add_argument("--max-satellite", type=int)
    parser.add_argument("--high-mu-only", action="store_true")
    parser.add_argument("--two-scale", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = search(
        args.seed,
        args.n,
        args.evaluations,
        args.max_satellite,
        args.high_mu_only,
        args.two_scale,
    )
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "best_ratio": result["best_ratio"],
                "best_excess": result["best_excess"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
