"""Exact barriers to two tempting strengthenings around the L3 proof.

Neither barrier refutes L3.  They delimit the matrix multipliers that a valid
proof may use.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def p_child(matrix: sp.Matrix) -> sp.Matrix:
    d = matrix.rows
    identity = sp.eye(d)
    return sp.simplify(
        ((3 * d + 1) * identity - 4 * matrix + 2 * (matrix - identity) ** 2 / (d - 1))
        / (2 * d * (d - 1))
    )


def full_d2_compensation_barrier() -> dict[str, object]:
    """Full beta Schur compensation fails in child dimension two."""
    mu = Q(1, 4)
    parent = sp.Matrix(
        [
            [1, Q(3, 4), Q(3, 4)],
            [Q(3, 4), 1, Q(3, 4)],
            [Q(3, 4), Q(3, 4), 1],
        ]
    )
    child = parent[1:, 1:]
    b = parent[1:, 0]
    c = child.inv() * b
    schur = sp.factor(1 - (b.T * c)[0])
    beta = 3 * mu / 4
    failed_gap = sp.simplify(
        p_child(child) - beta * child.inv() - beta * c * c.T / schur
    )
    witness = sp.Matrix([1, 1])
    quadratic = sp.factor((witness.T * failed_gap * witness)[0])
    determinant = sp.factor(failed_gap.det())
    scalar_lambda = Q(7, 4)
    scalar_g = sp.factor(
        (
            7
            - 4 * scalar_lambda
            + 2 * (scalar_lambda - 1) ** 2
        )
        / 4
        - 3 * mu / (4 * scalar_lambda)
    )
    scalar_required = sp.factor(
        Q(3, 4)
        * (scalar_lambda - mu)
        * (1 - mu)
        / (scalar_lambda * (scalar_lambda + 1 - mu))
    )
    assert sp.factor(parent.charpoly().as_expr()) == (
        (2 * sp.Symbol("lambda") - 5)
        * (4 * sp.Symbol("lambda") - 1) ** 2
        / 32
    )
    assert schur == Q(5, 14)
    assert scalar_g == Q(39, 224)
    assert scalar_required == Q(27, 140)
    assert sp.factor(scalar_g - scalar_required) == -Q(3, 160)
    assert quadratic == -Q(3, 80)
    assert determinant == -Q(99, 5120)
    return {
        "parent": [[str(x) for x in row] for row in parent.tolist()],
        "mu": str(mu),
        "parent_characteristic_polynomial": str(sp.factor(parent.charpoly().as_expr())),
        "child_high_eigenvalue": str(scalar_lambda),
        "schur_s": str(schur),
        "failed_claim": "P_2(C)-beta C^-1 >= (beta/s)cc^T with beta=3mu/4",
        "scalar_gap": str(sp.factor(scalar_g - scalar_required)),
        "matrix_witness": [str(x) for x in witness],
        "matrix_witness_quadratic": str(quadratic),
        "matrix_gap_determinant": str(determinant),
        "scope": "The piecewise smaller kappa used in the proof survives; the L3 target itself is not refuted.",
    }


def no_scalar_zf_dominates_f2() -> dict[str, object]:
    """The exact anisotropic residual cannot dominate F^2 by any c>0."""
    size = 4
    f = sp.ones(size) - sp.eye(size)
    z_f = sp.diag(*[(f**2)[i, i] for i in range(size)]) - f**2 / (size - 1)
    witness = sp.ones(size, 1)
    z_quadratic = sp.factor((witness.T * z_f * witness)[0])
    f2_quadratic = sp.factor((witness.T * f**2 * witness)[0])
    assert z_quadratic == 0
    assert f2_quadratic == 36
    return {
        "matrix_F": [[str(x) for x in row] for row in f.tolist()],
        "size": size,
        "witness": [str(x) for x in witness],
        "Z_F_witness_quadratic": str(z_quadratic),
        "F_squared_witness_quadratic": str(f2_quadratic),
        "failed_claim": "Z_F=Diag(diag F^2)-F^2/(m-1) >= c F^2 for some universal c>0",
        "exact_conclusion": "On this witness the gap Z_F-cF^2 equals -36c for every c>0.",
        "scope": "Z_F is still PSD and essential in transverse directions; only a scalar domination by F^2 is refuted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/iteration6/route_l3/evidence/EXACT_ROUTE_BARRIERS.json"),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact route counterexamples",
        "scope_warning": "Neither item is a counterexample to L3 or to RPCD.",
        "full_d2_compensation_barrier": full_d2_compensation_barrier(),
        "no_scalar_zf_dominates_f2": no_scalar_zf_dominates_f2(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "PASS"}))


if __name__ == "__main__":
    main()
