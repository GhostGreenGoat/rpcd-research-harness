"""Search the exact first-order small-mu boundary coefficient for M1.

For a singular correlation matrix C, this script computes

    c(C) = lambda_min(K_NN - K_NR K_RR^{-1} K_RN),

where K=E[(M_pi(C) M_pi(C)^T)^{-1}] and N=ker(C).  The M1 target has
first-order coefficient 2.  Thus c(C)<2 would be an E1 candidate for a
small-mu counterexample; c(C)>=2 in a finite search is not a proof.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from scripts.search_strong_one_epoch_energy import (
    boundary_gram,
    circle_gram,
    cut_mixture_gram,
    normalize_rows,
)


def remaining_set_k_dp(c: np.ndarray) -> np.ndarray:
    """Compute E[(M_pi M_pi^T)^-1] using the residual subset recursion."""
    n = c.shape[0]
    values: list[np.ndarray | None] = [None] * (1 << n)
    values[0] = np.zeros((0, 0))
    for mask in range(1, 1 << n):
        indices = [i for i in range(n) if mask & (1 << i)]
        b = c[np.ix_(indices, indices)]
        m = len(indices)
        total = np.zeros((m, m))
        for position, index in enumerate(indices):
            submask = mask ^ (1 << index)
            subk = values[submask]
            assert subk is not None
            immediate = np.zeros((m, m))
            immediate[position, position] = 1.0
            keep = [j for j in range(m) if j != position]
            selector = np.eye(m)[keep, :]
            e = np.eye(m)[:, position]
            transition = selector @ (np.eye(m) - np.outer(b[:, position], e))
            total += immediate + transition.T @ subk @ transition
        values[mask] = total / m
    result = values[-1]
    assert result is not None
    return (result + result.T) / 2.0


def boundary_coefficient(c: np.ndarray, eig_tolerance: float = 1e-8) -> dict[str, object]:
    values, vectors = np.linalg.eigh((c + c.T) / 2.0)
    null = vectors[:, values < eig_tolerance]
    image = vectors[:, values >= eig_tolerance]
    if null.shape[1] == 0 or image.shape[1] == 0:
        raise ValueError("C must be singular and nonzero")
    k = remaining_set_k_dp(c)
    k_nn = null.T @ k @ null
    k_nr = null.T @ k @ image
    k_rr = image.T @ k @ image
    schur = k_nn - k_nr @ np.linalg.solve(k_rr, k_nr.T)
    coefficient = float(np.linalg.eigvalsh((schur + schur.T) / 2.0)[0])
    return {
        "n": int(c.shape[0]),
        "rank": int(image.shape[1]),
        "nullity": int(null.shape[1]),
        "coefficient": coefficient,
        "gap_coefficient_minus_2": coefficient - 2.0,
        "eigenvalues": values.tolist(),
        "correlation": c.tolist(),
    }


def two_pole_ring(n: int, latitude: float) -> np.ndarray:
    if n < 4:
        raise ValueError("two-pole ring requires n>=4")
    count = n - 2
    vectors = np.zeros((n, 3))
    vectors[:2, 2] = 1.0
    radius = np.sqrt(1.0 - latitude * latitude)
    for j in range(count):
        angle = 2.0 * np.pi * j / count
        vectors[2 + j] = [radius * np.cos(angle), radius * np.sin(angle), latitude]
    return vectors @ vectors.T


def gram_vectors(c: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((c + c.T) / 2.0)
    positive = values > 1e-8
    return normalize_rows(vectors[:, positive] * np.sqrt(values[positive]))


def greedy_refine(
    vectors: np.ndarray,
    rng: np.random.Generator,
    scales: list[float],
    attempts: int,
) -> tuple[np.ndarray, dict[str, object], list[dict[str, object]]]:
    current = boundary_coefficient(vectors @ vectors.T)
    trace: list[dict[str, object]] = []
    for scale in scales:
        accepted = 0
        for _ in range(attempts):
            candidate = vectors.copy()
            row = int(rng.integers(candidate.shape[0]))
            direction = rng.normal(size=candidate.shape[1])
            direction -= np.dot(direction, candidate[row]) * candidate[row]
            norm = np.linalg.norm(direction)
            if norm < 1e-14:
                continue
            candidate[row] += scale * direction / norm
            candidate[row] /= np.linalg.norm(candidate[row])
            record = boundary_coefficient(candidate @ candidate.T)
            if float(record["coefficient"]) < float(current["coefficient"]):
                vectors = candidate
                current = record
                accepted += 1
        trace.append({"scale": scale, "accepted": accepted, "coefficient": current["coefficient"]})
    return vectors, current, trace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260826)
    parser.add_argument("--n-min", type=int, default=3)
    parser.add_argument("--n-max", type=int, default=8)
    parser.add_argument("--samples", type=int, default=300)
    parser.add_argument("--local-attempts", type=int, default=500)
    parser.add_argument("--scales", default="0.25,0.1,0.03,0.01,0.003")
    parser.add_argument("--keep", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/M1_BOUNDARY_COEFFICIENT_SEARCH_2026_08_21.json"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    started = time.time()
    global_best: list[dict[str, object]] = []
    dimension_best: dict[str, dict[str, object]] = {}
    traces: dict[str, list[dict[str, object]]] = {}
    evaluations = [0]

    def consider(record: dict[str, object], family: str) -> None:
        record["family"] = family
        evaluations[0] += 1
        global_best.append(record)
        global_best.sort(key=lambda item: float(item["coefficient"]))
        del global_best[args.keep:]
        key = str(record["n"])
        if key not in dimension_best or float(record["coefficient"]) < float(
            dimension_best[key]["coefficient"]
        ):
            dimension_best[key] = record

    for n in range(args.n_min, args.n_max + 1):
        for _ in range(args.samples):
            rank = int(rng.integers(1, n))
            consider(boundary_coefficient(boundary_gram(n, rank, rng)), f"boundary_gram_r{rank}")
            if n >= 3:
                consider(boundary_coefficient(circle_gram(n, rng)), "frustrated_circle_r2")
            components = int(rng.integers(1, n))
            consider(
                boundary_coefficient(cut_mixture_gram(n, components, rng)),
                f"cut_mixture_m{components}",
            )
        if n >= 4:
            for latitude in np.linspace(0.1, 0.99, 80):
                consider(boundary_coefficient(two_pole_ring(n, float(latitude))), "two_pole_ring")

        seed_record = dimension_best[str(n)]
        vectors = gram_vectors(np.asarray(seed_record["correlation"], dtype=float))
        vectors, local, trace = greedy_refine(
            vectors,
            rng,
            [float(value) for value in args.scales.split(",")],
            args.local_attempts,
        )
        local["vectors"] = vectors.tolist()
        consider(local, "local_boundary_gram")
        evaluations[0] += len(trace) * args.local_attempts
        traces[str(n)] = trace

    payload = {
        "status": "E1 small-mu coefficient search; nonnegative finite gaps are not a proof",
        "formula": "c(C)=lambda_min(K_NN-K_NR K_RR^{-1} K_RN); M1 needs c(C)>=2",
        "seed": args.seed,
        "n_range": [args.n_min, args.n_max],
        "samples_per_dimension": args.samples,
        "local_attempts_per_scale": args.local_attempts,
        "evaluations_counting_local_attempts": evaluations[0],
        "elapsed_seconds": time.time() - started,
        "best": global_best,
        "dimension_best": dimension_best,
        "local_traces": traces,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "evaluations": evaluations[0],
        "elapsed_seconds": payload["elapsed_seconds"],
        "best_coefficient": global_best[0]["coefficient"],
        "gap_to_2": global_best[0]["gap_coefficient_minus_2"],
        "best_n": global_best[0]["n"],
        "best_family": global_best[0]["family"],
    }, indent=2))
