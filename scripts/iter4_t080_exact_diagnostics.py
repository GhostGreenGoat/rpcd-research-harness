"""Deterministic exact diagnostics for Iteration-4 task T080.

This script does not prove the general boundary inequality.  It records exact
finite witnesses and checks algebraic identities used by the accompanying
proof-search document.  All matrix arithmetic is over ``sympy.Rational``.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations
from pathlib import Path

import sympy as sp


def ordered_factor(correlation: sp.Matrix, order: tuple[int, ...]) -> sp.Matrix:
    """Return M_order in the original coordinate labels."""
    n = correlation.rows
    permutation = sp.eye(n)[:, list(order)]
    permuted = permutation.T * correlation * permutation
    lower = sp.Matrix(
        n,
        n,
        lambda row, column: permuted[row, column] if row >= column else 0,
    )
    return permutation * lower * permutation.T


def expected_inverse_gram(correlation: sp.Matrix) -> sp.Matrix:
    n = correlation.rows
    result = sp.zeros(n)
    orders = list(permutations(range(n)))
    for order in orders:
        inverse = ordered_factor(correlation, order).inv()
        result += inverse.T * inverse
    return sp.simplify(result / len(orders))


def projector_onto_ones_complement(n: int) -> sp.Matrix:
    ones = sp.ones(n, 1)
    return sp.eye(n) - ones * ones.T / n


def rational_matrix(matrix: sp.Matrix) -> list[list[str]]:
    return [[str(sp.factor(matrix[i, j])) for j in range(matrix.cols)] for i in range(matrix.rows)]


def quadratic_ratio(matrix: sp.Matrix, vector: sp.Matrix) -> sp.Expr:
    return sp.factor((vector.T * matrix * vector)[0] / vector.dot(vector))


def rank_one_checks() -> dict[str, object]:
    records: dict[str, object] = {}
    for n in range(2, 7):
        correlation = sp.ones(n)
        computed = expected_inverse_gram(correlation)
        claimed = 2 * projector_onto_ones_complement(n) + sp.eye(n) / n
        residual = sp.simplify(computed - claimed)
        assert residual == sp.zeros(n)
        records[str(n)] = {
            "orders": int(sp.factorial(n)),
            "identity_residual_zero": True,
            "kernel_eigenvalue": str(2 + sp.Rational(1, n)),
            "range_eigenvalue": str(sp.Rational(1, n)),
        }
    return records


def reverse_and_cycle_witnesses() -> dict[str, object]:
    # Reverse-pair obstruction for J_3.
    c3 = sp.ones(3)
    m3 = ordered_factor(c3, (0, 1, 2))
    b3 = m3.inv()
    reverse_pair = (b3.T * b3 + b3 * b3.T) / 2
    u3 = sp.Matrix([1, 0, -1])
    reverse_ratio = quadratic_ratio(reverse_pair, u3)
    assert reverse_ratio == sp.Rational(3, 2)

    # Average all rotations of the natural J_4 cycle and their reversals.
    c4 = sp.ones(4)
    cycle_orders: list[tuple[int, ...]] = []
    base = (0, 1, 2, 3)
    for shift in range(4):
        rotation = base[shift:] + base[:shift]
        cycle_orders.extend([rotation, tuple(reversed(rotation))])
    cycle_average = sp.zeros(4)
    for order in cycle_orders:
        inverse = ordered_factor(c4, order).inv()
        cycle_average += inverse.T * inverse
    cycle_average /= len(cycle_orders)
    u4 = sp.Matrix([1, 0, -1, 0])
    cycle_ratio = quadratic_ratio(cycle_average, u4)
    assert cycle_ratio == sp.Rational(7, 4)

    return {
        "J3_reverse_pair": {
            "order": [1, 2, 3],
            "inverse": rational_matrix(b3),
            "kernel_vector": [1, 0, -1],
            "rayleigh_ratio": str(reverse_ratio),
            "target": "2",
        },
        "J4_cycle_dihedral_orbit": {
            "orders_count": len(cycle_orders),
            "kernel_vector": [1, 0, -1, 0],
            "rayleigh_ratio": str(cycle_ratio),
            "target": "2",
        },
    }


def volume_circuit_identity(vectors: sp.Matrix) -> dict[str, object]:
    """Check the volume-sampled oblique-projector identities exactly.

    ``vectors`` is r-by-n with its Gram columns representing the correlation
    vectors (unit norms are not needed for this algebraic identity).
    """
    rank, n = vectors.shape
    frame = vectors * vectors.T
    normalizer = sp.factor(frame.det())
    assert normalizer != 0
    expected_g = sp.zeros(n)
    expected_ggt = sp.zeros(n)
    singular_correction = sp.zeros(n)
    weight_sum = sp.Integer(0)
    identity = sp.eye(n)
    range_projector = sp.simplify(vectors.T * frame.inv() * vectors)
    kernel_projector = sp.simplify(identity - range_projector)
    singular_subsets = 0
    for subset in combinations(range(n), rank):
        basis = vectors[:, list(subset)]
        weight = sp.factor(basis.det() ** 2)
        selector = identity[:, list(subset)]
        if weight == 0:
            singular_subsets += 1
            singular_correction += selector * range_projector.extract(subset, subset).adjugate() * selector.T
            continue
        oblique = identity - selector * basis.inv() * vectors
        expected_g += weight * oblique
        expected_ggt += weight * oblique * oblique.T
        weight_sum += weight
    expected_g = sp.simplify(expected_g / normalizer)
    expected_ggt = sp.simplify(expected_ggt / normalizer)
    singular_correction = sp.simplify(singular_correction)
    residual_first = sp.simplify(expected_g - kernel_projector)
    residual_second = sp.simplify(
        expected_ggt - ((rank + 1) * kernel_projector - singular_correction)
    )
    assert sp.factor(weight_sum - normalizer) == 0
    assert residual_first == sp.zeros(n)
    assert residual_second == sp.zeros(n)
    return {
        "rank": rank,
        "n": n,
        "normalizer": str(normalizer),
        "weights_sum_to_normalizer": True,
        "E_G_equals_Pker": True,
        "singular_r_subsets": singular_subsets,
        "general_position": singular_subsets == 0,
        "corrected_E_GGt_identity": True,
        "uncorrected_E_GGt_identity": expected_ggt == (rank + 1) * kernel_projector,
        "singular_correction_trace": str(sp.factor(sp.trace(singular_correction))),
    }


def volume_checks() -> list[dict[str, object]]:
    examples = [
        sp.Matrix([[1, 1, 1, 1]]),
        sp.Matrix([[1, 0, 1, 2], [0, 1, 1, -1]]),
        sp.Matrix([[1, 0, 0, 1, 2], [0, 1, 0, 1, -1], [0, 0, 1, 1, 1]]),
        # Unit columns, but {0,1} is a zero-volume rank-two subset.
        sp.Matrix([[1, 1, 0], [0, 0, 1]]),
    ]
    return [volume_circuit_identity(vectors) for vectors in examples]


def regular_simplex_checks() -> dict[str, object]:
    records: dict[str, object] = {}
    for n in range(3, 9):
        rho = -sp.Rational(1, n - 1)
        correlation = sp.ones(n) * rho + sp.eye(n) * (1 - rho)
        computed = expected_inverse_gram(correlation)
        ones = sp.ones(n, 1)
        coefficient = sp.factor((ones.T * computed * ones)[0] / n)
        q = sp.Rational(n, n - 1)
        claimed = sp.factor(sum(q ** (2 * k) for k in range(n)) / n)
        assert sp.factor(coefficient - claimed) == 0
        records[str(n)] = {
            "kernel_coefficient": str(coefficient),
            "formula": str(claimed),
            "gap_to_2": str(sp.factor(coefficient - 2)),
        }
    return records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER4_T080_EXACT_DIAGNOSTICS_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {
        "status": (
            "E2 exact finite diagnostics plus instances of separately derived algebraic identities; "
            "not a proof of T080"
        ),
        "arithmetic": "sympy exact rational arithmetic",
        "rank_one": rank_one_checks(),
        "local_group_obstructions": reverse_and_cycle_witnesses(),
        "volume_circuit_examples": volume_checks(),
        "regular_simplex": regular_simplex_checks(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
