"""Hostile E1 differential-evolution attack on the half-prefix inequality.

The target is the stronger (leaf-free) statement

    J_ceil(n/2)(A) >= (mu/2) A^{-1}.

Matrices are low-rank Gram lifts A=mu*I+(1-mu)*V*V.T with unit rows.  The
subset Bellman recursion is exact up to float64 arithmetic.  A null result is
not a proof; a negative margin must be reconstructed exactly before promotion.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from iter4_schur_moment_search import SubsetBellman, generalized_coefficient


def logistic(value: float) -> float:
    value = float(np.clip(value, -18.0, 8.0))
    return 1.0 / (1.0 + math.exp(-value))


def decode(parameters: np.ndarray, n: int, rank: int, fixed_mu: float | None = None):
    vectors = parameters[:-1].reshape(n, rank).copy()
    norms = np.linalg.norm(vectors, axis=1)
    norms[norms < 1e-12] = 1.0
    vectors /= norms[:, None]
    requested_mu = logistic(parameters[-1]) if fixed_mu is None else fixed_mu
    correlation = vectors @ vectors.T
    matrix = requested_mu * np.eye(n) + (1.0 - requested_mu) * correlation
    return matrix, vectors, requested_mu


def objective(parameters: np.ndarray, n: int, rank: int, fixed_mu: float | None = None):
    matrix, vectors, requested_mu = decode(parameters, n, rank, fixed_mu)
    actual_mu = float(np.linalg.eigvalsh(matrix)[0])
    steps = (n + 1) // 2
    certificate = SubsetBellman(matrix).prefix((1 << n) - 1, steps)
    coefficient = generalized_coefficient(matrix, certificate)
    return coefficient / actual_mu, coefficient, actual_mu, requested_mu, matrix, vectors


def seed_population(rng: np.random.Generator, population: int, n: int, rank: int):
    dimension = n * rank + 1
    values = rng.normal(size=(population, dimension))
    values[:, -1] = rng.uniform(-14.0, 5.0, size=population)
    # Signed-rank-one, near-identity, alternating poles, and a circle seed.
    for row, logit in ((0, 0.0), (1, 4.0), (2, -10.0)):
        values[row, :-1] = 0.0
        values[row, 0 : n * rank : rank] = 1.0
        values[row, -1] = logit
    if rank >= 2 and population > 3:
        angles = 2.0 * np.pi * np.arange(n) / n
        vectors = np.zeros((n, rank))
        vectors[:, 0] = np.cos(angles)
        vectors[:, 1] = np.sin(angles)
        values[3, :-1] = vectors.ravel()
        values[3, -1] = -6.0
    if population > 4:
        vectors = np.zeros((n, rank))
        vectors[:, 0] = np.where(np.arange(n) % 2, -1.0, 1.0)
        values[4, :-1] = vectors.ravel()
        values[4, -1] = -6.0
    return values


def run(args: argparse.Namespace) -> dict[str, object]:
    rng = np.random.default_rng(args.seed)
    population = seed_population(rng, args.population, args.n, args.rank)
    values = [objective(row, args.n, args.rank, args.fixed_mu) for row in population]
    dimension = population.shape[1]
    history: list[dict[str, float | int]] = []
    started = time.monotonic()
    for generation in range(args.generations):
        for target in range(args.population):
            pool = [index for index in range(args.population) if index != target]
            first, second, third = rng.choice(pool, size=3, replace=False)
            scale = rng.uniform(0.35, 1.0)
            mutant = population[first] + scale * (population[second] - population[third])
            mutant[-1] = np.clip(mutant[-1], -18.0, 8.0)
            mask = rng.random(dimension) < args.crossover
            mask[int(rng.integers(0, dimension))] = True
            proposal = np.where(mask, mutant, population[target])
            if args.fixed_mu is not None:
                proposal[-1] = 0.0
            proposal_value = objective(proposal, args.n, args.rank, args.fixed_mu)
            if proposal_value[0] < values[target][0]:
                population[target] = proposal
                values[target] = proposal_value
        best = min(values, key=lambda item: item[0])
        history.append(
            {
                "generation": generation + 1,
                "coefficient_over_mu": float(best[0]),
                "margin_over_half": float(best[0] - 0.5),
                "actual_mu": float(best[2]),
            }
        )
        if (generation + 1) % 10 == 0:
            print(json.dumps(history[-1]), flush=True)

    index = min(range(args.population), key=lambda item: values[item][0])
    ratio, coefficient, actual_mu, requested_mu, matrix, vectors = values[index]
    return {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 differential-evolution search; null result is not proof",
        "target": "J_ceil(n/2)(A) >= (mu/2) A^{-1}",
        "seed": args.seed,
        "n": args.n,
        "gram_rank": args.rank,
        "fixed_mu": args.fixed_mu,
        "steps": (args.n + 1) // 2,
        "population": args.population,
        "generations": args.generations,
        "evaluations": args.population * (args.generations + 1),
        "elapsed_seconds": time.monotonic() - started,
        "best": {
            "coefficient_over_mu": float(ratio),
            "margin_over_half": float(ratio - 0.5),
            "coefficient": float(coefficient),
            "actual_mu": float(actual_mu),
            "requested_mu": float(requested_mu),
            "vectors": vectors.tolist(),
            "matrix": matrix.tolist(),
        },
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--rank", type=int, default=3)
    parser.add_argument("--population", type=int, default=32)
    parser.add_argument("--generations", type=int, default=80)
    parser.add_argument("--crossover", type=float, default=0.72)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--fixed-mu", type=float)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER5_HALF_PREFIX_OPTIMIZE.json"),
    )
    args = parser.parse_args()
    if args.fixed_mu is not None and not 0.0 < args.fixed_mu <= 1.0:
        parser.error("--fixed-mu must lie in (0,1]")
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best": result["best"]}, indent=2))


if __name__ == "__main__":
    main()
