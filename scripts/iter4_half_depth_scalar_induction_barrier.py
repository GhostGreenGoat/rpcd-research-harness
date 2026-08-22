"""Exact barrier to the scalar-floor induction for prefix certificates.

This does not refute the prefix conjecture ``J_t >= (t*mu/m) B^-1``.
It refutes the natural proof that substitutes only that scalar child bound in
the Bellman recursion and then tries to close with ``B^-1`` and the first
Schur-loss matrix.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp


def exact_record() -> dict[str, object]:
    m = 3
    mu = sp.Rational(1, 5)
    matrix = mu * sp.eye(m) + (1 - mu) * sp.ones(m)
    inverse = matrix.inv()
    leverage = sp.diag(*[1 / inverse[index, index] for index in range(m)])
    first_loss = (inverse - sp.eye(m)) * leverage * (inverse - sp.eye(m)) / m

    # For the induction J_{t+1}, t=1, this is the residual obtained after
    # inserting the child's scalar floor and clearing m(m-1).
    t = 1
    induction_residual = (
        (m - 1 - t * mu) * sp.eye(m)
        - m * t * mu * first_loss
        - mu * (m - t - 1) * inverse
    )
    transverse = sp.Matrix([1, -1, 0])
    induction_eigenvalue = sp.factor(
        (transverse.T * induction_residual * transverse)[0]
        / (transverse.T * transverse)[0]
    )
    assert induction_eigenvalue == -sp.Rational(28, 225)

    diagonal_square = sp.diag(*[(matrix * matrix)[i, i] for i in range(m)])
    prefix_two = (
        (2 * m - 1) * sp.eye(m) - 2 * matrix + diagonal_square
    ) / (m * (m - 1))
    actual_residual = prefix_two - 2 * mu * inverse / m
    actual_eigenvalue = sp.factor(
        (transverse.T * actual_residual * transverse)[0]
        / (transverse.T * transverse)[0]
    )
    assert actual_eigenvalue == sp.Rational(12, 25)
    assert induction_eigenvalue < 0 < actual_eigenvalue
    return {
        "schema_version": "1.0",
        "evidence_level": "E2",
        "status": "exact finite counterexample to a scalar-floor induction step",
        "scope_warning": "The prefix bound itself remains true in this example and is not refuted.",
        "matrix": [[str(entry) for entry in row] for row in matrix.tolist()],
        "mu": str(mu),
        "child_depth_t": t,
        "cleared_induction_residual_transverse_eigenvalue": str(induction_eigenvalue),
        "actual_J2_minus_2mu_over_m_Binverse_transverse_eigenvalue": str(actual_eigenvalue),
        "checks": {
            "induction_closure_is_strictly_negative": True,
            "actual_prefix_target_has_positive_margin": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_HALF_DEPTH_SCALAR_INDUCTION_BARRIER_2026_08_21.json"
        ),
    )
    args = parser.parse_args()
    record = exact_record()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "record": record}))


if __name__ == "__main__":
    main()
