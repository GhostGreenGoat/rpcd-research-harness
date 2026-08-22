"""Exact counterexample to the unrestricted duplicate-direction child lemma.

The rejected lemma was

    ((I + B)e_i)^T K_0(B) ((I + B)e_i) >= 3,

where ``K_0(B) = E[(M_pi M_pi^T)^-1]``.  The matrix below is the Gram
matrix of two copies of a pole and an equilateral triangle at latitude 4/5.
All entries are rational, so the subset Bellman recursion is checked over
``sympy.Rational`` rather than in floating point.

This refutes only that proposed induction lemma.  It is not a counterexample
to T080 or to the RPCD rate conjecture.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


def counterexample_matrix() -> sp.Matrix:
    q = sp.Rational
    return sp.Matrix(
        [
            [1, 1, q(4, 5), q(4, 5), q(4, 5)],
            [1, 1, q(4, 5), q(4, 5), q(4, 5)],
            [q(4, 5), q(4, 5), 1, q(23, 50), q(23, 50)],
            [q(4, 5), q(4, 5), q(23, 50), 1, q(23, 50)],
            [q(4, 5), q(4, 5), q(23, 50), q(23, 50), 1],
        ]
    )


def exact_remaining_set_k(correlation: sp.Matrix) -> sp.Matrix:
    """Evaluate K_0 through the exact first-coordinate subset recursion."""
    n = correlation.rows
    values: list[sp.Matrix | None] = [None] * (1 << n)
    values[0] = sp.zeros(0)
    for mask in range(1, 1 << n):
        indices = [index for index in range(n) if mask & (1 << index)]
        child_matrix = correlation.extract(indices, indices)
        dimension = len(indices)
        total = sp.zeros(dimension)
        for position, index in enumerate(indices):
            child = values[mask ^ (1 << index)]
            assert child is not None
            immediate = sp.zeros(dimension)
            immediate[position, position] = 1
            keep = [j for j in range(dimension) if j != position]
            selector = sp.eye(dimension).extract(keep, range(dimension))
            coordinate = sp.eye(dimension)[:, position]
            transition = selector * (
                sp.eye(dimension) - child_matrix[:, position] * coordinate.T
            )
            total += immediate + transition.T * child * transition
        values[mask] = total / dimension
    result = values[-1]
    assert result is not None
    return result


def exact_record() -> dict[str, object]:
    matrix = counterexample_matrix()
    # A rational Gram factor is not needed: the exact eigenvalues below prove
    # positive semidefiniteness and the geometric construction proves it too.
    characteristic = sp.factor(matrix.charpoly().as_expr())
    expected_characteristic = sp.Symbol("lambda") ** 2 * (
        sp.Symbol("lambda") - sp.Rational(27, 50)
    ) ** 2 * (sp.Symbol("lambda") - sp.Rational(196, 50))
    assert sp.expand(characteristic - expected_characteristic) == 0

    k_zero = exact_remaining_set_k(matrix)
    coordinate = sp.eye(5)[:, 0]
    z = (sp.eye(5) + matrix) * coordinate
    value = sp.factor((z.T * k_zero * z)[0])
    gap = sp.factor(value - 3)
    expected_value = sp.Rational(7204453277, 2441406250)
    expected_gap = -sp.Rational(119765473, 2441406250)
    assert value == expected_value
    assert gap == expected_gap
    assert gap < 0
    return {
        "schema_version": "1.0",
        "evidence_level": "E2",
        "status": "exact finite counterexample to the duplicate-child lemma",
        "scope_warning": "This does not refute T080 or the RPCD complexity conjecture.",
        "matrix": [[str(entry) for entry in row] for row in matrix.tolist()],
        "geometry": "two identical poles plus an equilateral latitude-4/5 ring",
        "characteristic_polynomial": str(characteristic),
        "tested_coordinate_zero_based": 0,
        "z": [str(entry) for entry in z],
        "value": str(value),
        "gap_to_three": str(gap),
        "decimal_value": str(sp.N(value, 18)),
        "checks": {
            "correlation_psd_from_exact_spectrum": True,
            "subset_bellman_recursion_exact": True,
            "strict_gap_below_three": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_DUPLICATE_CHILD_EXACT_COUNTEREXAMPLE_2026_08_21.json"
        ),
    )
    args = parser.parse_args()
    record = exact_record()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "value": record["value"], "gap": record["gap_to_three"]}))


if __name__ == "__main__":
    main()
