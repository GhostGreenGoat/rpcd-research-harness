"""Targeted large-n threshold scan for a two-coordinate satellite.

The floor is parameterized as ``1-mu = c log(n)/n`` to balance the vanishing
determinant leaf against the positive fixed-satellite asymptotic margin.  Both
H_half and the bare prefix J_half are evaluated.  Results are E1 float64.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from reproducer import ExchangeableTailDP, evaluate_family


def scan(dimensions: list[int]) -> dict[str, object]:
    c_values = np.linspace(1.4, 4.2, 15)
    t_values = np.linspace(0.0, 0.8, 9)
    records = []
    started = time.time()
    for n in dimensions:
        best_h = None
        best_j = None
        for c in c_values:
            alpha = float(c * math.log(n) / n)
            if alpha >= 0.95:
                continue
            mu = 1.0 - alpha
            for t in t_values:
                directions = np.array([[1.0, 0.0], [t, math.sqrt(1.0 - t * t)]])
                h_item = evaluate_family(
                    "two_satellite_threshold",
                    (n - 2, 2),
                    directions,
                    (1.0, 1.0),
                    mu,
                    {"c": float(c), "t": float(t)},
                )
                j_dp = ExchangeableTailDP(
                    (n - 2, 2),
                    np.asarray(h_item["within"]),
                    np.asarray(h_item["cross"]),
                    "zero",
                )
                j_result = j_dp.coefficient((n + 1) // 2)
                j_ratio = j_result["coefficient"] / h_item["actual_mu"]
                compact = {
                    "n": n,
                    "c": float(c),
                    "t": float(t),
                    "mu": h_item["actual_mu"],
                    "H_ratio": h_item["ratio"],
                    "H_margin": h_item["margin_over_half"],
                    "H_sector": h_item["result"]["sector"],
                    "J_ratio": float(j_ratio),
                    "J_margin": float(j_ratio - 0.5),
                    "J_sector": j_result["sector"],
                    "states_H": h_item["result"]["states_evaluated"],
                    "states_J": j_result["states_evaluated"],
                }
                if best_h is None or compact["H_ratio"] < best_h["H_ratio"]:
                    best_h = compact
                if best_j is None or compact["J_ratio"] < best_j["J_ratio"]:
                    best_j = compact
        records.append({"n": n, "best_H": best_h, "best_J": best_j})
    return {
        "evidence_level": "E1 float64 targeted threshold scan; no finite grid is a proof",
        "family": "two-coordinate orthogonal/oblique satellite",
        "parameterization": "1-mu=c log(n)/n",
        "c_values": c_values.tolist(),
        "t_values": t_values.tolist(),
        "records": records,
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimensions", default="1000,3000,10000,30000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dimensions = [int(value) for value in args.dimensions.split(",")]
    result = scan(dimensions)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "records": result["records"]}, indent=2))


if __name__ == "__main__":
    main()
