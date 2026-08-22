"""Iteration-4 diagnostics for T085 Schur-loss moment compression.

All floating-point outputs are E1/E2 finite diagnostics, never proofs.  The
script works with a fixed full correlation matrix and uses subset Bellman DP,
so no n! enumeration is required.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from functools import lru_cache
from pathlib import Path

import numpy as np


def normalize_rows(vectors: np.ndarray) -> np.ndarray:
    return vectors / np.linalg.norm(vectors, axis=1)[:, None]


def boundary_matrix(n: int, rank: int, mu: float, rng: np.random.Generator) -> np.ndarray:
    vectors = normalize_rows(rng.normal(size=(n, rank)))
    correlation = vectors @ vectors.T
    return mu * np.eye(n) + (1.0 - mu) * correlation


def deletion_data(matrix: np.ndarray, index: int):
    size = matrix.shape[0]
    keep = [j for j in range(size) if j != index]
    selector = np.eye(size)[keep, :]
    unit = np.eye(size)[:, index]
    lift = selector @ (np.eye(size) - np.outer(matrix[:, index], unit))
    child = matrix[np.ix_(keep, keep)]
    return child, lift, unit


def first_schur_moment(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    inverse = np.linalg.inv(matrix)
    leverage = 1.0 / np.diag(inverse)
    shifted = inverse - np.eye(size)
    return shifted @ np.diag(leverage) @ shifted / size


def second_schur_moment(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    result = np.zeros_like(matrix)
    for index in range(size):
        child, lift, _ = deletion_data(matrix, index)
        result += lift.T @ first_schur_moment(child) @ lift
    return result / size


def second_schur_pair_formula(matrix: np.ndarray) -> np.ndarray:
    """Exact ordered-pair rank-one representation derived in iteration 4."""
    size = matrix.shape[0]
    inverse = np.linalg.inv(matrix)
    shifted = inverse - np.eye(size)
    result = np.zeros_like(matrix)
    identity = np.eye(size)
    for first in range(size):
        for second in range(size):
            if first == second:
                continue
            denominator = (
                inverse[second, second]
                - inverse[first, second] ** 2 / inverse[first, first]
            )
            child_leverage = 1.0 / denominator
            vector = (
                shifted @ identity[:, second]
                - (inverse[first, second] / inverse[first, first])
                * shifted
                @ identity[:, first]
                + matrix[first, second] * identity[:, first]
            )
            result += child_leverage * np.outer(vector, vector)
    return result / (size * (size - 1))


def normalized_first_loss_rate(matrix: np.ndarray) -> float:
    """Smallest eta such that bar(D)_B <= eta B^{-1}."""
    loss = first_schur_moment(matrix)
    root = symmetric_sqrt(matrix)
    return float(np.linalg.eigvalsh(root @ loss @ root)[-1])


def second_trace_loss_rate_upper(matrix: np.ndarray) -> float:
    """Certified lambda-max upper bound from trace and trace-square moments."""
    size = matrix.shape[0]
    if size == 1:
        return 0.0
    inverse = np.linalg.inv(matrix)
    leverage = 1.0 / np.diag(inverse)
    core = inverse - 2.0 * np.eye(size) + matrix
    frame_gram = (
        np.diag(np.sqrt(leverage))
        @ core
        @ np.diag(np.sqrt(leverage))
        / size
    )
    trace = float(np.trace(frame_gram))
    trace_square = float(np.trace(frame_gram @ frame_gram))
    radicand = max(0.0, (size - 1) * (size * trace_square - trace * trace))
    moment_bound = (trace + math.sqrt(radicand)) / size
    spectral_floor_bound = 1.0 - float(np.linalg.eigvalsh(matrix)[0])
    return min(moment_bound, max(0.0, spectral_floor_bound))


def weighted_second_compression(matrix: np.ndarray, mode: str = "exact") -> np.ndarray:
    """Return a certified upper compression of the second Schur moment.

    ``mode=exact`` uses the exact scalar eta(C_i) for each child.  ``trace``
    uses eta(C_i) <= 1-average(child leverage), which is algebraic but looser.
    """
    size = matrix.shape[0]
    inverse = np.linalg.inv(matrix)
    leverage = 1.0 / np.diag(inverse)
    weights = []
    for index in range(size):
        child, _, _ = deletion_data(matrix, index)
        if mode == "exact":
            weights.append(normalized_first_loss_rate(child))
        elif mode == "moment":
            weights.append(second_trace_loss_rate_upper(child))
        elif mode == "trace":
            child_inverse = np.linalg.inv(child)
            weights.append(1.0 - float(np.mean(1.0 / np.diag(child_inverse))))
        else:
            raise ValueError(mode)
    weights_array = np.asarray(weights)
    shifted = inverse - np.eye(size)
    return (
        float(np.mean(weights_array)) * inverse
        - np.diag(weights_array) / size
        - shifted @ np.diag(weights_array * leverage) @ shifted / size
    )


def lifted_child_loss_rate_upper(matrix: np.ndarray, index: int, mode: str = "moment") -> float:
    """Bound one lifted child loss in the *parent* energy metric.

    If ``X_i=L_i^T bar(D)_{C_i}L_i``, the returned beta satisfies
    ``X_i <= beta B^{-1}``.  The crucial matrix in the nonzero spectrum is
    ``bar(D)_{C_i}^{1/2}(C_i-b_i b_i^T)bar(D)_{C_i}^{1/2}``, not the looser
    child normalization ``C_i^{1/2}bar(D)_{C_i}C_i^{1/2}``.
    """
    child, lift, _ = deletion_data(matrix, index)
    child_loss = first_schur_moment(child)
    keep = [j for j in range(matrix.shape[0]) if j != index]
    column = matrix[keep, index]
    schur_after_pivot = child - np.outer(column, column)
    if mode == "exact":
        root = symmetric_sqrt(schur_after_pivot)
        normalized = root @ child_loss @ root
        return float(np.linalg.eigvalsh((normalized + normalized.T) / 2.0)[-1])
    if mode != "moment":
        raise ValueError(mode)
    dimension = child.shape[0]
    product = schur_after_pivot @ child_loss
    trace = float(np.trace(product))
    trace_square = float(np.trace(product @ product))
    radicand = max(
        0.0, (dimension - 1) * (dimension * trace_square - trace * trace)
    )
    moment_bound = (trace + math.sqrt(radicand)) / dimension
    # schur_after_pivot <= child, and bar(D)_child <=
    # (1-lambda_min(child))*child^{-1}.
    spectral_floor_bound = 1.0 - float(np.linalg.eigvalsh(child)[0])
    return min(moment_bound, max(0.0, spectral_floor_bound))


def parallel_sum(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """PSD parallel sum, using the Moore--Penrose extension."""
    left = (left + left.T) / 2.0
    right = (right + right.T) / 2.0
    total = left + right
    value = left - left @ np.linalg.pinv(total, rcond=1e-12, hermitian=True) @ left
    return (value + value.T) / 2.0


def parallel_second_compression(
    matrix: np.ndarray, child_mode: str = "moment", lifted_mode: str = "moment"
) -> np.ndarray:
    """Complementary two-geometry compression of the second Schur moment.

    ``U`` scalarizes each child before lifting and is sharp on the high-nullity
    signed-rank-one boundary.  ``W`` scalarizes after lifting in the parent
    metric and is sharp up to a small constant on the simple-null boundary.
    Since ``R<=U`` and ``R<=W``, monotonicity of the parallel sum gives the
    certified inequality ``R<=2(U:W)``.
    """
    size = matrix.shape[0]
    inverse = np.linalg.inv(matrix)
    child_upper = weighted_second_compression(matrix, mode=child_mode)
    lifted_rates = [
        lifted_child_loss_rate_upper(matrix, index, mode=lifted_mode)
        for index in range(size)
    ]
    parent_upper = float(np.mean(lifted_rates)) * inverse
    return 2.0 * parallel_sum(child_upper, parent_upper)


def adaptive_second_compression(
    matrix: np.ndarray, child_mode: str = "moment", lifted_mode: str = "moment"
) -> tuple[np.ndarray, str, float, float]:
    """Select the tighter parent-rate upper while retaining ``U`` when useful."""
    size = matrix.shape[0]
    inverse = np.linalg.inv(matrix)
    child_upper = weighted_second_compression(matrix, mode=child_mode)
    lifted_rate = float(
        np.mean(
            [
                lifted_child_loss_rate_upper(matrix, index, mode=lifted_mode)
                for index in range(size)
            ]
        )
    )
    child_rate = -generalized_coefficient(matrix, -child_upper)
    if child_rate <= lifted_rate:
        return child_upper, "pre_lift", child_rate, lifted_rate
    return lifted_rate * inverse, "post_lift", child_rate, lifted_rate


def direct_pair_trace_loss_rate_upper(matrix: np.ndarray) -> float:
    """Trace/trace-square scalar compression after aggregating the pair frame."""
    size = matrix.shape[0]
    second = second_schur_moment(matrix)
    root = symmetric_sqrt(matrix)
    normalized = root @ second @ root
    normalized = (normalized + normalized.T) / 2.0
    trace = float(np.trace(normalized))
    trace_square = float(np.trace(normalized @ normalized))
    radicand = max(0.0, (size - 1) * (size * trace_square - trace * trace))
    return (trace + math.sqrt(radicand)) / size


def symmetric_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2.0)
    return (vectors * np.sqrt(np.maximum(values, 0.0))) @ vectors.T


def generalized_coefficient(matrix: np.ndarray, certificate: np.ndarray) -> float:
    root = symmetric_sqrt(matrix)
    scaled = root @ certificate @ root
    return float(np.linalg.eigvalsh((scaled + scaled.T) / 2.0)[0])


class SubsetBellman:
    def __init__(self, matrix: np.ndarray):
        self.matrix = matrix
        self.n = matrix.shape[0]

    def indices(self, mask: int) -> list[int]:
        return [i for i in range(self.n) if mask & (1 << i)]

    @lru_cache(maxsize=None)
    def determinant_tail(self, mask: int, depth: int) -> np.ndarray:
        indices = self.indices(mask)
        block = self.matrix[np.ix_(indices, indices)]
        size = len(indices)
        if size == 1:
            return np.ones((1, 1))
        if depth == 0:
            return np.linalg.det(block) * np.linalg.inv(block)
        result = np.zeros_like(block)
        for local, global_index in enumerate(indices):
            child, lift, unit = deletion_data(block, local)
            child_value = self.determinant_tail(mask ^ (1 << global_index), depth - 1)
            result += np.outer(unit, unit) + lift.T @ child_value @ lift
        return result / size

    @lru_cache(maxsize=None)
    def prefix(self, mask: int, steps: int) -> np.ndarray:
        indices = self.indices(mask)
        block = self.matrix[np.ix_(indices, indices)]
        size = len(indices)
        if steps == 0:
            return np.zeros_like(block)
        if size == 1:
            return np.ones((1, 1))
        if steps > size:
            raise ValueError("steps exceeds remaining dimension")
        result = np.zeros_like(block)
        for local, global_index in enumerate(indices):
            child, lift, unit = deletion_data(block, local)
            child_value = self.prefix(mask ^ (1 << global_index), steps - 1)
            result += np.outer(unit, unit) + lift.T @ child_value @ lift
        return result / size


def structured_rank_one(n: int, mu: float) -> np.ndarray:
    return mu * np.eye(n) + (1.0 - mu) * np.ones((n, n))


def structured_simplex(n: int, mu: float) -> np.ndarray:
    correlation = np.full((n, n), -1.0 / (n - 1))
    np.fill_diagonal(correlation, 1.0)
    return mu * np.eye(n) + (1.0 - mu) * correlation


def rank_one_shallow_limit(n: int, depth: int) -> float:
    """Exact mu->0 limit of c_depth/mu on the signed rank-one family.

    Valid for 1 <= depth <= n-3.  At depth n-2 the determinant tail reaches a
    two-dimensional child and contributes an additional boundary term.  The
    derivation is algebraic and recorded in
    the accompanying iteration-4 document.
    """
    if not 1 <= depth <= n - 3:
        raise ValueError("formula requires 1 <= depth <= n-3")
    return (2.0 * depth - 1.0 - 1.0 / n) / (n - 1.0)


def run(args: argparse.Namespace) -> dict[str, object]:
    rng = np.random.default_rng(args.seed)
    started = time.time()
    max_pair_residual = 0.0
    min_exact_compression_residual = math.inf
    min_moment_compression_residual = math.inf
    min_trace_compression_residual = math.inf
    min_parallel_compression_residual = math.inf
    max_parallel_rate_ratio = 0.0
    max_direct_pair_moment_ratio = 0.0
    min_adaptive_compression_residual = math.inf
    max_adaptive_rate_ratio = 0.0
    adaptive_branch_counts = {"pre_lift": 0, "post_lift": 0}
    worst_first_dominates_second = {"min_eigenvalue": math.inf}
    prefix_min_ratio: dict[str, dict[str, object]] = {}
    tail_min_ratio: dict[str, dict[str, object]] = {}
    evaluations = 0

    for n in range(args.n_min, args.n_max + 1):
        prefix_min_ratio[str(n)] = {}
        tail_min_ratio[str(n)] = {}
        for sample in range(args.samples):
            rank = int(rng.integers(1, n + 1))
            requested_mu = 10.0 ** rng.uniform(args.log_mu_min, args.log_mu_max)
            matrix = boundary_matrix(n, rank, requested_mu, rng)
            actual_mu = float(np.linalg.eigvalsh(matrix)[0])

            first = first_schur_moment(matrix)
            second = second_schur_moment(matrix)
            pair = second_schur_pair_formula(matrix)
            max_pair_residual = max(max_pair_residual, float(np.max(np.abs(second - pair))))

            exact_upper = weighted_second_compression(matrix, mode="exact")
            moment_upper = weighted_second_compression(matrix, mode="moment")
            trace_upper = weighted_second_compression(matrix, mode="trace")
            parallel_upper = parallel_second_compression(
                matrix, child_mode="moment", lifted_mode="moment"
            )
            adaptive_upper, adaptive_branch, _, _ = adaptive_second_compression(
                matrix, child_mode="moment", lifted_mode="moment"
            )
            adaptive_branch_counts[adaptive_branch] += 1
            min_exact_compression_residual = min(
                min_exact_compression_residual,
                float(np.linalg.eigvalsh((exact_upper - second + exact_upper.T - second.T) / 2.0)[0]),
            )
            min_trace_compression_residual = min(
                min_trace_compression_residual,
                float(np.linalg.eigvalsh((trace_upper - second + trace_upper.T - second.T) / 2.0)[0]),
            )
            min_moment_compression_residual = min(
                min_moment_compression_residual,
                float(
                    np.linalg.eigvalsh(
                        (moment_upper - second + moment_upper.T - second.T) / 2.0
                    )[0]
                ),
            )
            min_parallel_compression_residual = min(
                min_parallel_compression_residual,
                float(
                    np.linalg.eigvalsh(
                        (parallel_upper - second + parallel_upper.T - second.T) / 2.0
                    )[0]
                ),
            )
            min_adaptive_compression_residual = min(
                min_adaptive_compression_residual,
                float(
                    np.linalg.eigvalsh(
                        (adaptive_upper - second + adaptive_upper.T - second.T) / 2.0
                    )[0]
                ),
            )
            actual_second_rate = generalized_coefficient(
                matrix, -second
            ) * -1.0
            # The helper above returns lambda_min; negation extracts lambda_max.
            if actual_second_rate > 1e-14:
                parallel_rate = generalized_coefficient(matrix, -parallel_upper) * -1.0
                max_parallel_rate_ratio = max(
                    max_parallel_rate_ratio, parallel_rate / actual_second_rate
                )
                max_direct_pair_moment_ratio = max(
                    max_direct_pair_moment_ratio,
                    direct_pair_trace_loss_rate_upper(matrix) / actual_second_rate,
                )
                adaptive_rate = generalized_coefficient(matrix, -adaptive_upper) * -1.0
                max_adaptive_rate_ratio = max(
                    max_adaptive_rate_ratio, adaptive_rate / actual_second_rate
                )
            dominance = float(np.linalg.eigvalsh((first - second + first.T - second.T) / 2.0)[0])
            if dominance < float(worst_first_dominates_second["min_eigenvalue"]):
                worst_first_dominates_second = {
                    "min_eigenvalue": dominance,
                    "n": n,
                    "rank": rank,
                    "requested_mu": requested_mu,
                    "actual_mu": actual_mu,
                    "matrix": matrix.tolist(),
                }

            bellman = SubsetBellman(matrix)
            full = (1 << n) - 1
            for steps in range(1, n + 1):
                prefix = bellman.prefix(full, steps)
                coefficient = generalized_coefficient(matrix, prefix)
                denominator = steps * actual_mu / n
                ratio = coefficient / denominator
                previous = prefix_min_ratio[str(n)].get(str(steps))
                if previous is None or ratio < float(previous["ratio_to_t_mu_over_n"]):
                    prefix_min_ratio[str(n)][str(steps)] = {
                        "ratio_to_t_mu_over_n": ratio,
                        "coefficient": coefficient,
                        "actual_mu": actual_mu,
                        "rank": rank,
                    }

            for depth in range(0, n):
                tail = bellman.determinant_tail(full, depth)
                coefficient = generalized_coefficient(matrix, tail)
                ratio = coefficient / actual_mu
                previous = tail_min_ratio[str(n)].get(str(depth))
                if previous is None or ratio < float(previous["coefficient_over_mu"]):
                    tail_min_ratio[str(n)][str(depth)] = {
                        "coefficient_over_mu": ratio,
                        "coefficient": coefficient,
                        "actual_mu": actual_mu,
                        "rank": rank,
                    }
            evaluations += 1

    structured_limits = {
        str(n): {
            str(depth): rank_one_shallow_limit(n, depth)
            for depth in range(1, n - 2)
        }
        for n in range(max(3, args.n_min), args.n_max + 1)
    }
    return {
        "status": "E1/E2 finite diagnostics; null searches are not proofs",
        "seed": args.seed,
        "n_range": [args.n_min, args.n_max],
        "samples_per_dimension": args.samples,
        "log10_mu_range": [args.log_mu_min, args.log_mu_max],
        "evaluations": evaluations,
        "elapsed_seconds": time.time() - started,
        "max_pair_formula_residual": max_pair_residual,
        "min_exact_weighted_compression_residual": min_exact_compression_residual,
        "min_second_trace_compression_residual": min_moment_compression_residual,
        "min_trace_weighted_compression_residual": min_trace_compression_residual,
        "min_parallel_moment_compression_residual": min_parallel_compression_residual,
        "max_parallel_moment_rate_ratio": max_parallel_rate_ratio,
        "max_direct_pair_moment_rate_ratio": max_direct_pair_moment_ratio,
        "min_adaptive_moment_compression_residual": min_adaptive_compression_residual,
        "max_adaptive_moment_rate_ratio": max_adaptive_rate_ratio,
        "adaptive_branch_counts": adaptive_branch_counts,
        "worst_R1_minus_R2": worst_first_dominates_second,
        "prefix_min_ratio": prefix_min_ratio,
        "determinant_tail_min_ratio": tail_min_ratio,
        "rank_one_shallow_exact_limits": structured_limits,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--n-min", type=int, default=3)
    parser.add_argument("--n-max", type=int, default=8)
    parser.add_argument("--samples", type=int, default=80)
    parser.add_argument("--log-mu-min", type=float, default=-4.0)
    parser.add_argument("--log-mu-max", type=float, default=-0.01)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T085_SCHUR_MOMENT_SEARCH.json"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = run(arguments)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(arguments.output),
        "evaluations": result["evaluations"],
        "elapsed_seconds": result["elapsed_seconds"],
        "max_pair_formula_residual": result["max_pair_formula_residual"],
        "min_exact_compression_residual": result["min_exact_weighted_compression_residual"],
        "min_second_trace_compression_residual": result["min_second_trace_compression_residual"],
        "min_trace_compression_residual": result["min_trace_weighted_compression_residual"],
        "min_parallel_compression_residual": result["min_parallel_moment_compression_residual"],
        "max_parallel_rate_ratio": result["max_parallel_moment_rate_ratio"],
        "max_direct_pair_moment_rate_ratio": result["max_direct_pair_moment_rate_ratio"],
        "min_adaptive_compression_residual": result["min_adaptive_moment_compression_residual"],
        "max_adaptive_rate_ratio": result["max_adaptive_moment_rate_ratio"],
        "adaptive_branch_counts": result["adaptive_branch_counts"],
        "worst_R1_minus_R2": result["worst_R1_minus_R2"]["min_eigenvalue"],
    }, indent=2))
