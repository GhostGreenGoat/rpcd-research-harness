"""Exact finite checks for the T143 adaptive-history Lyapunov route.

All decisive arithmetic in this file uses sympy Rational.  The script verifies:

1. the frozen residual Bellman capture equals the triangular inverse moment;
2. a genuinely history-dependent n=3 certificate with rational data;
3. failure of the fixed-A LMI at the same rational rate;
4. exact five- and nine-facet canonical phase closures and shorter failures;
5. the exact non-normal block-power necessities and one finite obstruction;
6. symbolic identities for near-singular 2-by-2 and noncommuting 3-by-3 families;
7. signed, connected-block, and inherited-barrier controls.

The finite checks are not a proof for arbitrary dimension.  The general
algebraic arguments are recorded in route_development.md.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import sympy as sp


def frac(value: sp.Expr) -> str:
    return str(sp.factor(sp.cancel(value)))


def matrix_strings(matrix: sp.Matrix) -> list[list[str]]:
    return [[frac(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def all_principal_minors(matrix: sp.Matrix) -> dict[str, str]:
    result: dict[str, str] = {}
    n = matrix.rows
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            submatrix = matrix.extract(subset, subset)
            key = ",".join(str(index) for index in subset)
            result[key] = frac(submatrix.det())
    return result


def principal_minor_values(matrix: sp.Matrix) -> list[sp.Expr]:
    values: list[sp.Expr] = []
    n = matrix.rows
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            values.append(sp.factor(matrix.extract(subset, subset).det()))
    return values


def bernstein_coefficients_on_unit_interval(polynomial: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
    expanded = sp.Poly(sp.expand(polynomial), variable)
    degree = expanded.degree()
    powers = [expanded.nth(index) for index in range(degree + 1)]
    return [
        sp.factor(
            sum(
                powers[index] * sp.binomial(level, index) / sp.binomial(degree, index)
                for index in range(level + 1)
            )
        )
        for level in range(degree + 1)
    ]


def polynomial_psd_record(matrix: sp.Matrix, variable: sp.Symbol) -> dict[str, object]:
    records: dict[str, object] = {}
    for size in range(1, matrix.rows + 1):
        for subset in itertools.combinations(range(matrix.rows), size):
            determinant = sp.factor(matrix.extract(subset, subset).det())
            numerator, denominator = sp.fraction(determinant)
            coefficients = bernstein_coefficients_on_unit_interval(numerator, variable)
            assert denominator > 0
            assert all(coefficient >= 0 for coefficient in coefficients)
            records[",".join(str(index) for index in subset)] = {
                "determinant": frac(determinant),
                "numerator_bernstein_coefficients_on_0_1": [frac(value) for value in coefficients],
                "all_coefficients_nonnegative": True,
            }
    return records


def leading_principal_minors(matrix: sp.Matrix) -> list[str]:
    return [frac(matrix[:size, :size].det()) for size in range(1, matrix.rows + 1)]


def coordinate_updates(matrix: sp.Matrix) -> list[sp.Matrix]:
    n = matrix.rows
    identity = sp.eye(n)
    updates: list[sp.Matrix] = []
    for index in range(n):
        coordinate = sp.zeros(n, 1)
        coordinate[index] = 1
        updates.append(identity - coordinate * (coordinate.T * matrix))
    return updates


def epoch_maps(matrix: sp.Matrix) -> list[tuple[tuple[int, ...], sp.Matrix]]:
    n = matrix.rows
    updates = coordinate_updates(matrix)
    result: list[tuple[tuple[int, ...], sp.Matrix]] = []
    for permutation in itertools.permutations(range(n)):
        epoch = sp.eye(n)
        for index in permutation:
            epoch = updates[index] * epoch
        result.append((permutation, sp.simplify(epoch)))
    return result


def covariance_adjoint(
    weight: sp.Matrix, maps: list[tuple[tuple[int, ...], sp.Matrix]]
) -> sp.Matrix:
    total = sp.zeros(weight.rows)
    for _, epoch in maps:
        total += epoch.T * weight * epoch
    return sp.simplify(total / len(maps))


def bellman_capture(matrix: sp.Matrix) -> sp.Matrix:
    """Average sum of selected squared residual rows by direct path expansion."""
    n = matrix.rows
    identity = sp.eye(n)
    total = sp.zeros(n)
    for permutation in itertools.permutations(range(n)):
        residual_map = identity
        path_capture = sp.zeros(n)
        for index in permutation:
            selected = residual_map[index, :]
            path_capture += selected.T * selected
            coordinate = sp.zeros(n, 1)
            coordinate[index] = 1
            residual_map = (identity - matrix * coordinate * coordinate.T) * residual_map
        total += path_capture
    return sp.simplify(total / sp.factorial(n))


def triangular_inverse_capture(matrix: sp.Matrix) -> sp.Matrix:
    """Average P^T L^{-T}L^{-1}P in chronological permutation coordinates."""
    n = matrix.rows
    total = sp.zeros(n)
    for permutation in itertools.permutations(range(n)):
        selector = sp.zeros(n)
        lower = sp.zeros(n)
        for row, original_row in enumerate(permutation):
            selector[row, original_row] = 1
            for column in range(row + 1):
                original_column = permutation[column]
                lower[row, column] = matrix[original_row, original_column]
        inverse = lower.inv()
        total += selector.T * inverse.T * inverse * selector
    return sp.simplify(total / sp.factorial(n))


def exact_three_dimensional_certificate() -> dict[str, object]:
    # Eigenvalues are 1/2, 1, 3/2, so mu=1/2 exactly.
    matrix = sp.Matrix(
        [
            [1, sp.Rational(3, 10), 0],
            [sp.Rational(3, 10), 1, sp.Rational(2, 5)],
            [0, sp.Rational(2, 5), 1],
        ]
    )
    mu = sp.Rational(1, 2)
    rate = sp.Rational(7, 40)
    history_kappa = sp.Integer(2)
    tail_kappa = sp.Rational(509, 500)
    maps = epoch_maps(matrix)
    fixed_output = covariance_adjoint(matrix, maps)
    bellman = bellman_capture(matrix)
    triangular = triangular_inverse_capture(matrix)
    assert bellman == triangular
    assert matrix - fixed_output == matrix * bellman * matrix

    path_records: list[dict[str, object]] = []
    for permutation, epoch in maps:
        left_kernel = epoch.T.nullspace()
        assert left_kernel
        witness = left_kernel[0]
        denominator = sp.cancel((witness.T * matrix.inv() * witness)[0])
        invisible = sp.simplify(witness * witness.T / denominator)
        metric = matrix + invisible
        dynamic_gap = sp.simplify(rate * metric - fixed_output)

        assert epoch.T * invisible * epoch == sp.zeros(3)
        assert all(value >= 0 for value in principal_minor_values(invisible))
        assert all(value >= 0 for value in principal_minor_values(matrix - invisible))
        assert all(value > 0 for value in [dynamic_gap[:k, :k].det() for k in range(1, 4)])

        path_records.append(
            {
                "permutation_zero_based": list(permutation),
                "epoch_rank": epoch.rank(),
                "left_kernel_witness": [frac(value) for value in witness],
                "normalizer_wT_Ainv_w": frac(denominator),
                "Q": matrix_strings(invisible),
                "P_equals_A_plus_Q": matrix_strings(metric),
                "T_transpose_Q_T_is_zero": True,
                "Q_psd_principal_minors": all_principal_minors(invisible),
                "A_minus_Q_psd_principal_minors": all_principal_minors(matrix - invisible),
                "dynamic_gap_leading_principal_minors": leading_principal_minors(dynamic_gap),
            }
        )

    fixed_gap = sp.simplify(rate * matrix - fixed_output)
    assert fixed_gap.det() < 0
    fixed_witness = sp.Matrix([-2, 4, -3])
    fixed_witness_value = sp.cancel((fixed_witness.T * fixed_gap * fixed_witness)[0])
    assert fixed_witness_value < 0

    # A two-facet cone Lyapunov function closes even though the P_0=A facet
    # does not contract into itself.  The routing is 0 -> 1 and 1 -> 1.
    facet_zero = matrix
    facet_one = sp.simplify(fixed_output / rate)
    terminal_facet_gap = sp.simplify(rate * facet_one - covariance_adjoint(facet_one, maps))
    upper_facet_gap = sp.simplify(tail_kappa * matrix - facet_one)
    lower_trial_kappa = sp.Rational(1017, 1000)
    lower_trial_gap = sp.simplify(lower_trial_kappa * matrix - facet_one)
    assert covariance_adjoint(facet_zero, maps) == rate * facet_one
    assert all(value >= 0 for value in principal_minor_values(facet_one))
    assert all(value >= 0 for value in principal_minor_values(upper_facet_gap))
    assert all(value > 0 for value in principal_minor_values(terminal_facet_gap))
    assert lower_trial_gap.det() < 0

    updates = coordinate_updates(matrix)
    commutator_records: list[dict[str, str]] = []
    for first, second in ((0, 1), (1, 2)):
        commutator = updates[first] * updates[second] - updates[second] * updates[first]
        norm_squared = sp.expand(sum(entry * entry for entry in commutator))
        assert norm_squared > 0
        commutator_records.append(
            {
                "pair_zero_based": f"{first},{second}",
                "frobenius_norm_squared": frac(norm_squared),
            }
        )

    # The adaptive certificate implies these necessities for every power.  We
    # check the first eight exactly to guard the direction and prefactor.
    block_power_records: list[dict[str, object]] = []
    power = matrix
    for epoch_count in range(1, 9):
        power = covariance_adjoint(power, maps)
        gap = sp.simplify((rate**epoch_count) * tail_kappa * matrix - power)
        minors = all_principal_minors(gap)
        assert all(value >= 0 for value in principal_minor_values(gap))
        block_power_records.append(
            {
                "epoch_count": epoch_count,
                "all_gap_principal_minors": minors,
                "determinant": frac(gap.det()),
            }
        )

    # Concrete exact use of the power obstruction: a slightly faster q and
    # fixed kappa=2 fail at epoch 11 on an integer ray.
    attacked_rate = sp.Rational(7, 50)
    attacked_kappa = sp.Integer(2)
    attacked_power = matrix
    for _ in range(11):
        attacked_power = covariance_adjoint(attacked_power, maps)
    attacked_gap = sp.simplify(
        attacked_kappa * attacked_rate**11 * matrix - attacked_power
    )
    attacked_ray = sp.Matrix([-2, 4, -3])
    attacked_value = sp.factor((attacked_ray.T * attacked_gap * attacked_ray)[0])
    assert attacked_value < 0

    return {
        "family": "noncommuting rational three-coordinate chain",
        "A": matrix_strings(matrix),
        "unit_diagonal": True,
        "characteristic_polynomial": frac(matrix.charpoly().as_expr()),
        "eigenvalues_exact": ["1/2", "1", "3/2"],
        "mu": frac(mu),
        "q": frac(rate),
        "history_kappa": frac(history_kappa),
        "two_facet_kappa": frac(tail_kappa),
        "Mstar_A": matrix_strings(fixed_output),
        "bellman_equals_triangular_inverse_moment": bellman == triangular,
        "energy_identity_A_minus_MstarA_equals_A_H_A": matrix - fixed_output == matrix * bellman * matrix,
        "fixed_A_gap_qA_minus_MstarA_principal_minors": all_principal_minors(fixed_gap),
        "fixed_A_gap_determinant_is_negative": frac(fixed_gap.det()),
        "fixed_A_exact_negative_ray": {
            "vector": ["-2", "4", "-3"],
            "quadratic_value": frac(fixed_witness_value),
        },
        "two_facet_cone_certificate": {
            "P_0": matrix_strings(facet_zero),
            "P_1_equals_q_inverse_Mstar_P0": matrix_strings(facet_one),
            "routing": {"0": 1, "1": 1},
            "Mstar_P0_equals_q_P1": True,
            "q_P1_minus_Mstar_P1_principal_minors": all_principal_minors(terminal_facet_gap),
            "P1_psd_principal_minors": all_principal_minors(facet_one),
            "kappaA_minus_P1_principal_minors": all_principal_minors(upper_facet_gap),
            "canonical_P1_metric_comparison_bracket": {
                "passing_kappa": frac(tail_kappa),
                "passing_gap_determinant": frac(upper_facet_gap.det()),
                "failing_trial_kappa": frac(lower_trial_kappa),
                "failing_gap_determinant": frac(lower_trial_gap.det()),
                "scope": "This brackets the chosen canonical P1 only; it is not an infeasibility proof for every possible tail R.",
            },
        },
        "adaptive_path_metrics": path_records,
        "coordinate_update_noncommutators": commutator_records,
        "block_power_prefactor_checks": block_power_records,
        "exact_block_power_obstruction": {
            "q": frac(attacked_rate),
            "kappa": frac(attacked_kappa),
            "epoch_count": 11,
            "ray": ["-2", "4", "-3"],
            "quadratic_value": frac(attacked_value),
            "scope": "Refutes only this q,kappa pair for the adaptive certificate; it is not a C050 counterexample.",
        },
    }


def five_facet_phase_certificate() -> dict[str, object]:
    """Exact finite-horizon cone closure beyond the first canonical tail facet."""
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
    first_output = covariance_adjoint(matrix, maps)
    facets = [matrix]
    for _ in range(4):
        facets.append(sp.simplify(covariance_adjoint(facets[-1], maps) / rate))

    records: list[dict[str, object]] = []
    for index, facet in enumerate(facets):
        upper_gap = sp.simplify(kappa * matrix - facet)
        assert all(value > 0 for value in [
            facet[:size, :size].det() for size in range(1, 4)
        ])
        assert all(value > 0 for value in [
            upper_gap[:size, :size].det() for size in range(1, 4)
        ])
        records.append(
            {
                "index": index,
                "P": matrix_strings(facet),
                "P_leading_principal_minors": leading_principal_minors(facet),
                "kappaA_minus_P_leading_principal_minors": leading_principal_minors(upper_gap),
            }
        )
        if index < 4:
            assert covariance_adjoint(facet, maps) == rate * facets[index + 1]

    terminal_gap = sp.simplify(rate * facets[-1] - covariance_adjoint(facets[-1], maps))
    assert all(value > 0 for value in [
        terminal_gap[:size, :size].det() for size in range(1, 4)
    ])

    failed_shorter_self_loops: list[dict[str, str | int]] = []
    for index, facet in enumerate(facets[:-1]):
        self_loop_gap = sp.simplify(rate * facet - covariance_adjoint(facet, maps))
        minors = all_principal_minors(self_loop_gap)
        negative = next((key, value) for key, value in minors.items() if sp.Rational(value) < 0)
        failed_shorter_self_loops.append(
            {
                "facet_index": index,
                "negative_principal_subset": negative[0],
                "negative_principal_minor": negative[1],
            }
        )

    attack_ray = sp.Matrix([-1, 1, -1])
    fixed_gap = sp.simplify(rate * facets[0] - covariance_adjoint(facets[0], maps))
    first_tail_gap = sp.simplify(rate * facets[1] - covariance_adjoint(facets[1], maps))
    fixed_value = sp.factor((attack_ray.T * fixed_gap * attack_ray)[0])
    first_tail_value = sp.factor((attack_ray.T * first_tail_gap * attack_ray)[0])
    assert fixed_value < 0
    assert first_tail_value < 0

    # A separately scouted rational tail matrix repairs the failed canonical
    # P1 self-loop with a modest comparison factor.
    rational_tail = sp.Matrix(
        [
            [sp.Rational(153, 500), sp.Rational(3, 200), sp.Rational(2283, 10000)],
            [sp.Rational(3, 200), sp.Rational(833, 1250), sp.Rational(13, 625)],
            [sp.Rational(2283, 10000), sp.Rational(13, 625), sp.Rational(4767, 10000)],
        ]
    )
    rational_tail_kappa = sp.Rational(13, 10)
    rational_tail_first_gap = sp.simplify(rate * rational_tail - first_output)
    rational_tail_terminal_gap = sp.simplify(
        rate * rational_tail - covariance_adjoint(rational_tail, maps)
    )
    rational_tail_upper_gap = sp.simplify(rational_tail_kappa * matrix - rational_tail)
    for positive_matrix in (
        rational_tail,
        rational_tail_first_gap,
        rational_tail_terminal_gap,
        rational_tail_upper_gap,
    ):
        assert all(value > 0 for value in [
            positive_matrix[:size, :size].det() for size in range(1, 4)
        ])

    # Exact resolvent tail: (qI-M*)R_res=M*(A).  It always gives a two-facet
    # certificate here, but its comparison factor is dramatically worse.
    symmetric_basis: list[sp.Matrix] = []
    upper_indices: list[tuple[int, int]] = []
    for row in range(3):
        for column in range(row, 3):
            basis = sp.zeros(3)
            basis[row, column] = 1
            basis[column, row] = 1
            symmetric_basis.append(basis)
            upper_indices.append((row, column))

    def coordinates(weight: sp.Matrix) -> sp.Matrix:
        return sp.Matrix([weight[row, column] for row, column in upper_indices])

    operator = sp.Matrix.hstack(*[
        coordinates(covariance_adjoint(basis, maps)) for basis in symmetric_basis
    ])
    resolvent_coefficients = (rate * sp.eye(6) - operator).inv() * coordinates(first_output)
    resolvent = sp.zeros(3)
    for coefficient, basis in zip(resolvent_coefficients, symmetric_basis, strict=True):
        resolvent += coefficient * basis
    resolvent = sp.simplify(resolvent)
    resolvent_identity = sp.simplify(
        rate * resolvent - covariance_adjoint(resolvent, maps) - first_output
    )
    assert resolvent_identity == sp.zeros(3)
    resolvent_upper = sp.simplify(51 * matrix - resolvent)
    assert all(value > 0 for value in [
        resolvent[:size, :size].det() for size in range(1, 4)
    ])
    assert all(value > 0 for value in [
        resolvent_upper[:size, :size].det() for size in range(1, 4)
    ])
    trial_resolvent_gap = sp.simplify(50 * matrix - resolvent)
    trial_resolvent_value = sp.factor(
        (sp.Matrix([-2, 4, -3]).T * trial_resolvent_gap * sp.Matrix([-2, 4, -3]))[0]
    )
    assert trial_resolvent_value < 0

    return {
        "family": "same rational noncommuting n=3 chain at a more aggressive phase rate",
        "A": matrix_strings(matrix),
        "mu": "1/2",
        "q": frac(rate),
        "equivalent_local_c0": "17/10",
        "kappa": frac(kappa),
        "routing": "0->1->2->3->4 and 4->4",
        "facets": records,
        "failed_shorter_canonical_self_loops": failed_shorter_self_loops,
        "terminal_gap_leading_principal_minors": leading_principal_minors(terminal_gap),
        "fixed_facet_failure": {
            "ray": ["-1", "1", "-1"],
            "quadratic_value": frac(fixed_value),
        },
        "first_canonical_tail_facet_failure": {
            "ray": ["-1", "1", "-1"],
            "quadratic_value": frac(first_tail_value),
            "scope": "Rejects the canonical R=q^{-1}Mstar(A) self-loop only, not every possible two-facet tail matrix.",
        },
        "noncanonical_rational_two_facet_tail": {
            "R": matrix_strings(rational_tail),
            "kappa": frac(rational_tail_kappa),
            "R_leading_principal_minors": leading_principal_minors(rational_tail),
            "qR_minus_MstarA_leading_principal_minors": leading_principal_minors(rational_tail_first_gap),
            "qR_minus_MstarR_leading_principal_minors": leading_principal_minors(rational_tail_terminal_gap),
            "kappaA_minus_R_leading_principal_minors": leading_principal_minors(rational_tail_upper_gap),
            "interpretation": "The failed canonical P1 does not refute the two-facet SDP; this exact rational R succeeds with kappa=13/10. The five-phase max still has the sharper kappa=6/5.",
        },
        "exact_resolvent_two_facet_comparison": {
            "R_res_solves_qI_minus_Mstar_inverse_MstarA": matrix_strings(resolvent),
            "resolvent_identity_is_zero": True,
            "R_res_leading_principal_minors": leading_principal_minors(resolvent),
            "51A_minus_R_res_leading_principal_minors": leading_principal_minors(resolvent_upper),
            "kappa_50_failure_ray": ["-2", "4", "-3"],
            "kappa_50_failure_value": frac(trial_resolvent_value),
            "interpretation": "The exact two-facet resolvent needs comparison factor greater than 50 on this instance, while the five-phase max certificate uses kappa=6/5.",
        },
        "outcome": "Five exact phase facets close at q=3/20 with kappa=6/5 after the fixed facet and first canonical tail self-loop both fail.",
        "scope": "Finite n=3 cone certificate; no lower bound on the necessary number of arbitrary facets",
    }


def nine_facet_phase_depth_stress() -> dict[str, object]:
    """Exact canonical phase-depth stress closer to the limiting rate."""
    matrix = sp.Matrix(
        [
            [1, sp.Rational(3, 10), 0],
            [sp.Rational(3, 10), 1, sp.Rational(2, 5)],
            [0, sp.Rational(2, 5), 1],
        ]
    )
    rate = sp.Rational(147, 1000)
    kappa = sp.Rational(5, 4)
    maps = epoch_maps(matrix)
    facet = matrix
    comparison_records: list[dict[str, object]] = []
    failed_self_loops: list[dict[str, object]] = []
    terminal_minors: dict[str, str] | None = None
    for index in range(9):
        facet_minors = [facet[:size, :size].det() for size in range(1, 4)]
        upper = sp.simplify(kappa * matrix - facet)
        upper_minors = [upper[:size, :size].det() for size in range(1, 4)]
        assert all(value > 0 for value in facet_minors)
        assert all(value > 0 for value in upper_minors)
        comparison_records.append(
            {
                "index": index,
                "P_leading_principal_minors": [frac(value) for value in facet_minors],
                "kappaA_minus_P_leading_principal_minors": [frac(value) for value in upper_minors],
            }
        )

        self_loop_gap = sp.simplify(rate * facet - covariance_adjoint(facet, maps))
        minors = all_principal_minors(self_loop_gap)
        if index < 8:
            negative = next((key, value) for key, value in minors.items() if sp.Rational(value) < 0)
            failed_self_loops.append(
                {
                    "facet_index": index,
                    "negative_principal_subset": negative[0],
                    "negative_principal_minor": negative[1],
                }
            )
            facet = sp.simplify(covariance_adjoint(facet, maps) / rate)
        else:
            assert all(sp.Rational(value) > 0 for value in minors.values())
            terminal_minors = minors

    assert terminal_minors is not None
    return {
        "family": "same rational noncommuting n=3 chain",
        "q": frac(rate),
        "kappa": frac(kappa),
        "routing": "0->1->...->8 and 8->8",
        "failed_canonical_self_loops": failed_self_loops,
        "facet_comparison_records": comparison_records,
        "terminal_gap_all_principal_minors": terminal_minors,
        "outcome": "The first eight canonical self-loops each fail an exact principal-minor test, while the ninth facet closes and all nine facets are strictly below (5/4)A.",
        "scope": "Exact fixed-n canonical-phase stress only; not a lower bound for arbitrary facet architectures and not dimension-growth evidence.",
    }


def signed_block_closure() -> dict[str, object]:
    """Exact signed/block stress obtained from two conjugate n=3 chains."""
    base = sp.Matrix(
        [
            [1, sp.Rational(3, 10), 0],
            [sp.Rational(3, 10), 1, sp.Rational(2, 5)],
            [0, sp.Rational(2, 5), 1],
        ]
    )
    signature = sp.diag(1, -1, 1)
    signed = signature * base * signature
    rate = sp.Rational(7, 40)
    kappa = sp.Rational(509, 500)
    base_maps = epoch_maps(base)
    signed_maps = epoch_maps(signed)

    for (permutation, base_epoch), (signed_permutation, signed_epoch) in zip(
        base_maps, signed_maps, strict=True
    ):
        assert permutation == signed_permutation
        assert signed_epoch == signature * base_epoch * signature

    base_one = covariance_adjoint(base, base_maps) / rate
    signed_one = signature * base_one * signature
    base_facets = [base, base_one]
    signed_facets = [signed, signed_one]
    block_matrix = sp.diag(base, signed)

    # Global permutations only interleave the two block orders.  Exhaustive
    # enumeration at n=6 independently verifies the exact factorization.
    global_maps = epoch_maps(block_matrix)
    assert len(global_maps) == 720

    compressed_tail = sp.diag(base_one, signed_one)
    compressed_first_gap = sp.simplify(rate * compressed_tail - covariance_adjoint(block_matrix, global_maps))
    compressed_terminal_gap = sp.simplify(rate * compressed_tail - covariance_adjoint(compressed_tail, global_maps))
    compressed_upper_gap = sp.simplify(kappa * block_matrix - compressed_tail)
    assert all(value >= 0 for value in principal_minor_values(compressed_first_gap))
    assert all(value >= 0 for value in principal_minor_values(compressed_terminal_gap))
    assert all(value >= 0 for value in principal_minor_values(compressed_upper_gap))

    records: list[dict[str, object]] = []
    for first_index, first_facet in enumerate(base_facets):
        for second_index, second_facet in enumerate(signed_facets):
            facet = sp.diag(first_facet, second_facet)
            global_pullback = covariance_adjoint(facet, global_maps)
            factored_pullback = sp.diag(
                covariance_adjoint(first_facet, base_maps),
                covariance_adjoint(second_facet, signed_maps),
            )
            assert global_pullback == factored_pullback
            routed = sp.diag(base_one, signed_one)
            dynamic_gap = sp.simplify(rate * routed - global_pullback)
            upper_gap = sp.simplify(kappa * block_matrix - facet)
            assert all(value >= 0 for value in principal_minor_values(dynamic_gap))
            assert all(value >= 0 for value in principal_minor_values(facet))
            assert all(value >= 0 for value in principal_minor_values(upper_gap))
            records.append(
                {
                    "facet_pair": [first_index, second_index],
                    "routed_to": [1, 1],
                    "global_average_equals_independent_block_average": True,
                    "dynamic_gap_determinant": frac(dynamic_gap.det()),
                    "kappaA_minus_facet_determinant": frac(upper_gap.det()),
                }
            )

    return {
        "family": "six-coordinate block diagonal sum of a rational chain and its signed conjugate",
        "A_base": matrix_strings(base),
        "signature": matrix_strings(signature),
        "A_signed": matrix_strings(signed),
        "A_block": matrix_strings(block_matrix),
        "unit_diagonal": True,
        "eigenvalues_exact": ["1/2", "1/2", "1", "1", "3/2", "3/2"],
        "mu": "1/2",
        "q": frac(rate),
        "kappa": frac(kappa),
        "signed_epoch_conjugacy_for_all_six_local_orders": True,
        "global_permutations_exhausted": len(global_maps),
        "four_facet_product_cone": records,
        "compressed_two_facet_tail": {
            "R": matrix_strings(compressed_tail),
            "qR_minus_MstarA_principal_minors": all_principal_minors(compressed_first_gap),
            "qR_minus_MstarR_principal_minors": all_principal_minors(compressed_terminal_gap),
            "kappaA_minus_R_principal_minors": all_principal_minors(compressed_upper_gap),
        },
        "scope": "Exact finite signed/block closure; no all-dimensional block-compression claim",
    }


def coupled_ladder_tail_certificate() -> dict[str, object]:
    """Connected n=6 rational example where two facets beat the A facet."""
    base = sp.Matrix(
        [
            [1, sp.Rational(3, 10), 0],
            [sp.Rational(3, 10), 1, sp.Rational(2, 5)],
            [0, sp.Rational(2, 5), 1],
        ]
    )
    coupling = sp.Rational(1, 10)
    matrix = sp.diag(base, base)
    for index in range(3):
        matrix[index, index + 3] = coupling
        matrix[index + 3, index] = coupling

    rate = sp.Rational(1, 4)
    kappa = sp.Rational(11, 10)
    maps = epoch_maps(matrix)
    assert len(maps) == 720
    first = covariance_adjoint(matrix, maps)
    tail = sp.simplify(first / rate)
    second = covariance_adjoint(first, maps)
    terminal_gap = sp.simplify(rate * tail - covariance_adjoint(tail, maps))
    upper_gap = sp.simplify(kappa * matrix - tail)
    fixed_gap = sp.simplify(rate * matrix - first)

    for positive_matrix in (tail, terminal_gap, upper_gap):
        assert all(value > 0 for value in [
            positive_matrix[:size, :size].det() for size in range(1, 7)
        ])

    fixed_witness = sp.Matrix([-1, 2, -2, 1, -2, 2])
    fixed_value = sp.factor((fixed_witness.T * fixed_gap * fixed_witness)[0])
    assert fixed_value < 0

    updates = coordinate_updates(matrix)
    commutator_pairs = [(0, 1), (1, 2), (0, 3)]
    commutators: list[dict[str, str]] = []
    for first_index, second_index in commutator_pairs:
        difference = (
            updates[first_index] * updates[second_index]
            - updates[second_index] * updates[first_index]
        )
        norm_squared = sp.factor(sum(entry * entry for entry in difference))
        assert norm_squared > 0
        commutators.append(
            {
                "pair_zero_based": f"{first_index},{second_index}",
                "frobenius_norm_squared": frac(norm_squared),
            }
        )

    return {
        "family": "connected six-coordinate rational ladder with two unequal within-chain edges and matching cross-couplings",
        "A": matrix_strings(matrix),
        "unit_diagonal": True,
        "eigenvalues_exact": ["2/5", "3/5", "9/10", "11/10", "7/5", "8/5"],
        "mu": "2/5",
        "q": frac(rate),
        "equivalent_local_c0": "15/8",
        "kappa": frac(kappa),
        "global_permutations_exhausted": len(maps),
        "coordinate_update_noncommutators": commutators,
        "fixed_A_failure": {
            "ray": ["-1", "2", "-2", "1", "-2", "2"],
            "quadratic_value": frac(fixed_value),
            "gap_determinant": frac(fixed_gap.det()),
        },
        "tail_R_equals_q_inverse_MstarA": matrix_strings(tail),
        "tail_R_leading_principal_minors": leading_principal_minors(tail),
        "qR_minus_MstarR_leading_principal_minors": leading_principal_minors(terminal_gap),
        "kappaA_minus_R_leading_principal_minors": leading_principal_minors(upper_gap),
        "Mstar_squared_A": matrix_strings(second),
        "outcome": "Exact Sylvester minors prove a two-facet tail certificate, while an exact rational ray rejects the fixed A facet at the same q.",
        "scope": "Finite connected n=6 certificate; no universal tail-SDP conclusion",
    }


def inherited_inverse_potential_barrier_control() -> dict[str, object]:
    """Check the n=9 C046 matrix without using the refuted potential."""
    n = 9
    rho = sp.Rational(1, 2)
    matrix = (1 - rho) * sp.eye(n) + rho * sp.ones(n)
    identity = sp.eye(n)
    epoch = identity
    for index in range(n):
        coordinate = sp.zeros(n, 1)
        coordinate[index] = 1
        update = identity - coordinate * (coordinate.T * matrix)
        epoch = update * epoch

    one_order_pullback = sp.simplify(epoch.T * matrix * epoch)
    trace = sp.trace(one_order_pullback)
    total_sum = (sp.ones(1, n) * one_order_pullback * sp.ones(n, 1))[0]
    transverse = sp.factor((n * trace - total_sum) / (n * (n - 1)))
    parallel = sp.factor(total_sum / n)
    matrix_transverse = sp.Rational(1, 2)
    matrix_parallel = sp.Integer(5)
    rate = sp.Rational(3, 4)
    transverse_gap = sp.factor(rate * matrix_transverse - transverse)
    parallel_gap = sp.factor(rate * matrix_parallel - parallel)
    assert transverse_gap > 0
    assert parallel_gap > 0

    # Validate the trace/total-sum conjugacy shortcut against exhaustive n=3.
    small = sp.Rational(1, 2) * sp.eye(3) + sp.Rational(1, 2) * sp.ones(3)
    small_maps = epoch_maps(small)
    small_average = covariance_adjoint(small, small_maps)
    small_epoch = small_maps[0][1]
    small_one = small_epoch.T * small * small_epoch
    small_trace = sp.trace(small_one)
    small_total = (sp.ones(1, 3) * small_one * sp.ones(3, 1))[0]
    small_transverse = sp.factor((3 * small_trace - small_total) / 6)
    small_parallel = sp.factor(small_total / 3)
    reconstructed_small = small_transverse * sp.eye(3) + (
        (small_parallel - small_transverse) / 3
    ) * sp.ones(3)
    assert reconstructed_small == small_average

    return {
        "family": "n=9 A=(I+J)/2 from the inherited C046 potential barrier",
        "mu": "1/2",
        "q": "3/4",
        "uniform_permutation_average_method": "all epoch maps are permutation conjugates; the invariant average is reconstructed exactly from one order's trace and total entry sum",
        "shortcut_regression": "matched exhaustive six-order averaging at n=3",
        "MstarA_transverse_eigenvalue": frac(transverse),
        "MstarA_parallel_eigenvalue": frac(parallel),
        "qA_minus_MstarA_transverse_margin": frac(transverse_gap),
        "qA_minus_MstarA_parallel_margin": frac(parallel_gap),
        "outcome": "The fixed A facet itself contracts at q=3/4 on this matrix; the inherited failure of a different inverse remaining-frame potential does not obstruct the tail/cone route here.",
        "scope": "Exact structured control only; it neither repairs the refuted C046 potential nor proves a general rate",
    }


def near_singular_symbolic_family() -> dict[str, object]:
    rho = sp.symbols("rho", positive=True)
    q = sp.symbols("q", positive=True)
    matrix = sp.Matrix([[1, rho], [rho, 1]])
    q12 = sp.Matrix([[rho**2, rho], [rho, 1]])
    q21 = sp.Matrix([[1, rho], [rho, rho**2]])
    p12 = matrix + q12
    p21 = matrix + q21
    selected_energy = rho**2 * (1 - rho**2) / 2
    fixed_output = selected_energy * sp.eye(2)

    maps = epoch_maps(matrix)
    assert maps[0][1].T * q12 * maps[0][1] == sp.zeros(2)
    assert maps[1][1].T * q21 * maps[1][1] == sp.zeros(2)
    assert sp.simplify(matrix - q12) == sp.diag(1 - rho**2, 0)
    assert sp.simplify(matrix - q21) == sp.diag(0, 1 - rho**2)

    determinant_polynomial = sp.factor((q * p12 - fixed_output).det())
    at_q_rho = sp.simplify(rho * p12 - fixed_output)
    q_star = sp.simplify(
        rho**2 * (3 + rho**2 + sp.sqrt(1 + 14 * rho**2 + rho**4)) / 8
    )
    fixed_metric_optimal_q = sp.simplify(rho**2 * (1 + rho) / 2)
    positive_square_side = 1 + 4 * rho - rho**2
    squared_strict_gap = sp.factor(
        positive_square_side**2 - (1 + 14 * rho**2 + rho**4)
    )
    assert sp.simplify(squared_strict_gap - 8 * rho * (1 - rho) * (1 + rho)) == 0

    bellman = bellman_capture(matrix)
    scaled_inverse = (1 - rho) * matrix.inv()
    plus = sp.simplify(
        (1 + rho) * (1 - rho + rho**2 / 2) / (1 - rho)
    )
    minus = sp.simplify(1 + rho + rho**2 / 2)
    assert sp.simplify((plus - minus) - rho**3 / (1 - rho)) == 0

    epsilon = sp.symbols("epsilon", positive=True)
    expansion = sp.series(q_star.subs(rho, 1 - epsilon), epsilon, 0, 3)
    fixed_expansion = sp.series(
        fixed_metric_optimal_q.subs(rho, 1 - epsilon), epsilon, 0, 4
    )

    return {
        "family": "near-singular two-coordinate correlation line",
        "A_rho": [["1", "rho"], ["rho", "1"]],
        "domain": "0 < rho < 1",
        "unit_diagonal": True,
        "eigenvalues": ["1-rho", "1+rho"],
        "mu": "1-rho",
        "history_metrics": {
            "Q_12": matrix_strings(q12),
            "Q_21": matrix_strings(q21),
            "P_12": matrix_strings(p12),
            "P_21": matrix_strings(p21),
            "A_preceq_P_preceq_2A_reason": "Q_pi is PSD and A-Q_pi is the displayed rank-one PSD diagonal matrix",
            "matched_invisibility": "T_pi^T Q_pi T_pi=0 for both orders",
        },
        "Mstar_A": [[frac(selected_energy), "0"], ["0", frac(selected_energy)]],
        "dynamic_gap_determinant_polynomial": frac(determinant_polynomial),
        "q_star_exact": str(q_star),
        "q_star_near_rho_one": str(expansion),
        "fixed_A_optimal_q": frac(fixed_metric_optimal_q),
        "fixed_A_optimal_q_near_rho_one": str(fixed_expansion),
        "adaptive_strict_improvement_proof": {
            "equivalent_positive_comparison": "sqrt(1+14rho^2+rho^4) < 1+4rho-rho^2",
            "difference_of_squares": frac(squared_strict_gap),
            "conclusion": "q_star<q_fixed for every 0<rho<1",
        },
        "q_equals_rho_first_leading_minor": frac(at_q_rho[0, 0]),
        "q_equals_rho_determinant": frac(at_q_rho.det()),
        "consequence": "q=rho=1-mu and kappa=2 is an exact feasible bounded-history certificate throughout the family; q_star is the sharper boundary and equals 1-(11/4)mu+O(mu^2)",
        "frozen_bellman_H": matrix_strings(bellman),
        "mu_A_inverse": matrix_strings(scaled_inverse),
        "generalized_ratios_H_over_mu_Ainv": {
            "parallel": frac(plus),
            "transverse": frac(minus),
            "parallel_minus_transverse": frac(plus - minus),
            "minimum_is_at_least_one": True,
        },
    }


def symbolic_noncommuting_chain_family() -> dict[str, object]:
    r = sp.symbols("r", positive=True)
    matrix = sp.Matrix(
        [
            [1, 3 * r / 5, 0],
            [3 * r / 5, 1, 4 * r / 5],
            [0, 4 * r / 5, 1],
        ]
    )
    maps = epoch_maps(matrix)
    fixed_output = covariance_adjoint(matrix, maps)
    rate = r
    tail = sp.simplify(fixed_output / rate)
    terminal_gap = sp.simplify(rate * tail - covariance_adjoint(tail, maps))
    comparison_gap = sp.simplify(matrix - tail)

    updates = coordinate_updates(matrix)
    first_commutator = updates[0] * updates[1] - updates[1] * updates[0]
    second_commutator = updates[1] * updates[2] - updates[2] * updates[1]
    first_norm = sp.factor(sum(entry * entry for entry in first_commutator))
    second_norm = sp.factor(sum(entry * entry for entry in second_commutator))
    assert first_norm > 0
    assert second_norm > 0

    tail_psd = polynomial_psd_record(tail, r)
    comparison_psd = polynomial_psd_record(comparison_gap, r)
    terminal_psd = polynomial_psd_record(terminal_gap, r)

    return {
        "family": "symbolic noncommuting three-coordinate chain A_r",
        "A_r": matrix_strings(matrix),
        "domain": "0 < r < 1",
        "unit_diagonal": True,
        "characteristic_polynomial": frac(matrix.charpoly().as_expr()),
        "eigenvalues": ["1-r", "1", "1+r"],
        "mu": "1-r",
        "q": "r=1-mu",
        "coordinate_update_noncommutator_norm_squares": [frac(first_norm), frac(second_norm)],
        "R_equals_q_inverse_MstarA": matrix_strings(tail),
        "R_psd_principal_minor_Bernstein_certificates": tail_psd,
        "A_minus_R_psd_principal_minor_Bernstein_certificates": comparison_psd,
        "qR_minus_MstarR_psd_principal_minor_Bernstein_certificates": terminal_psd,
        "consequence": "Exact Bernstein coefficients prove 0<=R<=A, Mstar(A)=qR, and Mstar(R)<=qR for every 0<r<1. In particular Mstar(A)<=qA, giving expected-distance rate exp(-mu*k/2) on this structured family.",
        "evidence_scope": "All-parameter n=3 proof draft with exact coefficient certificate; not independently audited and not an all-dimensional claim",
    }


def state_growth() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for n in range(2, 11):
        permutations = sp.factorial(n)
        symmetric_entries = n * (n + 1) // 2
        ordered_prefixes = sum(
            sp.factorial(n) // sp.factorial(n - depth) for depth in range(n + 1)
        )
        rows.append(
            {
                "n": n,
                "permutation_metrics": int(permutations),
                "scalar_metric_variables": int(permutations * symmetric_entries),
                "ordered_prefix_states": int(ordered_prefixes),
                "remaining_subset_states": 2**n,
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    result = {
        "schema_version": "1.0",
        "arithmetic": "exact sympy Rational plus symbolic factorization; no floating-point decision",
        "scope": "finite n=3 and signed/connected n=6 certificates, symbolic n=2 and n=3 families, exact phase-depth stress, and finite block-power checks; not a general C050 proof",
        "noncommuting_certificate": exact_three_dimensional_certificate(),
        "five_facet_phase_certificate": five_facet_phase_certificate(),
        "nine_facet_phase_depth_stress": nine_facet_phase_depth_stress(),
        "near_singular_family": near_singular_symbolic_family(),
        "symbolic_noncommuting_chain_family": symbolic_noncommuting_chain_family(),
        "coupled_ladder_tail_certificate": coupled_ladder_tail_certificate(),
        "signed_block_closure": signed_block_closure(),
        "inherited_inverse_potential_barrier_control": inherited_inverse_potential_barrier_control(),
        "adaptive_state_growth": state_growth(),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        payload = encoded.encode("utf-8")
        arguments.output.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        print(json.dumps({"output": str(arguments.output), "sha256": digest}))
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
