#!/usr/bin/env python3
"""Reproducible small-n search for RPCD counterexample candidates.

The script follows the ICML paper's correlation-matrix parameterization, then
affinely fixes lambda_min(A)=sigma.  It exhaustively averages all permutations
for every sampled matrix.  A negative float64 margin is only a candidate and
must be independently recertified at higher precision.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rpcd_harness.rpcd import (
    matrix_record,
    random_correlation,
    set_minimum_eigenvalue,
    structured_hessian,
)


def block_correlation(n: int, seed: int) -> np.ndarray:
    generator = np.random.default_rng(seed)
    split = max(1, n // 2)
    blocks = []
    for size in (split, n - split):
        if size == 0:
            continue
        x = generator.normal(size=(size, size))
        gram = x.T @ x + 0.05 * np.eye(size)
        diagonal = np.sqrt(np.diag(gram))
        blocks.append(gram / np.outer(diagonal, diagonal))
    output = np.zeros((n, n))
    cursor = 0
    for block in blocks:
        size = block.shape[0]
        output[cursor : cursor + size, cursor : cursor + size] = block
        cursor += size
    return output


def candidate_matrices(n: int, sigma: float, samples: int, seed: int):
    yield "structured", seed, structured_hessian(n, sigma)
    generator = np.random.default_rng(seed)
    for index in range(samples):
        local_seed = int(generator.integers(0, 2**31 - 1))
        ridge = 10.0 ** float(generator.uniform(-3.0, 0.0))
        correlation = random_correlation(n, local_seed, ridge=ridge)
        yield "random-correlation", local_seed, set_minimum_eigenvalue(correlation, sigma)
        if index % 4 == 0:
            block_seed = local_seed ^ 0x5A5A5A5A
            yield "block", block_seed, set_minimum_eigenvalue(
                block_correlation(n, block_seed), sigma
            )


def run_search(n: int, sigma: float, samples: int, seed: int, tolerance: float) -> dict[str, object]:
    if n > 7:
        raise ValueError("n! enumeration is capped at n=7")
    records = []
    best_conjecture = None
    best_jensen = None
    worst_jensen_route = None
    for family, local_seed, matrix in candidate_matrices(n, sigma, samples, seed):
        record = matrix_record(matrix, max_dimension=7)
        record["family"] = family
        record["seed"] = local_seed
        records.append(record)
        if best_conjecture is None or record["conjecture_margin"] < best_conjecture["conjecture_margin"]:
            best_conjecture = record
        if best_jensen is None or record["matrix_jensen_margin"] < best_jensen["matrix_jensen_margin"]:
            best_jensen = record
        if (
            worst_jensen_route is None
            or record["jensen_to_conjecture_margin"] < worst_jensen_route["jensen_to_conjecture_margin"]
        ):
            worst_jensen_route = record

    violations = [
        {
            "family": record["family"],
            "seed": record["seed"],
            "target": target,
            "margin": record[margin_key],
            "matrix": record["matrix"],
            "eigenvalues": record["eigenvalues"],
        }
        for record in records
        for target, margin_key in (
            ("C001", "conjecture_margin"),
            ("C010", "matrix_jensen_margin"),
        )
        if record[margin_key] < -tolerance
    ]
    return {
        "schema_version": "1.0",
        "kind": "counterexample-search",
        "evidence_ceiling": "E2",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "parameters": {"n": n, "sigma": sigma, "samples": samples, "seed": seed, "tolerance": tolerance},
        "evaluated_matrices": len(records),
        "all_permutations_per_matrix": True,
        "best_c001_margin": best_conjecture,
        "best_c010_margin": best_jensen,
        "worst_raw_jensen_to_c001_margin": worst_jensen_route,
        "raw_jensen_route_blocked": worst_jensen_route["jensen_to_conjecture_margin"] < -tolerance,
        "potential_violations": violations,
        "conclusion": (
            "Potential float64 counterexample candidates require independent high-precision certification."
            if violations
            else "No candidate found in this finite search; this is not a proof."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--sigma", type=float, default=0.4)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--tolerance", type=float, default=2e-9)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run_search(args.n, args.sigma, args.samples, args.seed, args.tolerance)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
