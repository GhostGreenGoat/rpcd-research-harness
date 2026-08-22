"""Explore an adjacency-feature Bessel certificate for the T080 boundary.

For a singular correlation matrix C and a uniformly random order pi, write

    B_pi = M_pi(C)^(-1),   K(C) = E[B_pi^T B_pi].

Regard each scalar row of B_pi as a function on permutations. Orthogonally
project it onto the span of the constant function and every oriented adjacency
indicator ``1{j is immediately before i}``. Bessel's inequality gives the
rigorous finite-dimensional relation

    K(C) >= K_adj(C).

This script evaluates whether the still-conjectural lower certificate
``K_adj(C) >= 2 P_ker(C)`` survives structured and random boundary tests. All
eigenvalue decisions are float64 E1 evidence, not a proof.
"""

from __future__ import annotations

import argparse
import json
import sys
from math import factorial
from itertools import permutations
from pathlib import Path
from typing import Iterable

import numpy as np

if __package__ in {None, ""}:  # direct ``python scripts/...py`` invocation
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.search_m1_boundary_coefficient import two_pole_ring
from scripts.search_strong_one_epoch_energy import boundary_gram, circle_gram


def orders_and_features(
    n: int,
    max_block_vertices: int,
    order_samples: int,
    rng: np.random.Generator,
) -> tuple[list[tuple[int, ...]], np.ndarray, np.ndarray, int]:
    if max_block_vertices < 2 or max_block_vertices > n:
        raise ValueError("max_block_vertices must lie in [2,n]")
    if order_samples < 0:
        raise ValueError("order_samples cannot be negative")
    orders = (
        [tuple(int(value) for value in rng.permutation(n)) for _ in range(order_samples)]
        if order_samples
        else list(permutations(range(n)))
    )
    blocks = [()] + [
        block
        for length in range(2, max_block_vertices + 1)
        for block in permutations(range(n), length)
    ]
    block_index = {block: index for index, block in enumerate(blocks)}
    feature_count = len(blocks)
    active_count = 1 + sum(
        n - length + 1 for length in range(2, max_block_vertices + 1)
    )
    active_features = np.empty((len(orders), active_count), dtype=np.int32)
    for row, order in enumerate(orders):
        active_features[row, 0] = 0
        cursor = 1
        for length in range(2, max_block_vertices + 1):
            for start in range(n - length + 1):
                active_features[row, cursor] = block_index[
                    order[start : start + length]
                ]
                cursor += 1
        assert cursor == active_count
    gram = exact_block_feature_gram(n, blocks)
    gram_inverse = np.linalg.pinv(gram, rcond=1e-12)
    return orders, active_features, gram_inverse, feature_count


def exact_block_feature_gram(
    n: int,
    blocks: list[tuple[int, ...]],
) -> np.ndarray:
    """Return exact E[phi phi^T] from compatible path-union counts.

    A set of oriented consecutive-block constraints is feasible precisely when
    its union is a vertex-disjoint collection of directed paths. If the union
    has ``e`` distinct adjacency edges, contracting those paths leaves ``n-e``
    objects, so the probability is ``(n-e)!/n!``.
    """
    edge_lists = [tuple(zip(block[:-1], block[1:])) for block in blocks]
    inverse_falling = [factorial(n - edges) / factorial(n) for edges in range(n)]
    gram = np.zeros((len(blocks), len(blocks)))
    for left, left_edges in enumerate(edge_lists):
        for right in range(left + 1):
            successors: dict[int, int] = {}
            predecessors: dict[int, int] = {}
            feasible = True
            for tail, head in (*left_edges, *edge_lists[right]):
                if (
                    tail in successors
                    and successors[tail] != head
                    or head in predecessors
                    and predecessors[head] != tail
                ):
                    feasible = False
                    break
                successors[tail] = head
                predecessors[head] = tail
            if feasible:
                for start in successors:
                    seen: set[int] = set()
                    vertex = start
                    while vertex in successors:
                        if vertex in seen:
                            feasible = False
                            break
                        seen.add(vertex)
                        vertex = successors[vertex]
                    if not feasible:
                        break
            probability = inverse_falling[len(successors)] if feasible else 0.0
            gram[left, right] = probability
            gram[right, left] = probability
    return gram


def inverse_factor(correlation: np.ndarray, order: tuple[int, ...]) -> np.ndarray:
    n = correlation.shape[0]
    permuted = correlation[np.ix_(order, order)]
    inverse_permuted = np.linalg.inv(np.tril(permuted))
    inverse = np.empty_like(correlation)
    inverse[np.ix_(order, order)] = inverse_permuted
    return inverse


def adjacency_certificate(
    correlation: np.ndarray,
    orders: list[tuple[int, ...]],
    active_features: np.ndarray,
    feature_gram_inverse: np.ndarray,
    feature_count: int,
    cross_fit: bool,
) -> tuple[np.ndarray, np.ndarray]:
    n = correlation.shape[0]
    cross = np.zeros((feature_count, n, n))
    cross_second = np.zeros_like(cross) if cross_fit else None
    first_count = len(orders) // 2 if cross_fit else len(orders)
    second_count = len(orders) - first_count
    exact = np.zeros((n, n))
    for row, order in enumerate(orders):
        inverse = inverse_factor(correlation, order)
        exact += inverse.T @ inverse
        target = cross if row < first_count else cross_second
        assert target is not None
        target[active_features[row]] += inverse
    cross /= first_count
    if cross_second is not None:
        cross_second /= second_count
    exact /= len(orders)
    projected = np.zeros((n, n))
    for output in range(n):
        moment = cross[:, output, :]
        if cross_second is None:
            projected += moment.T @ feature_gram_inverse @ moment
        else:
            other = cross_second[:, output, :]
            projected += (
                moment.T @ feature_gram_inverse @ other
                + other.T @ feature_gram_inverse @ moment
            ) / 2.0
    return (projected + projected.T) / 2.0, (exact + exact.T) / 2.0


def boundary_record(
    correlation: np.ndarray,
    family: str,
    orders: list[tuple[int, ...]],
    active_features: np.ndarray,
    feature_gram_inverse: np.ndarray,
    feature_count: int,
    cross_fit: bool,
) -> dict[str, object]:
    eigenvalues, eigenvectors = np.linalg.eigh((correlation + correlation.T) / 2.0)
    null = eigenvectors[:, eigenvalues < 1e-8]
    if null.shape[1] == 0:
        raise ValueError("boundary test requires a singular correlation matrix")
    projector = null @ null.T
    projected, exact = adjacency_certificate(
        correlation,
        orders,
        active_features,
        feature_gram_inverse,
        feature_count,
        cross_fit,
    )
    projected_residual = projected - 2.0 * projector
    exact_residual = exact - 2.0 * projector
    bessel_residual = exact - projected
    return {
        "family": family,
        "n": int(correlation.shape[0]),
        "rank": int(correlation.shape[0] - null.shape[1]),
        "nullity": int(null.shape[1]),
        "min_eigenvalue_projected_minus_2pker": float(
            np.linalg.eigvalsh(projected_residual)[0]
        ),
        "min_eigenvalue_exact_minus_2pker": float(
            np.linalg.eigvalsh(exact_residual)[0]
        ),
        "min_eigenvalue_bessel_residual": float(
            np.linalg.eigvalsh(bessel_residual)[0]
        ),
        "correlation_eigenvalues": eigenvalues.tolist(),
        "correlation": correlation.tolist(),
    }


def cases(
    n: int,
    samples: int,
    rng: np.random.Generator,
    latitudes: list[float],
    include_rank_one: bool,
) -> Iterable[tuple[str, np.ndarray]]:
    if include_rank_one:
        ones = np.ones((n, 1))
        yield "rank_one", ones @ ones.T
    for rank in range(1, n):
        for sample in range(samples):
            yield f"random_rank_{rank}_sample_{sample}", boundary_gram(n, rank, rng)
    if n >= 3:
        for sample in range(samples):
            yield f"circle_sample_{sample}", circle_gram(n, rng)
    if n >= 4:
        for latitude in latitudes:
            yield f"two_pole_ring_latitude_{latitude:.5f}", two_pole_ring(n, float(latitude))
        if n == 8:
            yield "two_pole_hexagon_exact_latitude", two_pole_ring(n, 4.0 / np.sqrt(21.0))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260827)
    parser.add_argument("--n-min", type=int, default=3)
    parser.add_argument("--n-max", type=int, default=7)
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument(
        "--max-block-vertices",
        type=int,
        default=2,
        help="Use consecutive permutation blocks with 2..L vertices as Bessel features.",
    )
    parser.add_argument(
        "--order-samples",
        type=int,
        default=0,
        help="0 enumerates all n! orders; a positive value uses Monte Carlo orders with an exact feature Gram.",
    )
    parser.add_argument(
        "--latitudes",
        default="0.15,0.2525,0.355,0.4575,0.56,0.6625,0.765,0.8675,0.97",
        help="Comma-separated two-pole-ring latitudes.",
    )
    parser.add_argument("--no-rank-one", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_ADJACENCY_BESSEL_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    latitudes = [float(value) for value in args.latitudes.split(",") if value.strip()]
    records: list[dict[str, object]] = []
    for n in range(args.n_min, args.n_max + 1):
        orders, active_features, feature_gram_inverse, feature_count = orders_and_features(
            n,
            args.max_block_vertices,
            args.order_samples,
            rng,
        )
        for family, correlation in cases(
            n,
            args.samples,
            rng,
            latitudes,
            not args.no_rank_one,
        ):
            record = boundary_record(
                correlation,
                family,
                orders,
                active_features,
                feature_gram_inverse,
                feature_count,
                args.order_samples > 0,
            )
            records.append(record)
            print(
                n,
                family,
                record["min_eigenvalue_projected_minus_2pker"],
                record["min_eigenvalue_exact_minus_2pker"],
            )
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E1",
        "claim": "Adjacency Bessel projection numerically dominates 2 P_ker on tested singular correlations.",
        "warning": "A finite float64 null search is not a proof; negative projected margin would refute only this certificate route.",
        "seed": args.seed,
        "n_min": args.n_min,
        "n_max": args.n_max,
        "samples_per_rank": args.samples,
        "max_block_vertices": args.max_block_vertices,
        "order_sampling": "exhaustive" if args.order_samples == 0 else "monte_carlo",
        "orders_per_matrix": len(orders),
        "monte_carlo_projection_estimator": (
            "two-half cross-fit (unbiased quadratic moment)"
            if args.order_samples
            else "exact orthogonal projection"
        ),
        "evaluations": len(records),
        "minimum_projected_margin": min(
            float(record["min_eigenvalue_projected_minus_2pker"]) for record in records
        ),
        "minimum_exact_margin": min(
            float(record["min_eigenvalue_exact_minus_2pker"]) for record in records
        ),
        "maximum_negative_bessel_roundoff": min(
            float(record["min_eigenvalue_bessel_residual"]) for record in records
        ),
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("wrote", args.output)


if __name__ == "__main__":
    main()
