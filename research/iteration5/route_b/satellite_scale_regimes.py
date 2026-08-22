"""Hostile count-scaling scan for the two-direction satellite family.

This separates fixed, growing sublinear, and linear satellite populations.
All results are E1 float64 evidence.  In particular, absence of a violation
on the finite grid is not a proof for any scaling regime.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, evaluate_family


HERE = Path(__file__).resolve().parent


def signed_baseline(n: int, mu: float) -> float:
    dp = ExchangeableTailDP((n,), (1.0 - mu,), np.zeros((1, 1)))
    return dp.coefficient((n + 1) // 2)["coefficient"] / mu


def satellite_count(n: int, regime: str) -> int:
    if regime == "fixed_2":
        return 2
    if regime == "sqrt_n":
        return max(2, int(round(math.sqrt(n))))
    if regime == "n_to_3_over_4":
        return max(2, int(round(n ** 0.75)))
    if regime == "linear_quarter":
        return n // 4
    raise ValueError(regime)


def main() -> None:
    started = time.time()
    cases = {
        "fixed_2": (100, 300, 1000),
        "sqrt_n": (100, 300, 1000),
        "n_to_3_over_4": (100, 300, 600),
        "linear_quarter": (100, 300, 600),
    }
    cosine_grid = (0.0, 0.6, 0.95)
    records: list[dict[str, object]] = []
    summaries: dict[str, object] = {}
    for regime, dimensions in cases.items():
        regime_records: list[dict[str, object]] = []
        for n in dimensions:
            k = satellite_count(n, regime)
            # The threshold value probes the empirically tight boundary layer
            # 1-mu = Theta(log(n)/n), while 0.5 and 0.9 are hostile interiors.
            threshold_mu = max(0.05, 1.0 - 2.5 * math.log(n) / n)
            for mu in (0.5, 0.9, threshold_mu):
                baseline = signed_baseline(n, mu)
                for cosine in cosine_grid:
                    sine = math.sqrt(max(0.0, 1.0 - cosine * cosine))
                    item = evaluate_family(
                        "two_group_satellite_scale_regime",
                        (n - k, k),
                        np.array([[1.0, 0.0], [cosine, sine]]),
                        (1.0, 1.0),
                        mu,
                        {
                            "regime": regime,
                            "satellite_count": k,
                            "satellite_fraction": k / n,
                            "cosine": cosine,
                        },
                    )
                    record = {
                        "regime": regime,
                        "n": n,
                        "k": k,
                        "k_over_n": k / n,
                        "mu": mu,
                        "cosine": cosine,
                        "ratio": item["ratio"],
                        "margin_over_half": item["margin_over_half"],
                        "signed_rank_one_baseline_ratio": baseline,
                        "excess_over_signed_rank_one": item["ratio"] - baseline,
                        "sector": item["result"]["sector"],
                        "states_evaluated": item["result"]["states_evaluated"],
                        "leaf_underflows": item["result"]["leaf_underflows"],
                    }
                    records.append(record)
                    regime_records.append(record)
        summaries[regime] = {
            "dimensions": list(dimensions),
            "evaluations": len(regime_records),
            "closest_to_half": min(regime_records, key=lambda r: r["ratio"]),
            "most_below_signed_baseline": min(
                regime_records, key=lambda r: r["excess_over_signed_rank_one"]
            ),
        }
    result = {
        "evidence_level": (
            "E1 deterministic float64 finite-grid structured search; a null result "
            "does not prove any fixed, sublinear, or linear asymptotic claim"
        ),
        "family": "two duplicate direction groups, A=mu*I+(1-mu)*Gram",
        "cosine_grid": list(cosine_grid),
        "mu_grid_rule": ["0.5", "0.9", "1-2.5*log(n)/n"],
        "total_evaluations": len(records),
        "violation_found_float64": any(r["margin_over_half"] < -1e-8 for r in records),
        "global_closest_to_half": min(records, key=lambda r: r["ratio"]),
        "global_most_below_signed_baseline": min(
            records, key=lambda r: r["excess_over_signed_rank_one"]
        ),
        "regime_summaries": summaries,
        "records": records,
        "elapsed_seconds": time.time() - started,
    }
    output = HERE / "satellite_scale_regimes.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "total_evaluations", "violation_found_float64",
        "global_closest_to_half", "global_most_below_signed_baseline",
        "regime_summaries", "elapsed_seconds"
    )}, indent=2))


if __name__ == "__main__":
    main()
