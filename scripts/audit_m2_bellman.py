"""Deterministic float64 regression checks for ITER3 M2.

These checks are finite numerical evidence only.  The audit document contains
the independent algebraic reconstruction.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import permutations
from math import factorial

import numpy as np


SEED = 20260821
TOL = 5e-10


def deletion_data(matrix: np.ndarray, index: int):
    size = matrix.shape[0]
    keep = [j for j in range(size) if j != index]
    delete = np.eye(size)[keep, :]
    unit = np.eye(size)[:, index]
    lift = delete @ (np.eye(size) - np.outer(matrix[:, index], unit))
    child = matrix[np.ix_(keep, keep)]
    return child, lift, unit[:, None]


def exact_decrease(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    if size == 1:
        return np.ones((1, 1))
    result = np.zeros_like(matrix)
    for index in range(size):
        child, lift, unit = deletion_data(matrix, index)
        result += unit @ unit.T + lift.T @ exact_decrease(child) @ lift
    return result / size


def determinant_tail(matrix: np.ndarray, depth: int) -> np.ndarray:
    size = matrix.shape[0]
    if size == 1:
        return np.ones((1, 1))
    if depth == 0:
        return np.linalg.det(matrix) * np.linalg.inv(matrix)
    result = np.zeros_like(matrix)
    for index in range(size):
        child, lift, unit = deletion_data(matrix, index)
        result += unit @ unit.T + lift.T @ determinant_tail(child, depth - 1) @ lift
    return result / size


def epoch_observable(matrix: np.ndarray) -> np.ndarray:
    size = matrix.shape[0]
    total = np.zeros_like(matrix)
    identity = np.eye(size)
    for order in permutations(range(size)):
        transform = identity.copy()
        for index in order:
            unit = identity[:, index]
            update = identity - np.outer(unit, unit @ matrix)
            transform = update @ transform
        total += transform.T @ matrix @ transform
    return total / factorial(size)


def main() -> None:
    rng = np.random.default_rng(SEED)
    max_leverage = 0.0
    max_h1 = 0.0
    max_j2 = 0.0
    max_final = 0.0
    max_epoch = 0.0
    min_monotone = np.inf
    count = 0

    for size in range(2, 7):
        for repetition in range(30):
            raw = rng.normal(size=(size, size + 2))
            matrix = raw @ raw.T
            scaling = np.sqrt(np.diag(matrix))
            matrix = matrix / scaling[:, None] / scaling[None, :]
            inverse = np.linalg.inv(matrix)
            determinant = np.linalg.det(matrix)
            h1_direct = np.zeros_like(matrix)
            j2_direct = np.zeros_like(matrix)

            for index in range(size):
                child, lift, unit = deletion_data(matrix, index)
                defect = (
                    inverse
                    - unit @ unit.T
                    - lift.T @ np.linalg.inv(child) @ lift
                )
                schur = 1.0 / inverse[index, index]
                leverage = (
                    schur
                    * (inverse - np.eye(size))
                    @ unit
                    @ unit.T
                    @ (inverse - np.eye(size))
                )
                max_leverage = max(
                    max_leverage, float(np.max(np.abs(defect - leverage)))
                )
                child_determinant = np.linalg.det(child)
                h1_direct += (
                    unit @ unit.T
                    + child_determinant * lift.T @ np.linalg.inv(child) @ lift
                ) / size
                j2_direct += (
                    unit @ unit.T + lift.T @ lift / (size - 1)
                ) / size

            h1_formula = (
                determinant * np.trace(inverse) * inverse
                - determinant * (inverse - np.eye(size)) @ (inverse - np.eye(size))
                + np.eye(size)
                - determinant * np.diag(np.diag(inverse))
            ) / size
            j2_formula = (
                (2 * size - 1) * np.eye(size)
                - 2 * matrix
                + np.diag(np.diag(matrix @ matrix))
            ) / (size * (size - 1))
            max_h1 = max(max_h1, float(np.max(np.abs(h1_direct - h1_formula))))
            max_j2 = max(max_j2, float(np.max(np.abs(j2_direct - j2_formula))))
            min_monotone = min(
                min_monotone,
                float(
                    np.linalg.eigvalsh(h1_direct - determinant * inverse)[0]
                ),
            )
            count += 1

            if repetition == 0:
                exact = exact_decrease(matrix)
                levels = [determinant_tail(matrix, depth) for depth in range(size)]
                for left, right in zip(levels, levels[1:]):
                    min_monotone = min(
                        min_monotone,
                        float(np.linalg.eigvalsh(right - left)[0]),
                    )
                max_final = max(
                    max_final, float(np.max(np.abs(levels[-1] - exact)))
                )
                if size <= 5:
                    observable = epoch_observable(matrix)
                    residual_formula = matrix - matrix @ exact @ matrix
                    max_epoch = max(
                        max_epoch,
                        float(np.max(np.abs(observable - residual_formula))),
                    )

    # Exact arithmetic for the structured m=3, mu=1/5 barrier.
    determinant = Fraction(13, 125)
    inverse_trace = Fraction(135, 13)
    inverse_diagonal = Fraction(45, 13)
    inverse_minspace = Fraction(5, 1)
    h1_minspace = (
        determinant * inverse_trace * inverse_minspace
        - determinant * (inverse_minspace - 1) ** 2
        + 1
        - determinant * inverse_diagonal
    ) / 3
    coefficient = h1_minspace / inverse_minspace
    target_decrease = 1 - Fraction(14, 15) ** 6
    gap = target_decrease - coefficient
    assert coefficient == Fraction(547, 1875)
    assert gap == Fraction(538064, 11390625)

    assert max_leverage < TOL
    assert max_h1 < TOL
    assert max_j2 < TOL
    assert max_final < TOL
    assert max_epoch < TOL
    assert min_monotone > -TOL

    print(
        {
            "seed": SEED,
            "tolerance": TOL,
            "random_matrices": count,
            "max_leverage_residual": max_leverage,
            "max_H1_residual": max_h1,
            "max_J2_residual": max_j2,
            "max_final_H_minus_K_residual": max_final,
            "max_epoch_identity_residual": max_epoch,
            "min_monotonicity_eigenvalue": min_monotone,
            "barrier_coefficient": str(coefficient),
            "barrier_gap": str(gap),
        }
    )


if __name__ == "__main__":
    main()
