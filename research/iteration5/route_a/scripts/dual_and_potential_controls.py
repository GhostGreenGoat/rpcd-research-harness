"""Exact controls for Iteration 5 route A.

This file does not test the half-depth conjecture itself.  It reconstructs two
strict obstructions to tempting closure steps:

1. Bellman induction with the *actual* child spectral floors still fails.
2. The new random-order dual certificate is too weak if its test matrix is
   restricted to diagonal weights depending only on permutation position.

All sign decisions below use ``sympy.Rational``.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def deletion_lift(matrix: sp.Matrix, pivot: int) -> tuple[sp.Matrix, sp.Matrix]:
    n = matrix.rows
    keep = [j for j in range(n) if j != pivot]
    child = matrix.extract(keep, keep)
    lift = sp.zeros(n - 1, n)
    for local, coordinate in enumerate(keep):
        lift[local, coordinate] = 1
        lift[local, pivot] = -matrix[coordinate, pivot]
    return child, lift


def child_floor_potential_failure() -> dict[str, object]:
    eps = Q(1, 100)
    vectors = sp.Matrix(
        [
            [0, 1],
            [Q(4, 5), Q(3, 5)],
            [Q(5, 13), Q(12, 13)],
            [Q(7, 25), Q(24, 25)],
        ]
    )
    boundary = vectors * vectors.T
    matrix = eps * sp.eye(4) + (1 - eps) * boundary

    # The boundary and every three-row deletion have rank two.  Hence the
    # parent and all children have exact spectral floor eps after the lift.
    assert boundary.rank() == 2
    child_ranks = []
    certificate = sp.eye(4) / 4
    for pivot in range(4):
        child, lift = deletion_lift(matrix, pivot)
        keep = [j for j in range(4) if j != pivot]
        child_boundary = boundary.extract(keep, keep)
        child_ranks.append(child_boundary.rank())
        assert child_boundary.rank() == 2
        certificate += eps * lift.T * child.inv() * lift / 8

    difference = certificate - eps * matrix.inv() / 2
    witness = sp.Matrix([1, 1, -1, -1])
    quadratic = sp.factor((witness.T * difference * witness)[0])
    assert quadratic < 0
    return {
        "status": "exact counterexample to a proof step",
        "epsilon": str(eps),
        "boundary_rank": boundary.rank(),
        "child_boundary_ranks": child_ranks,
        "boundary_gram": [[str(x) for x in boundary.row(i)] for i in range(4)],
        "witness": list(map(int, witness)),
        "quadratic_form": str(quadratic),
        "failed_inequality": (
            "I/4 + (1/4) sum_i (mu_i/2) L_i^T C_i^{-1} L_i "
            ">= (mu/2) B^{-1}, even with mu_i=lambda_min(C_i)=mu"
        ),
    }


def position_quadratic(n: int) -> sp.Matrix:
    """Penalty on a transverse vector at the signed-rank-one boundary.

    For positional weights r_0,...,r_(n-1), the dual certificate described in
    the accompanying note has transverse value

        2 b^T r - r^T Q r,  b=1/n.
    """

    matrix = sp.zeros(n)
    for i in range(n):
        matrix[i, i] = Q(i + 1, n)
        for j in range(i):
            matrix[i, j] = matrix[j, i] = -Q(1 + min(i, j), n * (n - 1))
    return matrix


def exact_ldl_pivots(matrix: sp.Matrix) -> list[sp.Rational]:
    """No-pivot exact LDL decomposition, returning the diagonal pivots."""

    n = matrix.rows
    lower = sp.eye(n)
    pivots: list[sp.Rational] = []
    for i in range(n):
        pivot = sp.factor(
            matrix[i, i]
            - sum(lower[i, k] * lower[i, k] * pivots[k] for k in range(i))
        )
        pivots.append(pivot)
        assert pivot > 0
        for j in range(i + 1, n):
            lower[j, i] = sp.factor(
                (
                    matrix[j, i]
                    - sum(
                        lower[j, k] * lower[i, k] * pivots[k]
                        for k in range(i)
                    )
                )
                / pivot
            )
    assert sp.simplify(lower * sp.diag(*pivots) * lower.T - matrix) == sp.zeros(n)
    return pivots


def positional_dual_failure(n: int = 20) -> dict[str, object]:
    matrix = position_quadratic(n)
    pivots = exact_ldl_pivots(matrix)
    linear = sp.ones(n, 1) / n
    optimizer = matrix.inv() * linear
    optimum = sp.factor((linear.T * optimizer)[0])
    gap = sp.factor(optimum - Q(1, 2))
    assert gap < 0
    return {
        "status": "exact obstruction to the positional-diagonal dual subclass",
        "dimension": n,
        "quadratic_matrix_formula": (
            "Q_ii=(i+1)/n and Q_ij=-(1+min(i,j))/(n(n-1)), "
            "with zero-based positions"
        ),
        "positive_definite": all(pivot > 0 for pivot in pivots),
        "minimum_ldl_pivot": str(min(pivots)),
        "optimal_transverse_boundary_value": str(optimum),
        "gap_to_one_half": str(gap),
        "optimizer_first_five": [str(x) for x in optimizer[:5, 0]],
        "scope": (
            "This rules out only R_pi diagonal with weights determined by "
            "permutation position.  The unrestricted random matrix R_pi, "
            "especially adjacency/path states, remains open."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_a/evidence/dual_and_potential_controls.json"
        ),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact finite controls",
        "child_floor_potential": child_floor_potential_failure(),
        "positional_dual": positional_dual_failure(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
