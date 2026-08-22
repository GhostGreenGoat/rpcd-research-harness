"""Symmetry-reduced hostile search for the RPCD half-depth certificate.

This is a finite floating-point explorer (evidence level E1), not a proof.
It evaluates the full determinant-tail Bellman matrix on block-exchangeable
correlation matrices.  A state is indexed only by the number of remaining
coordinates in each exchangeable group, so dimensions far beyond a generic
``2**n`` subset DP are accessible.

The target is

    H_{ceil(n/2)}(A) >= (lambda_min(A)/2) A^{-1}.

Run ``python reproducer.py --mode controls`` before trusting a search run.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np


@dataclass
class InvariantMatrix:
    """Entries of a matrix invariant under permutations inside each group."""

    diagonal: np.ndarray
    within: np.ndarray
    cross: np.ndarray


def _symmetric_sqrt(matrix: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2.0)
    if values[0] < -1e-9:
        raise ValueError(f"matrix is not PSD; smallest eigenvalue {values[0]}")
    return (vectors * np.sqrt(np.maximum(values, 0.0))) @ vectors.T


def full_matrix(
    counts: Sequence[int], diagonal: Sequence[float], within: Sequence[float], cross: np.ndarray
) -> np.ndarray:
    groups: list[int] = []
    for group, count in enumerate(counts):
        groups.extend([group] * int(count))
    size = len(groups)
    result = np.empty((size, size), dtype=float)
    for i, gi in enumerate(groups):
        for j, gj in enumerate(groups):
            if i == j:
                result[i, j] = diagonal[gi]
            elif gi == gj:
                result[i, j] = within[gi]
            else:
                result[i, j] = cross[gi, gj]
    return result


def representation_to_full(counts: Sequence[int], value: InvariantMatrix) -> np.ndarray:
    return full_matrix(counts, value.diagonal, value.within, value.cross)


class ExchangeableTailDP:
    """Exact-in-combinatorics Bellman DP with float64 small-block algebra.

    ``within[g]`` is the off-diagonal entry inside group ``g`` and
    ``cross[g,h]`` is the common entry between groups.  The diagonal is one.
    """

    def __init__(
        self,
        counts: Sequence[int],
        within: Sequence[float],
        cross: np.ndarray,
        leaf_mode: str = "determinant",
    ):
        self.counts = tuple(int(value) for value in counts)
        self.group_count = len(self.counts)
        self.within_a = np.asarray(within, dtype=float)
        self.cross_a = np.asarray(cross, dtype=float)
        if leaf_mode not in ("determinant", "zero"):
            raise ValueError("leaf_mode must be determinant or zero")
        self.leaf_mode = leaf_mode
        if self.within_a.shape != (self.group_count,):
            raise ValueError("within has wrong shape")
        if self.cross_a.shape != (self.group_count, self.group_count):
            raise ValueError("cross has wrong shape")
        if not np.allclose(self.cross_a, self.cross_a.T, atol=1e-13):
            raise ValueError("cross must be symmetric")
        self.states_evaluated = 0
        self.leaf_underflows = 0

    def root_matrix(self) -> np.ndarray:
        return full_matrix(
            self.counts,
            np.ones(self.group_count),
            self.within_a,
            self.cross_a,
        )

    def reduced_original(self, counts: Sequence[int]) -> tuple[list[int], np.ndarray]:
        active = [g for g, count in enumerate(counts) if count]
        reduced = np.zeros((len(active), len(active)), dtype=float)
        for ii, g in enumerate(active):
            reduced[ii, ii] = 1.0 + (counts[g] - 1) * self.within_a[g]
            for jj, h in enumerate(active[:ii]):
                value = math.sqrt(counts[g] * counts[h]) * self.cross_a[g, h]
                reduced[ii, jj] = reduced[jj, ii] = value
        return active, reduced

    def _leaf(self, counts: tuple[int, ...]) -> InvariantMatrix:
        """Return det(A_S) A_S^{-1} in invariant-entry coordinates."""
        groups = self.group_count
        if self.leaf_mode == "zero":
            return InvariantMatrix(
                np.zeros(groups), np.zeros(groups), np.zeros((groups, groups))
            )
        active, reduced = self.reduced_original(counts)
        sign, logdet = np.linalg.slogdet(reduced)
        if sign <= 0:
            raise ValueError("nonpositive group-constant block at determinant leaf")
        for g in active:
            if counts[g] > 1:
                transverse = 1.0 - self.within_a[g]
                if transverse <= 0:
                    raise ValueError("nonpositive transverse eigenvalue at determinant leaf")
                logdet += (counts[g] - 1) * math.log(transverse)
        if logdet < -744.0:
            scale = 0.0
            self.leaf_underflows += 1
        else:
            scale = math.exp(logdet)
        reduced_inverse = np.linalg.inv(reduced)
        diagonal = np.zeros(groups)
        within = np.zeros(groups)
        cross = np.zeros((groups, groups))
        position = {group: index for index, group in enumerate(active)}
        for g in active:
            count = counts[g]
            rgg = reduced_inverse[position[g], position[g]]
            if count > 1:
                transverse_inverse = 1.0 / (1.0 - self.within_a[g])
                diagonal[g] = scale * (
                    transverse_inverse * (1.0 - 1.0 / count) + rgg / count
                )
                within[g] = scale * (rgg - transverse_inverse) / count
            else:
                diagonal[g] = scale * rgg
        for ii, g in enumerate(active):
            for h in active[:ii]:
                value = (
                    scale
                    * reduced_inverse[position[g], position[h]]
                    / math.sqrt(counts[g] * counts[h])
                )
                cross[g, h] = cross[h, g] = value
        return InvariantMatrix(diagonal, within, cross)

    @lru_cache(maxsize=None)
    def bellman(self, counts: tuple[int, ...], depth: int) -> InvariantMatrix:
        self.states_evaluated += 1
        size = sum(counts)
        if size == 0:
            raise ValueError("empty Bellman state")
        if size == 1:
            diagonal = np.zeros(self.group_count)
            diagonal[next(g for g, count in enumerate(counts) if count)] = 1.0
            return InvariantMatrix(
                diagonal, np.zeros(self.group_count), np.zeros((self.group_count, self.group_count))
            )
        if depth == 0:
            return self._leaf(counts)
        if depth >= size:
            raise ValueError("depth must leave at least one coordinate")

        children: dict[int, InvariantMatrix] = {}
        for pivot in range(self.group_count):
            if counts[pivot] == 0:
                continue
            mutable = list(counts)
            mutable[pivot] -= 1
            children[pivot] = self.bellman(tuple(mutable), depth - 1)
        return self._lift_from_children(counts, children)

    def _lift_from_children(
        self, counts: tuple[int, ...], children: dict[int, InvariantMatrix]
    ) -> InvariantMatrix:
        """One Bellman lift from already evaluated child count states."""
        size = sum(counts)
        child_y: dict[int, np.ndarray] = {}
        child_s: dict[int, float] = {}
        for pivot in range(self.group_count):
            if counts[pivot] == 0:
                continue
            mutable = list(counts)
            mutable[pivot] -= 1
            remaining = tuple(mutable)
            child = children[pivot]
            b = np.array(
                [
                    self.within_a[pivot]
                    if h == pivot
                    else self.cross_a[pivot, h]
                    for h in range(self.group_count)
                ],
                dtype=float,
            )
            y = np.zeros(self.group_count)
            for h in range(self.group_count):
                if remaining[h] == 0:
                    continue
                y[h] = (
                    child.diagonal[h] + (remaining[h] - 1) * child.within[h]
                ) * b[h]
                for ell in range(self.group_count):
                    if ell != h and remaining[ell]:
                        y[h] += remaining[ell] * child.cross[h, ell] * b[ell]
            child_y[pivot] = y
            child_s[pivot] = float(sum(remaining[h] * b[h] * y[h] for h in range(self.group_count)))

        diagonal = np.zeros(self.group_count)
        within = np.zeros(self.group_count)
        cross = np.zeros((self.group_count, self.group_count))
        for h in range(self.group_count):
            if counts[h] == 0:
                continue
            total = 1.0 + child_s[h]
            if counts[h] > 1:
                total += (counts[h] - 1) * children[h].diagonal[h]
            for pivot in range(self.group_count):
                if pivot != h and counts[pivot]:
                    total += counts[pivot] * children[pivot].diagonal[h]
            diagonal[h] = total / size

            if counts[h] >= 2:
                total = -2.0 * child_y[h][h]
                if counts[h] > 2:
                    total += (counts[h] - 2) * children[h].within[h]
                for pivot in range(self.group_count):
                    if pivot != h and counts[pivot]:
                        total += counts[pivot] * children[pivot].within[h]
                within[h] = total / size

        for h in range(self.group_count):
            if counts[h] == 0:
                continue
            for ell in range(h):
                if counts[ell] == 0:
                    continue
                total = -child_y[h][ell] - child_y[ell][h]
                if counts[h] > 1:
                    total += (counts[h] - 1) * children[h].cross[h, ell]
                if counts[ell] > 1:
                    total += (counts[ell] - 1) * children[ell].cross[h, ell]
                for pivot in range(self.group_count):
                    if pivot not in (h, ell) and counts[pivot]:
                        total += counts[pivot] * children[pivot].cross[h, ell]
                cross[h, ell] = cross[ell, h] = total / size
        return InvariantMatrix(diagonal, within, cross)

    def bellman_iterative(self, depth: int) -> InvariantMatrix:
        """Layered equivalent of ``bellman`` for depths beyond Python's stack guard."""
        total = sum(self.counts)
        leaf_size = total - depth
        if not 1 <= leaf_size < total:
            raise ValueError("depth must leave at least one coordinate")

        def states_of_size(size: int):
            # The route uses this method for two/three groups at very large n;
            # a small recursive product avoids a dependency on itertools.product
            # materialization.
            state = [0] * self.group_count

            def generate(group: int, remaining: int):
                if group == self.group_count - 1:
                    if 0 <= remaining <= self.counts[group]:
                        state[group] = remaining
                        yield tuple(state)
                    return
                lower = max(0, remaining - sum(self.counts[group + 1 :]))
                upper = min(self.counts[group], remaining)
                for value in range(lower, upper + 1):
                    state[group] = value
                    yield from generate(group + 1, remaining - value)

            yield from generate(0, size)

        current: dict[tuple[int, ...], InvariantMatrix] = {}
        for state in states_of_size(leaf_size):
            current[state] = self._leaf(state)
        self.states_evaluated += len(current)
        for size in range(leaf_size + 1, total + 1):
            following: dict[tuple[int, ...], InvariantMatrix] = {}
            for state in states_of_size(size):
                children: dict[int, InvariantMatrix] = {}
                valid = True
                for pivot, count in enumerate(state):
                    if count == 0:
                        continue
                    mutable = list(state)
                    mutable[pivot] -= 1
                    child_state = tuple(mutable)
                    if child_state not in current:
                        valid = False
                        break
                    children[pivot] = current[child_state]
                if valid:
                    following[state] = self._lift_from_children(state, children)
            current = following
            self.states_evaluated += len(current)
        return current[self.counts]

    def coefficient(self, depth: int) -> dict[str, object]:
        # functools.lru_cache adds several Python frames per recursive level.
        required_limit = 20 * depth + 5000
        if sys.getrecursionlimit() < required_limit:
            sys.setrecursionlimit(required_limit)
        if depth >= 900:
            value = self.bellman_iterative(depth)
        else:
            value = self.bellman(self.counts, depth)
        active, original_reduced = self.reduced_original(self.counts)
        h_reduced = np.zeros_like(original_reduced)
        for ii, g in enumerate(active):
            count = self.counts[g]
            h_reduced[ii, ii] = value.diagonal[g] + (count - 1) * value.within[g]
            for jj, h in enumerate(active[:ii]):
                entry = math.sqrt(count * self.counts[h]) * value.cross[g, h]
                h_reduced[ii, jj] = h_reduced[jj, ii] = entry
        root = _symmetric_sqrt(original_reduced)
        normalized_reduced = root @ h_reduced @ root
        constant_values = np.linalg.eigvalsh((normalized_reduced + normalized_reduced.T) / 2.0)
        candidates: list[tuple[float, str]] = [
            (float(constant_values[0]), "group_constant")
        ]
        transverse_values: dict[str, float] = {}
        for g, count in enumerate(self.counts):
            if count > 1:
                candidate = (1.0 - self.within_a[g]) * (
                    value.diagonal[g] - value.within[g]
                )
                transverse_values[str(g)] = float(candidate)
                candidates.append((float(candidate), f"group_{g}_transverse"))
        coefficient, sector = min(candidates)
        root_eigenvalue_list = list(np.linalg.eigvalsh(original_reduced))
        for g, count in enumerate(self.counts):
            if count > 1:
                root_eigenvalue_list.append(1.0 - self.within_a[g])
        return {
            "coefficient": coefficient,
            "sector": sector,
            "constant_block_eigenvalues": [float(x) for x in constant_values],
            "transverse_coefficients": transverse_values,
            "root_min_eigenvalue": float(min(root_eigenvalue_list)),
            "root_max_eigenvalue": float(max(root_eigenvalue_list)),
            "states_evaluated": self.states_evaluated,
            "leaf_underflows": self.leaf_underflows,
            "certificate": value,
        }


def lift_from_reduced_gram(
    counts: Sequence[int], vectors: np.ndarray, mu: float
) -> tuple[np.ndarray, np.ndarray]:
    """Create A=mu I+(1-mu)C from a PSD group-constant Gram block.

    ``vectors @ vectors.T`` is the reduced block of the boundary correlation
    ``C`` in the orthonormal group-indicator basis.  Its diagonal must lie in
    ``[0, counts[g]]``.  Rank deficiency makes ``lambda_min(A)=mu``.
    """
    counts_array = np.asarray(counts, dtype=float)
    reduced = vectors @ vectors.T
    within_c = np.zeros(len(counts))
    for g, count in enumerate(counts):
        if count == 1:
            if abs(reduced[g, g] - 1.0) > 1e-8:
                raise ValueError("a singleton reduced diagonal must equal one")
            within_c[g] = 0.0
        else:
            within_c[g] = (reduced[g, g] - 1.0) / (count - 1.0)
            if not (-1.0 / (count - 1.0) - 1e-10 <= within_c[g] <= 1.0 + 1e-10):
                raise ValueError("invalid within-group correlation")
    cross_c = np.zeros((len(counts), len(counts)))
    for g in range(len(counts)):
        for h in range(g):
            value = reduced[g, h] / math.sqrt(counts_array[g] * counts_array[h])
            cross_c[g, h] = cross_c[h, g] = value
    return (1.0 - mu) * within_c, (1.0 - mu) * cross_c


def vectors_from_directions(
    counts: Sequence[int], directions: np.ndarray, mass_fractions: Sequence[float]
) -> np.ndarray:
    directions = np.asarray(directions, dtype=float)
    directions = directions / np.linalg.norm(directions, axis=1)[:, None]
    masses = np.sqrt(np.asarray(counts, dtype=float) * np.asarray(mass_fractions, dtype=float))
    return directions * masses[:, None]


def brute_determinant_tail(
    matrix: np.ndarray, depth: int, leaf_mode: str = "determinant"
) -> np.ndarray:
    """Generic 2**n float64 control, used only in small dimensions."""
    n = matrix.shape[0]

    def deletion(block: np.ndarray, index: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        size = block.shape[0]
        keep = [j for j in range(size) if j != index]
        selector = np.eye(size)[keep, :]
        unit = np.eye(size)[:, index]
        lift = selector @ (np.eye(size) - np.outer(block[:, index], unit))
        return block[np.ix_(keep, keep)], lift, unit

    def indices(mask: int) -> list[int]:
        return [i for i in range(n) if mask & (1 << i)]

    @lru_cache(maxsize=None)
    def recurse(mask: int, remaining_depth: int) -> np.ndarray:
        selected = indices(mask)
        block = matrix[np.ix_(selected, selected)]
        size = len(selected)
        if size == 1:
            return np.ones((1, 1))
        if remaining_depth == 0:
            if leaf_mode == "zero":
                return np.zeros_like(block)
            if leaf_mode != "determinant":
                raise ValueError(leaf_mode)
            return np.linalg.det(block) * np.linalg.inv(block)
        result = np.zeros_like(block)
        for local, global_index in enumerate(selected):
            _, lift, unit = deletion(block, local)
            result += np.outer(unit, unit) + lift.T @ recurse(
                mask ^ (1 << global_index), remaining_depth - 1
            ) @ lift
        return result / size

    return recurse((1 << n) - 1, depth)


def _jsonable_result(result: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in result.items() if key != "certificate"}


def run_controls() -> dict[str, object]:
    started = time.time()
    counts = (2, 2, 2)
    directions = np.array([[1.0, 0.0], [-0.4, 0.916515138991168], [-0.7, -0.714142842854285]])
    vectors = vectors_from_directions(counts, directions, (0.8, 0.55, 0.7))
    within, cross = lift_from_reduced_gram(counts, vectors, 0.17)
    dp = ExchangeableTailDP(counts, within, cross)
    depth = 3
    result = dp.coefficient(depth)
    symmetry_full = representation_to_full(counts, result["certificate"])
    generic_full = brute_determinant_tail(dp.root_matrix(), depth)
    residual = float(np.max(np.abs(symmetry_full - generic_full)))

    signs = np.array([1.0, -1.0, -1.0])
    signed_cross = cross * np.outer(signs, signs)
    signed = ExchangeableTailDP(counts, within, signed_cross).coefficient(depth)

    rank_n = 1000
    rank_mu = 0.98
    rank_dp = ExchangeableTailDP((rank_n,), ((1.0 - rank_mu),), np.zeros((1, 1)))
    rank_result = rank_dp.coefficient((rank_n + 1) // 2)
    rank_ratio = rank_result["coefficient"] / rank_mu

    identity_n = 25
    identity_dp = ExchangeableTailDP((identity_n,), (0.0,), np.zeros((1, 1)))
    identity = identity_dp.coefficient((identity_n + 1) // 2)
    return {
        "evidence_level": "E2 finite implementation controls; float64 comparisons",
        "subset_dp_max_abs_residual": residual,
        "subset_dp_pass_tolerance": residual < 2e-10,
        "group_sign_conjugation_gap": float(abs(result["coefficient"] - signed["coefficient"])),
        "group_sign_conjugation_pass_tolerance": abs(result["coefficient"] - signed["coefficient"]) < 2e-10,
        "signed_rank_one_control": {
            "n": rank_n,
            "mu": rank_mu,
            "ratio": float(rank_ratio),
            "margin_over_half": float(rank_ratio - 0.5),
            "sector": rank_result["sector"],
        },
        "identity_control": {
            "n": identity_n,
            "coefficient": identity["coefficient"],
            "expected": 1.0,
            "absolute_gap": abs(identity["coefficient"] - 1.0),
        },
        "elapsed_seconds": time.time() - started,
    }


def evaluate_family(
    name: str,
    counts: Sequence[int],
    directions: np.ndarray,
    masses: Sequence[float],
    mu: float,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    vectors = vectors_from_directions(counts, directions, masses)
    within, cross = lift_from_reduced_gram(counts, vectors, mu)
    dp = ExchangeableTailDP(counts, within, cross)
    depth = (sum(counts) + 1) // 2
    result = _jsonable_result(dp.coefficient(depth))
    actual_mu = result["root_min_eigenvalue"]
    return {
        "name": name,
        "counts": list(counts),
        "n": int(sum(counts)),
        "depth": depth,
        "mu_parameter": float(mu),
        "actual_mu": float(actual_mu),
        "ratio": float(result["coefficient"] / actual_mu),
        "margin_over_half": float(result["coefficient"] / actual_mu - 0.5),
        "directions": np.asarray(directions, dtype=float).tolist(),
        "mass_fractions": [float(x) for x in masses],
        "within": within.tolist(),
        "cross": cross.tolist(),
        "result": result,
        "metadata": metadata or {},
    }


def _random_unit_rows(rng: np.random.Generator, rows: int, columns: int) -> np.ndarray:
    values = rng.normal(size=(rows, columns))
    values /= np.linalg.norm(values, axis=1)[:, None]
    return values


def search_frustrated_three(seed: int, evaluations: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    counts = (20, 20, 20)
    best: dict[str, object] | None = None
    started = time.time()
    for evaluation in range(evaluations):
        if evaluation == 0:
            angles = np.array([0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0])
            masses = np.array([0.98, 0.98, 0.98])
            mu = 0.98
        else:
            angles = rng.uniform(0.0, 2.0 * math.pi, size=3)
            masses = 0.15 + 0.849 * rng.beta(2.0, 0.7, size=3)
            selector = rng.random()
            mu = (
                1.0 - 10.0 ** rng.uniform(-3.5, -0.6)
                if selector < 0.55
                else 10.0 ** rng.uniform(-4.0, -0.05)
            )
        directions = np.column_stack((np.cos(angles), np.sin(angles)))
        item = evaluate_family(
            "frustrated_three",
            counts,
            directions,
            masses,
            mu,
            {"evaluation": evaluation, "angles": angles.tolist()},
        )
        if best is None or item["ratio"] < best["ratio"]:
            best = item
    assert best is not None
    return {
        "avenue": "three exchangeable groups with a frustrated rank-two constant block",
        "seed": seed,
        "evaluations": evaluations,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def search_multiscale_four(seed: int, evaluations: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    counts = (8, 13, 21, 34)
    best: dict[str, object] | None = None
    started = time.time()
    for evaluation in range(evaluations):
        raw = _random_unit_rows(rng, 4, 3)
        scale = 10.0 ** rng.uniform(-3.0, -0.15)
        anisotropy = np.diag([1.0, scale, scale * scale])
        directions = raw @ anisotropy
        directions /= np.linalg.norm(directions, axis=1)[:, None]
        masses = np.clip(rng.beta(0.65, 0.65, size=4), 2e-3, 0.998)
        # Both a tiny global floor and an interior/high-floor degeneration are sampled.
        if rng.random() < 0.5:
            mu = 10.0 ** rng.uniform(-5.0, -0.3)
        else:
            mu = 1.0 - 10.0 ** rng.uniform(-3.5, -0.2)
        item = evaluate_family(
            "multiscale_four",
            counts,
            directions,
            masses,
            mu,
            {"evaluation": evaluation, "anisotropy_scale": float(scale)},
        )
        if best is None or item["ratio"] < best["ratio"]:
            best = item
    assert best is not None
    return {
        "avenue": "four uneven exchangeable groups with rank-three multiscale Gram geometry",
        "seed": seed,
        "evaluations": evaluations,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def search_star_pole(seed: int, evaluations: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    counts = (2, 18, 18, 18)
    best: dict[str, object] | None = None
    started = time.time()
    simplex = np.array(
        [
            [1.0, 0.0],
            [-0.5, math.sqrt(3.0) / 2.0],
            [-0.5, -math.sqrt(3.0) / 2.0],
        ]
    )
    for evaluation in range(evaluations):
        latitude = rng.uniform(-0.98, 0.98)
        leaf = np.column_stack(
            (
                np.full(3, latitude),
                math.sqrt(1.0 - latitude * latitude) * simplex,
            )
        )
        directions = np.vstack(([1.0, 0.0, 0.0], leaf))
        masses = np.array(
            [
                1.0,
                *np.clip(rng.beta(0.7, 0.7, size=3), 0.002, 0.998),
            ]
        )
        mu = (
            10.0 ** rng.uniform(-5.0, -0.1)
            if rng.random() < 0.55
            else 1.0 - 10.0 ** rng.uniform(-4.0, -0.25)
        )
        item = evaluate_family(
            "star_pole",
            counts,
            directions,
            masses,
            mu,
            {"evaluation": evaluation, "latitude": float(latitude)},
        )
        if best is None or item["ratio"] < best["ratio"]:
            best = item
    assert best is not None
    return {
        "avenue": "duplicate pole group coupled to three simplex-arranged exchangeable leaves",
        "seed": seed,
        "evaluations": evaluations,
        "best": best,
        "elapsed_seconds": time.time() - started,
    }


def run_search(seed: int, evaluations: int) -> dict[str, object]:
    started = time.time()
    controls = run_controls()
    per = max(1, evaluations // 3)
    avenues = [
        search_frustrated_three(seed + 11, per),
        search_multiscale_four(seed + 23, per),
        search_star_pole(seed + 37, evaluations - 2 * per),
    ]
    best = min((avenue["best"] for avenue in avenues), key=lambda item: item["ratio"])
    return {
        "schema_version": "1.0",
        "evidence_level": "E1 float64 structured null search; absence of a violation is not proof",
        "candidate": "H_ceil(n/2)(A) >= (mu/2) A^{-1}",
        "seed": seed,
        "total_evaluations": evaluations,
        "controls": controls,
        "avenues": avenues,
        "global_best": best,
        "violation_found_float64": bool(best["margin_over_half"] < -1e-8),
        "warning": "Any apparent negative margin requires independent high-precision and exact/interval reconstruction.",
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "elapsed_seconds": time.time() - started,
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "search"), default="search")
    parser.add_argument("--seed", type=int, default=202608215)
    parser.add_argument("--evaluations", type=int, default=90)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("search.json"),
    )
    args = parser.parse_args()
    if args.mode == "controls":
        result = run_controls()
    else:
        result = run_search(args.seed, args.evaluations)
    write_json(args.output, result)
    print(json.dumps({"output": str(args.output), "result": result if args.mode == "controls" else result["global_best"]}, indent=2))


if __name__ == "__main__":
    main()
