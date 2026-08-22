"""E1 attack on the candidate 3/2 boundary constant.

The two-pole/simplex proof uses the smallest ring correlation allowed by PSD.
This script searches the full exchangeable-ring PSD interval

    rho >= (k*a^2-1)/(k-1)

to test whether moving into the interior lowers the pole-difference
coefficient below the boundary family or below 3/2.  A null result is not a
proof of either monotonicity or the 3/2 conjecture.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


def coefficient(k: int, a: float, rho: float) -> float:
    q = 1.0 - rho
    denominator = 1.0 - q * q
    if abs(rho) < 1e-12 or abs(denominator) < 1e-12:
        return math.inf
    compositions = (k + 1) * (k + 2) / 2.0
    total = 0.0
    for middle in range(k + 1):
        q_middle = q**middle
        multiplicity = k - middle + 1
        base = (
            1.0
            + a * a * (1.0 - q_middle * q_middle) / denominator
            + (-2.0 + a * a * (1.0 - q_middle) / rho) ** 2
        )
        after_amplitude = a * (
            2.0 - q_middle - a * a * (1.0 - q_middle) / rho
        )
        last = k - middle
        summed_after_tail = (
            (last + 1)
            - (1.0 - q ** (2 * (last + 1))) / denominator
        ) / denominator
        total += multiplicity * base + after_amplitude**2 * summed_after_tail
    return total / (2.0 * compositions)


def run(seed: int, samples: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    started = time.time()
    records = []
    for k in (6, 10, 20, 50, 100, 200, 500, 1000):
        best = {"coefficient": math.inf}
        random_samples = samples if k < 100 else max(1000, samples // 3)
        for _ in range(random_samples):
            a = float(rng.uniform(0.005, 0.999))
            lower = (k * a * a - 1.0) / (k - 1.0)
            rho = float(lower + (1.0 - lower) * rng.beta(0.55, 2.0))
            value = coefficient(k, a, rho)
            if value < float(best["coefficient"]):
                best = {
                    "coefficient": value,
                    "a": a,
                    "rho": rho,
                    "rho_minus_psd_boundary": rho - lower,
                    "source": "interior_random",
                }
        lower_a = max(0.003, 1.01 / math.sqrt(k))
        for a_value in np.geomspace(lower_a, 0.99, 300):
            a = float(a_value)
            rho = (k * a * a - 1.0) / (k - 1.0)
            value = coefficient(k, a, rho)
            if value < float(best["coefficient"]):
                best = {
                    "coefficient": value,
                    "a": a,
                    "rho": rho,
                    "rho_minus_psd_boundary": 0.0,
                    "source": "psd_boundary_grid",
                }
        best["k"] = k
        best["n"] = k + 2
        best["gap_above_three_halves"] = float(best["coefficient"]) - 1.5
        records.append(best)
    return {
        "schema_version": "1.0",
        "evidence_level": "E1",
        "status": "finite float64 hostile search; no violation is not a proof",
        "candidate": "K0(C) >= (3/2) P_ker(C)",
        "family": "two identical poles plus an exchangeable k-point ring over its full PSD interval",
        "seed": seed,
        "random_samples_small_k": samples,
        "records": records,
        "minimum_observed": min(float(record["coefficient"]) for record in records),
        "all_minimizers_on_sampled_psd_boundary": all(
            record["source"] == "psd_boundary_grid" for record in records
        ),
        "scope_warning": (
            "This search neither proves ring-interior monotonicity nor the 3/2 lower bound, "
            "and it covers only an exchangeable family."
        ),
        "elapsed_seconds": time.time() - started,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=2026082112)
    parser.add_argument("--samples", type=int, default=12000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T095_EXCHANGEABLE_INTERIOR_ATTACK_2026_08_21.json"
        ),
    )
    args = parser.parse_args()
    payload = run(args.seed, args.samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "minimum": payload["minimum_observed"]}))


if __name__ == "__main__":
    main()
