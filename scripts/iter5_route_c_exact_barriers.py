"""Exact finite barriers and subset identities for Iteration-5 Route C.

These computations attack proof *routes*.  None of the negative certificates
below is a counterexample to the half-depth matrix conjecture itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def deletion_data(matrix: sp.Matrix, index: int) -> tuple[sp.Matrix, sp.Matrix]:
    size = matrix.rows
    keep = [j for j in range(size) if j != index]
    child = matrix.extract(keep, keep)
    lift = sp.zeros(size - 1, size)
    for local, original in enumerate(keep):
        lift[local, original] = 1
        lift[local, index] = -matrix[original, index]
    return child, lift


def j2(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    diagonal_square = sp.diag(*[(matrix * matrix)[i, i] for i in range(size)])
    return ((2 * size - 1) * sp.eye(size) - 2 * matrix + diagonal_square) / (
        size * (size - 1)
    )


def prefix_j(matrix: sp.Matrix, depth: int) -> sp.Matrix:
    """Exact Bellman prefix matrix, used only in tiny rational barriers."""
    size = matrix.rows
    if depth == 0:
        return sp.zeros(size)
    answer = sp.eye(size) / size
    if depth == 1:
        return answer
    for index in range(size):
        child, lift = deletion_data(matrix, index)
        answer += lift.T * prefix_j(child, depth - 1) * lift / size
    return sp.simplify(answer)


def incremental_gain_barrier() -> dict[str, object]:
    """Refute the tempting per-stage gain Delta_2 >= (mu/3) A^-1."""
    matrix = sp.Matrix(
        [
            [1, Q(2, 3), Q(2, 3)],
            [Q(2, 3), 1, Q(3, 4)],
            [Q(2, 3), Q(3, 4), 1],
        ]
    )
    mu = Q(1, 4)
    characteristic = sp.factor(matrix.charpoly().as_expr())
    expected = (4 * sp.Symbol("lambda") - 1) * (
        36 * sp.Symbol("lambda") ** 2 - 99 * sp.Symbol("lambda") + 31
    ) / 144
    assert sp.expand(characteristic - expected) == 0

    delta_two = j2(matrix) - sp.eye(3) / 3
    gap = sp.simplify(delta_two - mu * matrix.inv() / 3)
    leading_one = sp.factor(gap[0, 0])
    leading_two = sp.factor(gap[:2, :2].det())
    determinant = sp.factor(gap.det())
    assert leading_one == Q(1045, 3348)
    assert leading_two == Q(186373, 2892672)
    assert determinant == -Q(1624139, 2499268608)
    return {
        "matrix": [[str(x) for x in row] for row in matrix.tolist()],
        "mu": str(mu),
        "characteristic_polynomial": str(characteristic),
        "gap_leading_principal_minors": [
            str(leading_one),
            str(leading_two),
            str(determinant),
        ],
        "conclusion": (
            "The first two leading minors are positive and the determinant is "
            "negative, so Delta_2-(mu/3)A^-1 has exactly one negative eigenvalue."
        ),
    }


def scalar_child_half_barrier() -> dict[str, object]:
    """Refute a parent lift that keeps only each child's scalar half bound."""
    mu = Q(1, 100)
    rank_one_two = sp.Matrix([[1, 1 - mu], [1 - mu, 1]])
    simplex_off = -(1 - mu) / 2
    simplex_three = sp.Matrix(
        3, 3, lambda i, j: 1 if i == j else simplex_off
    )
    matrix = sp.diag(rank_one_two, simplex_three)
    size = matrix.rows
    certificate = sp.eye(size) / size
    for index in range(size):
        child, lift = deletion_data(matrix, index)
        # Every child still has spectral floor mu.  Insert only the already
        # proved dimension-four scalar certificate (mu/2) C_i^{-1}.
        certificate += lift.T * (mu * child.inv() / 2) * lift / size

    gap = sp.simplify(certificate - mu * matrix.inv() / 2)
    witness = sp.Matrix([0, 0, 1, 1, 1])
    quadratic = sp.factor((witness.T * gap * witness)[0])
    normalized = sp.factor(
        (witness.T * matrix * certificate * matrix * witness)[0]
        / ((witness.T * matrix * witness)[0] * mu)
    )
    assert quadratic == -Q(2761797, 10100000)
    assert normalized == Q(4129401, 10100000) < Q(1, 2)
    return {
        "matrix": [[str(x) for x in row] for row in matrix.tolist()],
        "geometry": "direct sum of a signed-rank-one 2-block and a simplex 3-block",
        "mu": str(mu),
        "witness": [str(x) for x in witness],
        "gap_quadratic_form": str(quadratic),
        "certificate_generalized_ratio_over_mu": str(normalized),
        "scope": (
            "This refutes scalarizing the dimension-four child certificates; "
            "the exact lifted J2 child matrices have large positive surplus."
        ),
    }


def volume_only_barrier() -> dict[str, object]:
    """Refute sufficiency of the determinant/volume subset certificate."""
    size = 6
    depth = 3
    mu = Q(1, 10)
    parallel_eigenvalue = size - (size - 1) * mu
    # For A=mu I+(1-mu)11^T, the volume-adjugate prefix certificate has
    # parallel eigenvalue (t/m)*L*mu^(t-1).
    coefficient = Q(depth, size) * parallel_eigenvalue * mu ** (depth - 1)
    gap = sp.factor(coefficient - mu / 2)
    assert coefficient == Q(11, 400)
    assert gap == -Q(9, 400)
    return {
        "family": "A=mu I+(1-mu)11^T",
        "size": size,
        "subset_depth": depth,
        "mu": str(mu),
        "volume_certificate_parallel_coefficient": str(coefficient),
        "gap_to_mu_over_two": str(gap),
        "scope": (
            "The exact prefix can still satisfy the target; determinant-weighted "
            "subset projectors alone discard the essential order variance."
        ),
    }


def local_subset_polynomial_barrier() -> dict[str, object]:
    """Refute a tempting local 3-subset spectral proxy."""
    matrix = sp.Matrix(
        [
            [1, Q(1, 2), -Q(2, 3)],
            [Q(1, 2), 1, 0],
            [-Q(2, 3), 0, 1],
        ]
    )
    # Its eigenvalues are 1/6, 1, 11/6, so it is SPD.
    characteristic = sp.factor(matrix.charpoly().as_expr())
    weighted_full = prefix_j(matrix, 3) - prefix_j(matrix, 2) / 2
    spectral_proxy = (3 * sp.eye(3) - matrix) / 3
    gap = sp.simplify(weighted_full - spectral_proxy)
    witness = sp.Matrix([1, 0, -1])
    quadratic = sp.factor((witness.T * gap * witness)[0])
    assert characteristic == (
        (sp.Symbol("lambda") - 1)
        * (6 * sp.Symbol("lambda") - 11)
        * (6 * sp.Symbol("lambda") - 1)
        / 36
    )
    assert gap[0, 0] == Q(125, 432)
    assert sp.factor(gap[:2, :2].det()) == -Q(2917, 62208)
    assert quadratic == -Q(11, 48)
    return {
        "matrix": [[str(x) for x in row] for row in matrix.tolist()],
        "eigenvalue_factorization": str(characteristic),
        "failed_claim": "J3-(1/2)J2 >= (3I-A)/3 on every 3-subset",
        "witness": [str(x) for x in witness],
        "gap_quadratic_form": str(quadratic),
        "gap_first_entry": str(gap[0, 0]),
        "gap_leading_two_minor": str(sp.factor(gap[:2, :2].det())),
        "scope": (
            "This kills a local-subset shortcut whose average spectral proxy "
            "would imply W3.  It does not refute W3 itself; the proxy has "
            "additional trace-floor slack relative to the true target."
        ),
    }


def iterated_row_square_barrier() -> dict[str, object]:
    """Refute closure after applying the zero-diagonal row lemma twice."""
    size = 4
    mu = Q(1, 100)
    matrix = mu * sp.eye(size) + (1 - mu) * sp.ones(size)
    h = matrix - sp.eye(size)
    diagonal_h2 = sp.diag(*[(h**2)[i, i] for i in range(size)])
    diagonal_h3 = sp.diag(*[(h**3)[i, i] for i in range(size)])

    # Exact lifted square state:
    # S=sum_i L_i^T(C_i-I)^2L_i.  Its last zero-diagonal frame is compressed
    # once more as S >= R^2/(m-1).
    r = (size - 2) * h - h**2 + diagonal_h2
    compressed_s = r**2 / (size - 1)
    numerator = (
        4 * (size - 1) * (size - 2) * sp.eye(size)
        - 10 * (size - 2) * h
        + 8 * h**2
        + (3 * size - 14) * diagonal_h2
        - 4 * diagonal_h3
        + 2 * compressed_s / (size - 2)
    )
    compressed_c3 = sp.simplify(
        numerator / (2 * size * (size - 1) * (size - 2))
    )
    witness = sp.Matrix([1, -1, 0, 0])
    ordinary_transverse = sp.factor(
        (witness.T * compressed_c3 * witness)[0]
        / (witness.T * witness)[0]
    )
    target = Q(2, size)
    gap = sp.factor(ordinary_transverse - target)
    weak_gap = sp.factor(ordinary_transverse - Q(3, 2 * size))
    assert ordinary_transverse == Q(187276289, 400000000)
    assert gap == -Q(12723711, 400000000)
    assert weak_gap == Q(37276289, 400000000)
    symbolic_m = sp.symbols("m", integer=True, positive=True)
    boundary_ratio = (3 * symbolic_m - 1) / (
        2 * symbolic_m * (symbolic_m - 1)
    )
    boundary_gap = sp.factor(boundary_ratio - 2 / symbolic_m)
    boundary_scaled = sp.factor(symbolic_m * boundary_ratio)
    assert sp.simplify(
        boundary_gap
        + (symbolic_m - 3) / (2 * symbolic_m * (symbolic_m - 1))
    ) == 0
    assert sp.simplify(
        boundary_scaled - sp.Rational(3, 2) - 1 / (symbolic_m - 1)
    ) == 0
    return {
        "family": "A=mu I+(1-mu)11^T",
        "size": size,
        "mu": str(mu),
        "failed_claim": (
            "The twice row-square-compressed lower state already proves "
            "C3 >= (2mu/m)A^-1."
        ),
        "transverse_witness": [str(x) for x in witness],
        "compressed_generalized_ratio_over_mu": str(ordinary_transverse),
        "target_ratio": str(target),
        "gap": str(gap),
        "gap_to_weaker_3_over_2m_target": str(weak_gap),
        "all_dimension_mu_to_zero_transverse_ratio": str(boundary_ratio),
        "all_dimension_gap_to_2_over_m": str(boundary_gap),
        "m_times_boundary_ratio": str(boundary_scaled),
        "scope": (
            "The exact uncompressed lifted square has positive anisotropic "
            "surplus.  Reapplying the same row-Cauchy compression discards "
            "enough of it to miss W3 for every m>3 near the rank-one boundary. "
            "It clears the weaker 3/(2m) target by only 1/[m(m-1)] in the limit."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_c/evidence/EXACT_ROUTE_BARRIERS.json"
        ),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact finite route certificates",
        "scope_warning": (
            "These are counterexamples to auxiliary proof compressions, not to "
            "H_ceil(n/2)>=(mu/2)A^-1."
        ),
        "incremental_gain_barrier": incremental_gain_barrier(),
        "scalar_child_half_barrier": scalar_child_half_barrier(),
        "volume_only_barrier": volume_only_barrier(),
        "local_subset_polynomial_barrier": local_subset_polynomial_barrier(),
        "iterated_row_square_barrier": iterated_row_square_barrier(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "PASS"}))


if __name__ == "__main__":
    main()
