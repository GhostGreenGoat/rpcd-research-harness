"""Targeted E1 attack on the fixed block-length-three Bessel certificate.

The mathematical inequality ``K0 >= K3`` follows from orthogonal projection
(Bessel).  This script tests only the stronger, still-conjectural shortcut
``K3 >= 2 P_ker``.  Float64 nonnegative margins are not proof.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.iter4_adjacency_bessel import (
    boundary_record,
    orders_and_features,
)
from scripts.search_m1_boundary_coefficient import two_pole_ring
from scripts.search_strong_one_epoch_energy import boundary_gram


def block_rank_one(parts: list[int]) -> np.ndarray:
    n = sum(parts)
    correlation = np.zeros((n, n))
    offset = 0
    for size in parts:
        correlation[offset : offset + size, offset : offset + size] = 1.0
        offset += size
    return correlation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=9)
    parser.add_argument("--seed", type=int, default=2026082104)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T080_Q3_ATTACK_N9_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.n != 9:
        raise ValueError("the deterministic case list is currently defined for n=9")
    rng = np.random.default_rng(args.seed)
    started = time.time()
    orders, active, gram_inverse, feature_count = orders_and_features(args.n, 3)
    setup_seconds = time.time() - started
    cases = [
        ("block_J5_plus_J4", block_rank_one([5, 4])),
        ("block_J7_plus_J2", block_rank_one([7, 2])),
        ("block_J3_plus_J3_plus_J3", block_rank_one([3, 3, 3])),
        ("two_pole_ring_latitude_0.88", two_pole_ring(9, 0.88)),
        ("random_rank_2", boundary_gram(9, 2, rng)),
        ("random_rank_3", boundary_gram(9, 3, rng)),
    ]
    records: list[dict[str, object]] = []
    for family, correlation in cases:
        case_started = time.time()
        record = boundary_record(
            correlation,
            family,
            orders,
            active,
            gram_inverse,
            feature_count,
        )
        record["elapsed_seconds"] = time.time() - case_started
        records.append(record)
        checkpoint = {
            "schema_version": "1.0",
            "evidence_level": "E1",
            "warning": "A finite float64 null search is not a proof.",
            "targeted_claim": "K3(C) >= 2 P_ker(C)",
            "seed": args.seed,
            "n": args.n,
            "setup_seconds": setup_seconds,
            "status": "running checkpoint",
            "records": records,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(checkpoint, indent=2) + "\n", encoding="utf-8")
        print(
            family,
            record["min_eigenvalue_projected_minus_2pker"],
            record["min_eigenvalue_exact_minus_2pker"],
            flush=True,
        )
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E1",
        "warning": "A finite float64 null search is not a proof.",
        "targeted_claim": "K3(C) >= 2 P_ker(C)",
        "seed": args.seed,
        "n": args.n,
        "setup_seconds": setup_seconds,
        "elapsed_seconds": time.time() - started,
        "minimum_projected_margin": min(
            float(record["min_eigenvalue_projected_minus_2pker"])
            for record in records
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "minimum": payload["minimum_projected_margin"]}))


if __name__ == "__main__":
    main()
