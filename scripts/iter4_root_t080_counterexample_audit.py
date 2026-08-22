"""Independent exact subset-DP audit of the n=8 T080 counterexample.

The discovery script reduces the permutation average to 56 pole-position
classes.  This audit deliberately uses a different computation: it constructs
the full rational matrix and evaluates the complete K_0 matrix through the
2^n remaining-set Bellman recursion.  It also gives a finite positive-definite
``mu=1/100`` violation of the stronger one-epoch A-energy target.

Neither statement refutes the original covariance spectral-rate conjecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sympy as sp

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.iter4_duplicate_child_counterexample import exact_remaining_set_k


def boundary_matrix() -> sp.Matrix:
    q = sp.Rational
    n = 8
    matrix = sp.ones(n) * q(71, 125)
    for index in range(n):
        matrix[index, index] = 1
    for first in range(2):
        for second in range(2):
            matrix[first, second] = 1
        for ring in range(2, n):
            matrix[first, ring] = matrix[ring, first] = q(4, 5)
    return matrix


def rayleigh(matrix: sp.Matrix, vector: sp.Matrix) -> sp.Expr:
    return sp.factor((vector.T * matrix * vector)[0] / (vector.T * vector)[0])


def exact_record() -> dict[str, object]:
    n = 8
    correlation = boundary_matrix()
    vector = sp.Matrix([1, -1, 0, 0, 0, 0, 0, 0])
    expected_characteristic = (
        sp.Symbol("lambda") ** 2
        * (sp.Symbol("lambda") - sp.Rational(54, 125)) ** 5
        * (sp.Symbol("lambda") - sp.Rational(146, 25))
    )
    characteristic = sp.factor(correlation.charpoly().as_expr())
    assert sp.expand(characteristic - expected_characteristic) == 0
    assert correlation * vector == sp.zeros(n, 1)

    boundary_k = exact_remaining_set_k(correlation)
    boundary_coefficient = rayleigh(boundary_k, vector)
    claimed_boundary_coefficient = sp.Rational(
        2296209806050635263939777,
        1164153218269348144531250,
    )
    assert boundary_coefficient == claimed_boundary_coefficient
    assert boundary_k * vector == boundary_coefficient * vector
    boundary_gap = sp.factor(boundary_coefficient - 2)
    assert boundary_gap < 0

    mu = sp.Rational(1, 100)
    positive_matrix = mu * sp.eye(n) + (1 - mu) * correlation
    positive_k = exact_remaining_set_k(positive_matrix)
    positive_kappa = rayleigh(positive_k, vector)
    assert positive_k * vector == positive_kappa * vector

    # A_mu u=mu u.  The one-epoch energy identity
    # A-E[T^TAT]=A K_0(A) A therefore makes the exact final-energy ratio
    # along u equal to 1-mu*positive_kappa.
    energy_rate = sp.factor(1 - mu * positive_kappa)
    covariance_target = (1 - mu / n) ** (2 * n)
    fixed_target = sp.Rational(n - 1, n) ** n
    assert covariance_target > fixed_target
    rate_gap = sp.factor(energy_rate - covariance_target)
    claimed_rate_gap = sp.Rational(
        139407497673157900331734058355416764719752656401774517490321089151,
        655360000000000000000000000000000000000000000000000000000000000000000,
    )
    assert rate_gap == claimed_rate_gap
    assert rate_gap > 0
    return {
        "schema_version": "1.0",
        "evidence_level": "E4",
        "status": "independent exact reconstruction of a T080 refutation",
        "scope_warning": (
            "The strong one-epoch A-energy certificate is refuted; the original "
            "RPCD covariance spectral-rate conjecture is not."
        ),
        "method": "full 2^8 rational remaining-set Bellman recursion",
        "boundary": {
            "characteristic_polynomial": str(characteristic),
            "kernel_vector": [int(value) for value in vector],
            "K0_eigenvalue_on_kernel_vector": str(boundary_coefficient),
            "gap_to_two": str(boundary_gap),
        },
        "finite_positive_definite_ray": {
            "mu": str(mu),
            "K0_eigenvalue_on_pole_difference": str(positive_kappa),
            "one_epoch_energy_rate": str(energy_rate),
            "target_q": str(covariance_target),
            "rate_minus_q": str(rate_gap),
            "rate_minus_q_decimal": str(sp.N(rate_gap, 18)),
        },
        "checks": {
            "unit_diagonal_psd_boundary_from_exact_spectrum": True,
            "full_K0_subset_recursion_exact": True,
            "pole_difference_is_common_eigenvector": True,
            "boundary_T080_gap_strictly_negative": True,
            "finite_mu_strong_energy_gap_strictly_positive": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_ROOT_T080_COUNTEREXAMPLE_AUDIT_2026_08_21.json"
        ),
    )
    args = parser.parse_args()
    record = exact_record()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "boundary_gap": record["boundary"]["gap_to_two"],
                "finite_mu_rate_gap": record["finite_positive_definite_ray"]["rate_minus_q"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
