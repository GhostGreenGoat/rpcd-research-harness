#!/usr/bin/env python3
"""Scout whether the reachable warm inequality is weaker than D>=mu I.

The search minimizes the full-PSD one-epoch coefficient while recording the
reachable two-epoch coefficient on the same matrix.  A matrix with one-epoch
coefficient below one but warm coefficient at least one would demonstrate the
importance of the post-epoch covariance cone.  Float64 output is E1 only.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from attack_warm_start import SEED, search_case


HERE = Path(__file__).resolve().parent
SCOUT_SEED = SEED + 101


def main() -> None:
    generator = np.random.default_rng(SCOUT_SEED)
    cases = [
        (4, 3, 0.70, 8, 600),
        (5, 4, 0.70, 8, 500),
        (5, 4, 0.30, 8, 500),
        (6, 5, 0.70, 5, 260),
        (6, 5, 0.20, 5, 260),
        (7, 6, 0.70, 2, 60),
        (7, 6, 0.20, 2, 60),
    ]
    records = [
        search_case(
            generator,
            n,
            rank,
            mu,
            restarts,
            steps,
            objective_key="one_epoch_c",
        )
        for n, rank, mu, restarts, steps in cases
    ]
    best = min(records, key=lambda item: item["best_diagnostic"]["one_epoch_c"])
    separating = [
        record
        for record in records
        if record["best_diagnostic"]["one_epoch_c"] < 1
        and record["best_diagnostic"]["effective_c"] >= 1
    ]
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "float64 reachable-cone separation scout",
        "evidence_level": "E1",
        "seed": SCOUT_SEED,
        "objective": "minimize lambda_min(A^{-1/2}(A-H1)A^{-1/2})/mu",
        "records": records,
        "global_best": best,
        "potential_reachable_cone_separations": separating,
        "conclusion": (
            "A float64 separation candidate was found and requires exact reconstruction."
            if separating
            else "No separation was found; this null search does not identify the reachable cone with the full PSD cone."
        ),
        "scope": (
            "Even an exact separation would refute only the unit-coefficient full-PSD shortcut, not "
            "the warm inequality, locked block lemma, C051 with some smaller constant, or C050."
        ),
    }
    output_path = HERE / "reachable_cone_attack.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": SCOUT_SEED,
        "cases": len(records),
        "global_best": best,
        "separation_count": len(separating),
        "output": str(output_path),
    }, indent=2))


if __name__ == "__main__":
    main()
