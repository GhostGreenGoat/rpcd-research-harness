"""Search for violations of the strong one-epoch A-energy inequality.

This is a numerical scout, not a proof.  It searches the fixed-sigma slice

    A = I + alpha H,  diag(H)=0,  lambda_min(A)=sigma,

and minimizes

    q(n,sigma) - lambda_max(E[T_pi^T A T_pi], A).

A negative result is only a candidate until certified with exact or interval
arithmetic.  A nonnegative search result is never evidence of a theorem.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from rpcd_harness.rpcd import (
    conjectured_rate_bound,
    correlation_from_offdiagonal_direction,
    exact_one_epoch_energy_rate,
    exact_rpcd_rate,
    matrix_diagnostics,
)


def symmetric_direction(parameters: np.ndarray, n: int) -> np.ndarray:
    matrix = np.zeros((n, n), dtype=np.float64)
    upper = np.triu_indices(n, 1)
    matrix[upper] = parameters
    return matrix + matrix.T


def evaluate(parameters: np.ndarray, n: int, sigma: float) -> dict[str, object]:
    direction = symmetric_direction(parameters, n)
    matrix = correlation_from_offdiagonal_direction(direction, sigma)
    energy_rate = exact_one_epoch_energy_rate(matrix)
    target = conjectured_rate_bound(n, sigma)
    return {
        "margin": float(target - energy_rate),
        "energy_rate": float(energy_rate),
        "target": float(target),
        "matrix": matrix,
        "parameters": parameters,
    }


def search_slice(
    n: int,
    sigma: float,
    trials: int,
    local_steps: int,
    seed: int,
) -> dict[str, object]:
    generator = np.random.default_rng(seed)
    parameter_count = n * (n - 1) // 2
    best: dict[str, object] | None = None

    for _ in range(trials):
        parameters = generator.normal(size=parameter_count)
        candidate = evaluate(parameters, n, sigma)
        if best is None or float(candidate["margin"]) < float(best["margin"]):
            best = candidate

    assert best is not None
    parameters = np.asarray(best["parameters"], dtype=np.float64)
    step = 0.25
    stale = 0
    for _ in range(local_steps):
        proposal = parameters + step * generator.normal(size=parameter_count)
        candidate = evaluate(proposal, n, sigma)
        if float(candidate["margin"]) < float(best["margin"]):
            best = candidate
            parameters = proposal
            stale = 0
        else:
            stale += 1
        if stale >= 25:
            step *= 0.7
            stale = 0

    matrix = np.asarray(best["matrix"], dtype=np.float64)
    diagnostics = matrix_diagnostics(matrix)
    return {
        "dimension": n,
        "sigma_requested": sigma,
        "seed": seed,
        "trials": trials,
        "local_steps": local_steps,
        "minimum_margin": float(best["margin"]),
        "one_epoch_energy_rate": float(best["energy_rate"]),
        "conjectured_rate": float(best["target"]),
        "rpcd_covariance_rate": float(exact_rpcd_rate(matrix)),
        "eigenvalues": np.linalg.eigvalsh(matrix).tolist(),
        "matrix": matrix.tolist(),
        "diagnostics": diagnostics.__dict__,
        "warning": "Numerical scout only; a negative margin requires certification.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dimensions", nargs="+", type=int, default=[3, 4, 5])
    parser.add_argument(
        "--sigmas", nargs="+", type=float, default=[0.02, 0.05, 0.1, 0.2, 0.4, 0.7]
    )
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--local-steps", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = []
    for n in args.dimensions:
        for offset, sigma in enumerate(args.sigmas):
            record = search_slice(
                n=n,
                sigma=sigma,
                trials=args.trials,
                local_steps=args.local_steps,
                seed=args.seed + 1000 * n + offset,
            )
            records.append(record)
            print(
                f"n={n} sigma={sigma:.6g} "
                f"margin={record['minimum_margin']:.9g} "
                f"energy={record['one_epoch_energy_rate']:.9g} "
                f"rho={record['rpcd_covariance_rate']:.9g}"
            )
    payload = {"schema_version": "1.0", "records": records}
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
