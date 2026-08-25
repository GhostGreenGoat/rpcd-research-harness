"""Exact rank-one-cone search for a two-facet tail-SDP dual witness.

This is a decisive checker only when it returns a positive rational dual gap.
The finite integer-ray restriction is not exhaustive, so a null result is not
an SDP feasibility proof.  All arithmetic and simplex pivots are exact SymPy
rationals; there is no numerical tolerance.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import sympy as sp
from sympy.solvers.simplex import linprog


def coordinate_updates(matrix: sp.Matrix) -> list[sp.Matrix]:
    identity = sp.eye(matrix.rows)
    updates: list[sp.Matrix] = []
    for index in range(matrix.rows):
        coordinate = sp.zeros(matrix.rows, 1)
        coordinate[index] = 1
        updates.append(identity - coordinate * (coordinate.T * matrix))
    return updates


def epoch_maps(matrix: sp.Matrix) -> list[sp.Matrix]:
    updates = coordinate_updates(matrix)
    result: list[sp.Matrix] = []
    for permutation in itertools.permutations(range(matrix.rows)):
        epoch = sp.eye(matrix.rows)
        for index in permutation:
            epoch = updates[index] * epoch
        result.append(sp.simplify(epoch))
    return result


def adjoint_map(weight: sp.Matrix, maps: list[sp.Matrix]) -> sp.Matrix:
    return sp.simplify(sum((epoch.T * weight * epoch for epoch in maps), sp.zeros(3)) / len(maps))


def forward_map(weight: sp.Matrix, maps: list[sp.Matrix]) -> sp.Matrix:
    return sp.simplify(sum((epoch * weight * epoch.T for epoch in maps), sp.zeros(3)) / len(maps))


def matrix_coordinates(matrix: sp.Matrix) -> list[sp.Expr]:
    return [matrix[0, 0], matrix[1, 1], matrix[2, 2], matrix[0, 1], matrix[0, 2], matrix[1, 2]]


def primitive_integer_rays(radius: int) -> list[sp.Matrix]:
    rays: set[tuple[int, int, int]] = set()
    for raw in itertools.product(range(-radius, radius + 1), repeat=3):
        if raw == (0, 0, 0):
            continue
        gcd = math.gcd(math.gcd(abs(raw[0]), abs(raw[1])), abs(raw[2]))
        primitive = tuple(value // gcd for value in raw)
        first = next(value for value in primitive if value != 0)
        if first < 0:
            primitive = tuple(-value for value in primitive)
        rays.add(primitive)
    return [sp.Matrix(ray) for ray in sorted(rays)]


def inner(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.trace(left.T * right)


def search(radius: int) -> dict[str, object]:
    matrix = sp.Matrix(
        [
            [1, sp.Rational(3, 10), 0],
            [sp.Rational(3, 10), 1, sp.Rational(2, 5)],
            [0, sp.Rational(2, 5), 1],
        ]
    )
    rate = sp.Rational(3, 20)
    kappa = sp.Rational(6, 5)
    maps = epoch_maps(matrix)
    first = adjoint_map(matrix, maps)
    rays = primitive_integer_rays(radius)
    dyads = [ray * ray.T for ray in rays]
    count = len(rays)

    # Variable blocks are nonnegative coefficients of L,U,X,Y, respectively.
    columns: list[list[sp.Expr]] = []
    objective: list[sp.Expr] = []
    normalization: list[sp.Expr] = []
    for block in ("L", "U", "X", "Y"):
        for dyad in dyads:
            if block == "L":
                stationarity = dyad
                objective_value = sp.Integer(0)
                normalization_value = sp.Integer(0)
            elif block == "U":
                stationarity = -dyad
                objective_value = kappa * inner(dyad, matrix)
                normalization_value = inner(dyad, matrix)
            elif block == "X":
                stationarity = rate * dyad
                objective_value = -inner(dyad, first)
                normalization_value = sp.Integer(0)
            else:
                stationarity = rate * dyad - forward_map(dyad, maps)
                objective_value = sp.Integer(0)
                normalization_value = sp.Integer(0)
            columns.append(matrix_coordinates(stationarity))
            objective.append(objective_value)
            normalization.append(normalization_value)

    equality = sp.Matrix.hstack(*(sp.Matrix(column) for column in columns))
    equality = equality.col_join(sp.Matrix([normalization]).reshape(1, 4 * count))
    right_hand_side = sp.Matrix([0, 0, 0, 0, 0, 0, 1])
    # SymPy 1.14 constructs an incorrectly sized empty inequality RHS when
    # A is omitted.  Supply the redundant nonnegativity consequence
    # -<U,A> <= 0 to keep the exact LP dimensions well-defined.
    redundant_inequality = -sp.Matrix([normalization]).reshape(1, 4 * count)
    optimum, coefficients = linprog(
        sp.Matrix(objective),
        A=redundant_inequality,
        b=sp.Matrix([0]),
        A_eq=equality,
        b_eq=right_hand_side,
    )

    variables: dict[str, sp.Matrix] = {}
    active: dict[str, list[dict[str, str | list[int]]]] = {}
    for block_index, block in enumerate(("L", "U", "X", "Y")):
        variable = sp.zeros(3)
        records: list[dict[str, str | list[int]]] = []
        for index, (ray, dyad) in enumerate(zip(rays, dyads, strict=True)):
            coefficient = coefficients[block_index * count + index]
            if coefficient:
                variable += coefficient * dyad
                records.append(
                    {
                        "ray": [int(value) for value in ray],
                        "coefficient": str(sp.factor(coefficient)),
                    }
                )
        variables[block] = sp.simplify(variable)
        active[block] = records

    stationarity = sp.simplify(
        variables["L"]
        - variables["U"]
        + rate * variables["X"]
        + rate * variables["Y"]
        - forward_map(variables["Y"], maps)
    )
    normalized_u = sp.factor(inner(variables["U"], matrix))
    dual_gap = sp.factor(inner(variables["X"], first) - kappa * normalized_u)
    assert stationarity == sp.zeros(3)
    assert normalized_u == 1
    assert dual_gap == -optimum
    assert all(coefficient >= 0 for coefficient in coefficients)

    return {
        "status": "exact_dual_witness" if dual_gap > 0 else "restricted_search_no_witness",
        "ray_radius": radius,
        "primitive_ray_count": count,
        "dual_variable_count": 4 * count,
        "rate": str(rate),
        "kappa": str(kappa),
        "objective_minimum_kappa_UA_minus_XB": str(sp.factor(optimum)),
        "certified_dual_gap_XB_minus_kappa_UA": str(dual_gap),
        "normalization_inner_U_A": str(normalized_u),
        "stationarity_exactly_zero": True,
        "psd_basis": "Each L,U,X,Y is an explicitly nonnegative rational sum of vv^T.",
        "active_rank_one_terms": active,
        "variables": {
            block: [[str(sp.factor(variable[i, j])) for j in range(3)] for i in range(3)]
            for block, variable in variables.items()
        },
        "scope": (
            "A positive gap is an exact tail-SDP infeasibility certificate. "
            "A nonpositive gap only reports a null search inside the finite integer-ray subcone."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radius", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    record = search(arguments.radius)
    encoded = json.dumps(record, indent=2, sort_keys=True) + "\n"
    arguments.output.write_bytes(encoded.encode("utf-8"))
    print(json.dumps({"sha256": hashlib.sha256(encoded.encode()).hexdigest(), **record}, indent=2))


if __name__ == "__main__":
    main()
