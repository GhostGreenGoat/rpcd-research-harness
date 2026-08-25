"""Exact checks for the bounded-horizon phase-reset repair.

The general phase-reset equivalence is proved in phase_reset_equivalence.md.
This script supplies zero-tolerance rational/symbolic checks on two hostile
families:

1. the noncommuting rational n=3 chain, where q=3/20 has no reset at
   horizons 1,...,8 but has a strict reset at horizon 9; and
2. the near-singular unit-diagonal n=2 line, where a two-epoch reset works
   uniformly for 99/100 <= rho < 1 although the one-epoch A-metric fails.

The output is finite verification or a symbolic proof-draft aid.  It does not
prove the unrestricted C050 claim.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp


def factor_string(value: sp.Expr) -> str:
    return str(sp.factor(sp.cancel(value)))


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
    maps: list[sp.Matrix] = []
    for permutation in itertools.permutations(range(matrix.rows)):
        epoch = sp.eye(matrix.rows)
        for index in permutation:
            epoch = updates[index] * epoch
        maps.append(sp.simplify(epoch))
    return maps


def covariance_adjoint(weight: sp.Matrix, maps: list[sp.Matrix]) -> sp.Matrix:
    return sp.simplify(
        sum((epoch.T * weight * epoch for epoch in maps), sp.zeros(weight.rows))
        / len(maps)
    )


def principal_minors(matrix: sp.Matrix) -> dict[str, sp.Expr]:
    result: dict[str, sp.Expr] = {}
    for size in range(1, matrix.rows + 1):
        for subset in itertools.combinations(range(matrix.rows), size):
            key = ",".join(str(index) for index in subset)
            result[key] = sp.factor(matrix.extract(subset, subset).det())
    return result


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
    expanded = sp.Poly(sp.expand(polynomial), variable)
    degree = expanded.degree()
    powers = [expanded.nth(index) for index in range(degree + 1)]
    return [
        sp.factor(
            sum(
                powers[index]
                * sp.binomial(level, index)
                / sp.binomial(degree, index)
                for index in range(level + 1)
            )
        )
        for level in range(degree + 1)
    ]


def noncommuting_reset() -> dict[str, object]:
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
    updates = coordinate_updates(matrix)
    commutators = [
        sp.factor(sp.trace((updates[0] * updates[1] - updates[1] * updates[0]).T * (updates[0] * updates[1] - updates[1] * updates[0]))),
        sp.factor(sp.trace((updates[1] * updates[2] - updates[2] * updates[1]).T * (updates[1] * updates[2] - updates[2] * updates[1]))),
    ]
    assert all(value > 0 for value in commutators)

    powers = [matrix]
    for _ in range(9):
        powers.append(covariance_adjoint(powers[-1], maps))

    failed_horizons: list[dict[str, object]] = []
    for horizon in range(1, 9):
        gap = sp.simplify(rate**horizon * matrix - powers[horizon])
        determinant = sp.factor(gap.det())
        assert determinant < 0
        failed_horizons.append(
            {
                "horizon": horizon,
                "determinant_of_q_power_A_minus_Mstar_power_A": factor_string(determinant),
                "dual_interpretation": "The negative determinant proves the reset gap is indefinite; an exact negative eigen-direction exists. This rejects only this prescribed horizon.",
            }
        )

    reset_gap = sp.simplify(rate**9 * matrix - powers[9])
    reset_minors = principal_minors(reset_gap)
    assert all(value > 0 for value in reset_minors.values())

    comparison_records: list[dict[str, object]] = []
    for phase in range(9):
        facet = sp.simplify(rate ** (-phase) * powers[phase])
        upper_gap = sp.simplify(kappa * matrix - facet)
        upper_minors = principal_minors(upper_gap)
        assert all(value > 0 for value in upper_minors.values())
        if phase < 8:
            next_facet = sp.simplify(rate ** (-(phase + 1)) * powers[phase + 1])
            assert covariance_adjoint(facet, maps) == rate * next_facet
        comparison_records.append(
            {
                "phase": phase,
                "determinant_of_kappa_A_minus_P_phase": factor_string(upper_gap.det()),
            }
        )

    last_facet = sp.simplify(rate ** (-8) * powers[8])
    terminal_gap = sp.simplify(rate * matrix - covariance_adjoint(last_facet, maps))
    assert terminal_gap == sp.simplify(rate ** (-8) * reset_gap)
    assert all(value > 0 for value in principal_minors(terminal_gap).values())

    return {
        "family": "rational noncommuting n=3 chain",
        "A": [[factor_string(matrix[i, j]) for j in range(3)] for i in range(3)],
        "unit_diagonal": True,
        "eigenvalues": ["1/2", "1", "3/2"],
        "mu": "1/2",
        "coordinate_update_commutator_norm_squares": [factor_string(value) for value in commutators],
        "q": factor_string(rate),
        "kappa": factor_string(kappa),
        "failed_reset_horizons": failed_horizons,
        "first_strict_reset_horizon": 9,
        "reset_gap_all_principal_minors": {
            key: factor_string(value) for key, value in reset_minors.items()
        },
        "phase_metric_comparisons": comparison_records,
        "routing": "0->1->...->8->0",
        "outcome": "Nine exact canonical facets form a deterministic reset cycle. Horizons 1 through 8 fail this reset architecture by exact negative determinants.",
        "scope": "Finite n=3 phase-reset certificate and minimality only within the prescribed canonical reset family; not a lower bound for arbitrary facets and not C050.",
    }


def near_singular_two_epoch_reset() -> dict[str, object]:
    rho = sp.symbols("rho", real=True)
    scaled_mu = sp.symbols("t", real=True)
    matrix = sp.Matrix([[1, rho], [rho, 1]])
    maps = epoch_maps(matrix)
    first = covariance_adjoint(matrix, maps)
    second = covariance_adjoint(first, maps)
    rate = sp.Rational(21, 8) * rho - sp.Rational(13, 8)
    expected_first = rho**2 * (1 - rho**2) * sp.eye(2) / 2
    expected_second = rho**4 * (1 - rho**4) * sp.eye(2) / 4
    assert sp.simplify(first - expected_first) == sp.zeros(2)
    assert sp.simplify(second - expected_second) == sp.zeros(2)

    one_epoch_bad_eigenvalue = sp.factor(
        rate * (1 - rho) - rho**2 * (1 - rho**2) / 2
    )
    expected_bad_factor = (rho - 1) ** 2 * (4 * rho**2 + 8 * rho - 13) / 8
    assert sp.simplify(one_epoch_bad_eigenvalue - expected_bad_factor) == 0

    two_epoch_small_eigenvalue = sp.factor(
        rate**2 * (1 - rho) - rho**4 * (1 - rho**4) / 4
    )
    positivity_polynomial = (
        16 * rho**6
        + 32 * rho**5
        + 48 * rho**4
        + 64 * rho**3
        + 64 * rho**2
        - 377 * rho
        + 169
    )
    expected_two_epoch_factor = (rho - 1) ** 2 * positivity_polynomial / 64
    assert sp.simplify(two_epoch_small_eigenvalue - expected_two_epoch_factor) == 0

    # Put t=100(1-rho), so rho in [99/100,1] corresponds exactly to t in [0,1].
    polynomial_on_unit_interval = sp.factor(
        positivity_polynomial.subs(rho, 1 - scaled_mu / 100)
    )
    coefficients = bernstein_coefficients(polynomial_on_unit_interval, scaled_mu)
    assert all(coefficient > 0 for coefficient in coefficients)

    # The one-epoch bad factor is strictly negative on the same interval:
    # 4 rho^2+8 rho-13 is increasing and is already negative at rho=1.
    assert sp.factor((4 * rho**2 + 8 * rho - 13).subs(rho, sp.Rational(99, 100))) < 0
    assert sp.factor((4 * rho**2 + 8 * rho - 13).subs(rho, 1)) < 0
    lower_rate = sp.factor(rate.subs(rho, sp.Rational(99, 100)))
    assert lower_rate == sp.Rational(779, 800)

    return {
        "family": "near-singular unit-diagonal A_rho=[[1,rho],[rho,1]]",
        "domain": "99/100 <= rho < 1",
        "mu": "1-rho in (0,1/100]",
        "q": "1-(21/8)mu=(21rho-13)/8",
        "q_lower_bound": factor_string(lower_rate),
        "Mstar_A": "rho^2(1-rho^2) I/2",
        "Mstar_squared_A": "rho^4(1-rho^4) I/4",
        "one_epoch_A_metric_bad_eigenvalue": factor_string(one_epoch_bad_eigenvalue),
        "one_epoch_failure_ray": [1, -1],
        "one_epoch_failure_reason": "4rho^2+8rho-13<0 throughout the stated interval",
        "two_epoch_reset_small_eigenvalue": factor_string(two_epoch_small_eigenvalue),
        "two_epoch_positivity_polynomial": factor_string(positivity_polynomial),
        "positivity_polynomial_after_t_equals_100mu": factor_string(polynomial_on_unit_interval),
        "bernstein_coefficients_on_t_in_0_1": [factor_string(value) for value in coefficients],
        "all_bernstein_coefficients_strictly_positive": True,
        "phase_facets": ["P0=A", "P1=q^{-1}Mstar(A)"],
        "routing": "0->1->0",
        "metric_comparison": "Pj<=q^{-1}A<=(800/779)A by pathwise A-energy monotonicity",
        "expected_distance_bound": "E||x_k||_A <= sqrt(800/779) exp(-(21/16)mu k)||x_0||_A on the stated family",
        "outcome": "A symbolic two-epoch phase reset succeeds uniformly in the near-singular interval while the one-epoch fixed-A LMI fails exactly.",
        "scope": "All-parameter n=2 proof draft on rho in [99/100,1); no extension to arbitrary SPD matrices.",
    }


def state_growth_stress() -> dict[str, object]:
    records: list[dict[str, int | str]] = []
    for dimension, inverse_mu in ((10, 10), (100, 100), (1000, 1000)):
        facets = inverse_mu
        symmetric_entries = dimension * (dimension + 1) // 2
        records.append(
            {
                "n": dimension,
                "illustrative_mu": f"1/{inverse_mu}",
                "illustrative_facets_for_B_equals_1": facets,
                "stored_symmetric_scalars": facets * symmetric_entries,
            }
        )
    return {
        "general_count": "At horizon m the literal canonical phase list stores m*n(n+1)/2 scalars; under m<=B/mu this is O(B*n^2/mu).",
        "examples": records,
        "interpretation": "The reset state is linear in 1/mu and quadratic in n, rather than factorial in n. This is representation cost, not a lower bound and not part of the RPCD update complexity.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "arithmetic": "exact SymPy Rational and symbolic factorization",
        "tolerance": 0,
        "seed": None,
        "noncommuting_reset": noncommuting_reset(),
        "near_singular_two_epoch_reset": near_singular_two_epoch_reset(),
        "state_growth_stress": state_growth_stress(),
        "dual_obstruction": {
            "fixed_horizon": "G_m=theta A-(Mstar)^m(A) must be PSD",
            "exact_separator": "If G_m is not PSD, self-duality of the PSD cone gives X>=0 with <X,G_m><0; a rank-one X=zz^T may be chosen.",
            "bounded_horizon_attack": "To refute a proposed bound m<=M, provide one exact separator X_m for every m=1,...,M. A universal refutation still requires a quantified family for arbitrarily large proposed B.",
        },
        "scope": "Exact finite/symbolic route checks only; the unrestricted bounded-horizon lemma and C050 remain open.",
    }
    encoded = json.dumps(record, indent=2, sort_keys=True) + "\n"
    arguments.output.write_bytes(encoded.encode("utf-8"))
    print(
        json.dumps(
            {
                "status": "PASS",
                "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                "noncommuting_first_reset_horizon": record["noncommuting_reset"]["first_strict_reset_horizon"],
                "near_singular_interval": record["near_singular_two_epoch_reset"]["domain"],
                "tolerance": 0,
                "seed": None,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
