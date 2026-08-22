"""Search for violations of the strong one-epoch RPCD energy inequality.

This is an E1 numerical search, not a proof.  It evaluates

    lambda_max(A^{-1/2} E_pi[T_pi^T A T_pi] A^{-1/2})
      <= max((1-1/n)^n, (1-lambda_min(A)/n)^(2n))

using a subset Bellman recursion (2^n states) rather than n! enumeration.
Every generated matrix has unit diagonal and is checked for positive
definiteness.  The low-rank Gram families hit the boundary of the elliptope
before adding ``mu I``, and include frustrated and cut-mixture geometries.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np


def coordinate_updates(a: np.ndarray) -> list[np.ndarray]:
    updates: list[np.ndarray] = []
    for i in range(a.shape[0]):
        u = np.eye(a.shape[0])
        u[i, :] -= a[i, :]
        updates.append(u)
    return updates


def expected_epoch_energy_dp(a: np.ndarray) -> np.ndarray:
    """Return E[T_pi^T A T_pi] via exact subset dynamic programming."""
    n = a.shape[0]
    updates = coordinate_updates(a)
    values: list[np.ndarray | None] = [None] * (1 << n)
    values[0] = a.copy()
    for mask in range(1, 1 << n):
        total = np.zeros_like(a)
        count = mask.bit_count()
        bits = mask
        while bits:
            low = bits & -bits
            i = low.bit_length() - 1
            suffix = values[mask ^ low]
            assert suffix is not None
            total += updates[i].T @ suffix @ updates[i]
            bits ^= low
        values[mask] = total / count
    result = values[-1]
    assert result is not None
    return (result + result.T) / 2.0


def generalized_max(a: np.ndarray, b: np.ndarray) -> float:
    eigenvalues, eigenvectors = np.linalg.eigh(a)
    inverse_sqrt = (eigenvectors * (1.0 / np.sqrt(eigenvalues))) @ eigenvectors.T
    scaled = inverse_sqrt @ b @ inverse_sqrt
    return float(np.linalg.eigvalsh((scaled + scaled.T) / 2.0)[-1])


def target(n: int, mu: float) -> float:
    return max((1.0 - 1.0 / n) ** n, (1.0 - mu / n) ** (2 * n))


def normalize_rows(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1)
    if float(np.min(norms)) < 1e-14:
        raise ValueError("zero row")
    return x / norms[:, None]


def boundary_gram(n: int, rank: int, rng: np.random.Generator) -> np.ndarray:
    vectors = normalize_rows(rng.normal(size=(n, rank)))
    return vectors @ vectors.T


def circle_gram(n: int, rng: np.random.Generator) -> np.ndarray:
    """Rank-two frustrated cycle/elliptope boundary sample."""
    base = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    angles = base + rng.normal(scale=0.55, size=n)
    vectors = np.column_stack((np.cos(angles), np.sin(angles)))
    signs = rng.choice(np.array([-1.0, 1.0]), size=n)
    vectors *= signs[:, None]
    return vectors @ vectors.T


def cut_mixture_gram(n: int, components: int, rng: np.random.Generator) -> np.ndarray:
    signs = rng.choice(np.array([-1.0, 1.0]), size=(components, n))
    weights = rng.dirichlet(np.full(components, 0.35))
    return (signs.T * weights) @ signs


def lifted(correlation: np.ndarray, mu: float) -> np.ndarray:
    n = correlation.shape[0]
    return mu * np.eye(n) + (1.0 - mu) * correlation


def evaluate(a: np.ndarray) -> dict[str, object]:
    eigenvalues = np.linalg.eigvalsh((a + a.T) / 2.0)
    mu = float(eigenvalues[0])
    energy = expected_epoch_energy_dp(a)
    rate = generalized_max(a, energy)
    q = target(a.shape[0], mu)
    return {
        "n": int(a.shape[0]),
        "mu": mu,
        "lambda_max": float(eigenvalues[-1]),
        "energy_rate": rate,
        "target": q,
        "gap_rate_minus_target": rate - q,
        "matrix": a.tolist(),
    }


def retain(best: list[dict[str, object]], record: dict[str, object], limit: int) -> None:
    best.append(record)
    best.sort(key=lambda item: float(item["gap_rate_minus_target"]), reverse=True)
    del best[limit:]


def local_search_vectors(
    vectors: np.ndarray,
    mu: float,
    rng: np.random.Generator,
    steps: int,
) -> tuple[np.ndarray, dict[str, object]]:
    vectors = normalize_rows(vectors.copy())
    current_a = lifted(vectors @ vectors.T, mu)
    current = evaluate(current_a)
    scale = 0.3
    for step in range(steps):
        candidate = vectors.copy()
        row = int(rng.integers(candidate.shape[0]))
        candidate[row] += rng.normal(scale=scale, size=candidate.shape[1])
        candidate[row] /= np.linalg.norm(candidate[row])
        record = evaluate(lifted(candidate @ candidate.T, mu))
        delta = float(record["gap_rate_minus_target"]) - float(
            current["gap_rate_minus_target"]
        )
        temperature = 0.01 * (1.0 - step / max(steps, 1))
        if delta >= 0.0 or rng.random() < math.exp(delta / max(temperature, 1e-8)):
            vectors = candidate
            current = record
        scale *= 0.999
    return vectors, current


def run(args: argparse.Namespace) -> dict[str, object]:
    rng = np.random.default_rng(args.seed)
    mus = [float(value) for value in args.mus.split(",")]
    best: list[dict[str, object]] = []
    family_best: dict[str, dict[str, object]] = {}
    evaluated = 0
    started = time.time()

    def add(family: str, a: np.ndarray) -> None:
        nonlocal evaluated
        record = evaluate(a)
        record["family"] = family
        evaluated += 1
        retain(best, record, args.keep)
        previous = family_best.get(family)
        if previous is None or float(record["gap_rate_minus_target"]) > float(
            previous["gap_rate_minus_target"]
        ):
            family_best[family] = record

    for n in range(args.n_min, args.n_max + 1):
        for mu in mus:
            # Published structured extremal candidate, with arbitrary signing.
            signs = rng.choice(np.array([-1.0, 1.0]), size=n)
            add("signed_rank_one", lifted(np.outer(signs, signs), mu))

            for _ in range(args.samples):
                max_rank = max(1, n - 1)
                rank = int(rng.integers(1, max_rank + 1))
                add(f"boundary_gram_r{rank}", lifted(boundary_gram(n, rank, rng), mu))

                if n >= 3:
                    add("frustrated_circle_r2", lifted(circle_gram(n, rng), mu))

                components = int(rng.integers(1, max_rank + 1))
                add(
                    f"cut_mixture_m{components}",
                    lifted(cut_mixture_gram(n, components, rng), mu),
                )

            # Refine the strongest low-rank Gram candidate at each (n,mu).
            seeds = [
                item
                for item in best
                if int(item["n"]) == n and abs(float(item["mu"]) - mu) < 5e-9
            ]
            if seeds and args.local_steps > 0:
                seed_matrix = np.asarray(seeds[0]["matrix"], dtype=float)
                c = (seed_matrix - mu * np.eye(n)) / (1.0 - mu)
                evals, evecs = np.linalg.eigh((c + c.T) / 2.0)
                positive = evals > 1e-9
                vectors = evecs[:, positive] * np.sqrt(evals[positive])
                if 0 < vectors.shape[1] < n:
                    _, local = local_search_vectors(vectors, mu, rng, args.local_steps)
                    local["family"] = "local_boundary_gram"
                    evaluated += args.local_steps + 1
                    retain(best, local, args.keep)
                    previous = family_best.get("local_boundary_gram")
                    if previous is None or float(local["gap_rate_minus_target"]) > float(
                        previous["gap_rate_minus_target"]
                    ):
                        family_best["local_boundary_gram"] = local

    return {
        "status": "E1 numerical search; a nonpositive best gap is not a proof",
        "seed": args.seed,
        "n_range": [args.n_min, args.n_max],
        "mus": mus,
        "samples_per_n_mu": args.samples,
        "local_steps_per_n_mu": args.local_steps,
        "evaluations_counting_local_steps": evaluated,
        "elapsed_seconds": time.time() - started,
        "best": best,
        "family_best": family_best,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--n-min", type=int, default=3)
    parser.add_argument("--n-max", type=int, default=8)
    parser.add_argument("--mus", default="0.005,0.01,0.03,0.1,0.25,0.5,0.8")
    parser.add_argument("--samples", type=int, default=80)
    parser.add_argument("--local-steps", type=int, default=120)
    parser.add_argument("--keep", type=int, default=20)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/M1_STRONG_ENERGY_SEARCH_2026_08_21.json"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = run(arguments)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    leader = result["best"][0]
    print(json.dumps({
        "output": str(arguments.output),
        "evaluations": result["evaluations_counting_local_steps"],
        "elapsed_seconds": result["elapsed_seconds"],
        "best_n": leader["n"],
        "best_mu": leader["mu"],
        "best_gap": leader["gap_rate_minus_target"],
        "best_family": leader["family"],
    }, indent=2))
