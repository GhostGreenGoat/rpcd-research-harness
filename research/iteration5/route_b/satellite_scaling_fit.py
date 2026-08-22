"""Empirical asymptotic fits for fixed/sublinear/linear satellite counts.

At each n this minimizes over a small cosine grid on the boundary layer
1-mu = 2.5 log(n)/n, then fits the positive margin over 1/2.  This is E1
numerical evidence only; slopes from five dimensions are diagnostics, not
asymptotic theorems.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, evaluate_family
from satellite_scale_regimes import satellite_count


HERE = Path(__file__).resolve().parent


def signed_baseline(n: int, mu: float) -> float:
    dp = ExchangeableTailDP((n,), (1.0 - mu,), np.zeros((1, 1)))
    return dp.coefficient((n + 1) // 2)["coefficient"] / mu


def fit_positive(records: list[dict[str, object]]) -> dict[str, float]:
    tail = records[-3:]
    x = np.log(np.array([float(r["n"]) for r in tail]))
    y = np.log(np.array([float(r["margin_over_half"]) for r in tail]))
    slope, intercept = np.polyfit(x, y, 1)
    scales = np.array([
        float(r["margin_over_half"]) * float(r["n"]) / math.log(float(r["n"]))
        for r in tail
    ])
    return {
        "last_three_loglog_slope_vs_n": float(slope),
        "last_three_loglog_intercept": float(intercept),
        "last_three_mean_n_margin_over_log_n": float(np.mean(scales)),
        "last_three_range_n_margin_over_log_n": float(np.ptp(scales)),
    }


def main() -> None:
    started = time.time()
    dimensions = (100, 200, 400, 800, 1600)
    cosine_grid = (0.0, 0.6, 0.95, 0.995)
    regimes: dict[str, list[dict[str, object]]] = {}
    for regime in ("fixed_2", "sqrt_n", "n_to_3_over_4", "linear_quarter"):
        best_by_n: list[dict[str, object]] = []
        for n in dimensions:
            k = satellite_count(n, regime)
            mu = 1.0 - 2.5 * math.log(n) / n
            baseline = signed_baseline(n, mu)
            candidates: list[dict[str, object]] = []
            for cosine in cosine_grid:
                directions = np.array([
                    [1.0, 0.0],
                    [cosine, math.sqrt(max(0.0, 1.0 - cosine * cosine))],
                ])
                item = evaluate_family(
                    "two_group_satellite_scaling_fit",
                    (n - k, k), directions, (1.0, 1.0), mu,
                    {"regime": regime, "cosine": cosine},
                )
                candidates.append({
                    "n": n,
                    "k": k,
                    "k_over_n": k / n,
                    "mu": mu,
                    "cosine": cosine,
                    "ratio": item["ratio"],
                    "margin_over_half": item["margin_over_half"],
                    "n_margin_over_log_n": item["margin_over_half"] * n / math.log(n),
                    "signed_rank_one_baseline_ratio": baseline,
                    "excess_over_signed_rank_one": item["ratio"] - baseline,
                    "sector": item["result"]["sector"],
                    "states_evaluated": item["result"]["states_evaluated"],
                })
            best_by_n.append(min(candidates, key=lambda r: r["ratio"]))
        regimes[regime] = best_by_n
    result = {
        "evidence_level": (
            "E1 float64 diagnostic fit on five finite dimensions and a four-point "
            "cosine grid; this is not an asymptotic proof"
        ),
        "boundary_layer": "1-mu=2.5*log(n)/n",
        "dimensions": list(dimensions),
        "cosine_grid": list(cosine_grid),
        "regimes": {
            name: {"best_by_n": values, "fit": fit_positive(values)}
            for name, values in regimes.items()
        },
        "violation_found_float64": any(
            row["margin_over_half"] < -1e-8
            for values in regimes.values() for row in values
        ),
        "elapsed_seconds": time.time() - started,
    }
    (HERE / "satellite_scaling_fit.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
