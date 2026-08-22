"""E1 differential-evolution attack on the half-depth T085 conjecture.

Matrices are ``A=mu I+(1-mu)VV^T`` with unit-normalized rows of V and
rank(V)<n, so the requested ``mu`` is the actual spectral floor up to floating
roundoff.  A negative search result is not a proof.
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
    value = float(np.clip(value, -16.0, 8.0))
    return 1.0 / (1.0 + math.exp(-value))


def decode(parameters: np.ndarray, n: int, rank: int):
    vectors = parameters[:-1].reshape(n, rank).copy()
    norms = np.linalg.norm(vectors, axis=1)
    norms[norms < 1e-12] = 1.0
    vectors /= norms[:, None]
    mu = logistic(parameters[-1])
    correlation = vectors @ vectors.T
    matrix = mu * np.eye(n) + (1.0 - mu) * correlation
    return matrix, vectors, mu


def objective(parameters: np.ndarray, n: int, rank: int, depth: int):
    matrix, _, requested_mu = decode(parameters, n, rank)
    actual_mu = float(np.linalg.eigvalsh(matrix)[0])
    tail = SubsetBellman(matrix).determinant_tail((1 << n) - 1, depth)
    coefficient = generalized_coefficient(matrix, tail)
    return coefficient / actual_mu, coefficient, actual_mu, requested_mu, matrix


def run(args):
    rng = np.random.default_rng(args.seed)
    dimension = args.n * args.rank + 1
    population = rng.normal(size=(args.population, dimension))
    population[:, -1] = rng.uniform(-10.0, 4.0, size=args.population)
    # Include signed-rank-one-like and near-identity starting points.
    population[0, :-1] = 0.0
    population[0, 0 : args.n * args.rank : args.rank] = 1.0
    population[0, -1] = 0.0
    population[1, :-1] = population[0, :-1]
    population[1, -1] = 3.0

    depth = (args.n + 1) // 2
    values = [objective(row, args.n, args.rank, depth) for row in population]
    history = []
    started = time.time()
    for generation in range(args.generations):
        for target in range(args.population):
            choices = [i for i in range(args.population) if i != target]
            first, second, third = rng.choice(choices, size=3, replace=False)
            factor = rng.uniform(0.45, 0.95)
            mutant = population[first] + factor * (population[second] - population[third])
            mutant[-1] = np.clip(mutant[-1], -16.0, 8.0)
            mask = rng.random(dimension) < args.crossover
            mask[int(rng.integers(0, dimension))] = True
            proposal = np.where(mask, mutant, population[target])
            proposal_value = objective(proposal, args.n, args.rank, depth)
            if proposal_value[0] < values[target][0]:
                population[target] = proposal
                values[target] = proposal_value
        best = min(values, key=lambda item: item[0])
        history.append({
            "generation": generation + 1,
            "best_ratio": float(best[0]),
            "actual_mu": float(best[2]),
        })
        if (generation + 1) % 10 == 0:
            print(json.dumps(history[-1]), flush=True)

    index = min(range(args.population), key=lambda i: values[i][0])
    ratio, coefficient, actual_mu, requested_mu, matrix = values[index]
    _, vectors, _ = decode(population[index], args.n, args.rank)
    return {
        "evidence_level": "E1 float64 differential-evolution search; null result is not proof",
        "seed": args.seed,
        "n": args.n,
        "gram_rank": args.rank,
        "depth": depth,
        "population": args.population,
        "generations": args.generations,
        "crossover": args.crossover,
        "elapsed_seconds": time.time() - started,
        "candidate_claim": "H_ceil(n/2) >= (mu/2) A^{-1}",
        "best": {
            "c_over_mu": float(ratio),
            "coefficient": float(coefficient),
            "actual_mu": float(actual_mu),
            "requested_mu": float(requested_mu),
            "margin_over_one_half": float(ratio - 0.5),
            "vectors": vectors.tolist(),
            "matrix": matrix.tolist(),
        },
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=8)
    parser.add_argument("--rank", type=int, default=2)
    parser.add_argument("--population", type=int, default=36)
    parser.add_argument("--generations", type=int, default=70)
    parser.add_argument("--crossover", type=float, default=0.72)
    parser.add_argument("--seed", type=int, default=45085)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T085_HALF_DEPTH_OPTIMIZE.json"),
    )
    args = parser.parse_args()
    result = run(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "best": result["best"]}, indent=2))


if __name__ == "__main__":
    main()
