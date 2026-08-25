#!/usr/bin/env python3
"""Exact checks for the locked exchangeable-transposition RPCD route.

All decisive calculations use sympy Rational arithmetic.  The floating-point
random scan at the end is deliberately optional and is labelled numerical.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math

import numpy as np
import sympy as sp


def update(A: sp.Matrix, i: int) -> sp.Matrix:
    """Return U_i = I-e_i e_i^T A."""
    n = A.rows
    e = sp.eye(n)[:, i]
    return sp.eye(n) - e * (e.T * A)


def dissipation(A: sp.Matrix, r0: sp.Matrix, order: tuple[int, ...]) -> sp.Rational:
    """Compute sum of squared visited residuals exactly."""
    r = r0
    total = sp.Rational(0)
    for i in order:
        d = r[i]
        total += d**2
        r = r - A[:, i] * d
    return sp.factor(total)


def signed_equicorrelation(n: int, rho: sp.Rational, signs: list[int]) -> sp.Matrix:
    s = sp.Matrix(signs)
    return (1 - rho) * sp.eye(n) + rho * (s * s.T)


def exact_counterexample() -> dict:
    n = 17
    rho = sp.Rational(99, 100)
    delta = 1 - rho
    signs = [1 if i % 3 else -1 for i in range(n)]
    A = signed_equicorrelation(n, rho, signs)
    s = sp.Matrix(signs)
    lam_low = delta
    lam_high = 1 + (n - 1) * rho
    ldl_pivots = [sp.Rational(1)] + [
        sp.factor(delta * (delta + k * rho) / (delta + (k - 1) * rho))
        for k in range(2, n + 1)
    ]
    assert all(pivot > 0 for pivot in ldl_pivots)
    x = s / lam_high
    assert A * x == s

    formula_D = sp.factor(sum(delta ** (2 * t) for t in range(n)))
    ratio = sp.factor(formula_D / n)
    margin = sp.factor(sp.Rational(1, 16) - ratio)
    initial_energy = sp.factor((x.T * A * x)[0])
    target_ratio = sp.factor(formula_D / (lam_low * initial_energy))
    assert margin > 0

    # Several orders certify that the signed recurrence is label/order invariant.
    sample_orders = [
        tuple(range(n)),
        tuple(reversed(range(n))),
        tuple(list(range(0, n, 2)) + list(range(1, n, 2))),
    ]
    for order in sample_orders:
        assert dissipation(A, s, order) == formula_D

    # The coordinate-update factors genuinely fail to commute.
    commutator_witness = sp.simplify((update(A, 1) * update(A, 0) - update(A, 0) * update(A, 1)) * x)
    assert commutator_witness != sp.zeros(n, 1)

    # A short integer proof of the strict margin, avoiding reliance on decimals:
    # D < 1/(1-delta^2)=10000/9999, and 16*10000 < 17*9999.
    strict_integer_gap = 17 * 9999 - 16 * 10000
    assert strict_integer_gap == 9983

    return {
        "family": "signed_equicorrelation",
        "n": n,
        "rho": str(rho),
        "signs": signs,
        "eigenvalue_low": str(lam_low),
        "eigenvalue_high": str(lam_high),
        "exact_ldlt_pivots": [str(v) for v in ldl_pivots],
        "initial_x_scale_times_sign_vector": str(1 / lam_high),
        "initial_residual": "sign vector",
        "dissipation": str(formula_D),
        "dissipation_over_residual_norm_squared": str(ratio),
        "initial_A_energy": str(initial_energy),
        "dissipation_over_mu_initial_A_energy": str(target_ratio),
        "one_sixteenth_minus_ratio": str(margin),
        "one_sixteenth_minus_ratio_decimal": f"{float(margin):.17g}",
        "strict_integer_gap": strict_integer_gap,
        "noncommuting_witness_squared_norm": str(sp.factor((commutator_witness.T * commutator_witness)[0])),
    }


def adjacent_swap_identity_check() -> dict:
    # A nonsymmetric-under-labels rational SPD example, verified by Sylvester.
    A = sp.Matrix(
        [
            [1, sp.Rational(1, 3), sp.Rational(-1, 5)],
            [sp.Rational(1, 3), 1, sp.Rational(1, 4)],
            [sp.Rational(-1, 5), sp.Rational(1, 4), 1],
        ]
    )
    leading_minors = [sp.factor(A[:k, :k].det()) for k in range(1, 4)]
    assert all(v > 0 for v in leading_minors)
    r = sp.Matrix([sp.Rational(7, 6), sp.Rational(-2, 5), sp.Rational(3, 7)])
    z = A.inv() * r
    a, b = 0, 1
    alpha, beta, q = r[a], r[b], A[a, b]
    z_ab = update(A, b) * update(A, a) * z
    z_ba = update(A, a) * update(A, b) * z
    endpoint_rhs = q * (alpha * sp.eye(3)[:, b] - beta * sp.eye(3)[:, a])
    assert sp.simplify(z_ab - z_ba - endpoint_rhs) == sp.zeros(3, 1)

    d_ab = alpha**2 + (beta - q * alpha) ** 2
    d_ba = beta**2 + (alpha - q * beta) ** 2
    scalar_rhs = q**2 * (alpha**2 - beta**2)
    assert sp.factor(d_ab - d_ba - scalar_rhs) == 0
    return {
        "matrix": [[str(v) for v in A.row(i)] for i in range(3)],
        "leading_principal_minors": [str(v) for v in leading_minors],
        "alpha": str(alpha),
        "beta": str(beta),
        "q": str(q),
        "endpoint_difference_squared_norm": str(sp.factor(((z_ab - z_ba).T * (z_ab - z_ba))[0])),
        "two_step_dissipation_difference": str(sp.factor(d_ab - d_ba)),
    }


def random_transposition_dirichlet_check() -> dict:
    # The formula is universal in r.  A concrete rational mean-zero vector checks it.
    r = [sp.Rational(-3), sp.Rational(-1), sp.Rational(0), sp.Rational(1), sp.Rational(3)]
    n = len(r)
    centered_norm_sq = sum(v**2 for v in r)
    variance = centered_norm_sq / n
    # Enumerate permutations and unordered position pairs exactly.
    total = sp.Rational(0)
    count = 0
    for p in itertools.permutations(range(n)):
        for i in range(n):
            for j in range(i + 1, n):
                pp = list(p)
                pp[i], pp[j] = pp[j], pp[i]
                total += (r[p[0]] - r[pp[0]]) ** 2
                count += 1
    mean_square_difference = sp.factor(total / count)
    formula = sp.factor(4 * centered_norm_sq / (n * (n - 1)))
    assert mean_square_difference == formula
    dirichlet = mean_square_difference / 2
    poincare_ratio = sp.factor(dirichlet / variance)
    assert poincare_ratio == sp.Rational(2, n - 1)
    return {
        "n": n,
        "centered_residual_vector": [str(v) for v in r],
        "variance_first_position": str(variance),
        "mean_square_pair_difference": str(mean_square_difference),
        "dirichlet_over_variance": str(poincare_ratio),
        "general_formula": "Dirichlet/Var = 2/(n-1)",
        "required_poincare_multiplier": "(n-1)/2",
    }


def equicorrelation_pair_variance_check() -> dict:
    """Exact terminal pair discrepancy on the sharp equicorrelation family."""
    n = 17
    delta = sp.Rational(1, 100)
    rho = 1 - delta
    pair_terms = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            # At termination the two iterates differ by
            # (delta^(j-1)-delta^(i-1))(e_a-e_b).  Its A-energy is below.
            pair_terms.append(2 * delta * (delta ** (i - 1) - delta ** (j - 1)) ** 2)
    mean_terminal_pair_energy = sp.factor(sum(pair_terms) / sp.binomial(n, 2))
    initial_energy = sp.factor(sp.Rational(n, 1) / (1 + (n - 1) * rho))
    mu_energy = sp.factor(delta * initial_energy)
    relative_proxy = sp.factor(mean_terminal_pair_energy / mu_energy)
    return {
        "family": "positive_equicorrelation_terminal_swap_discrepancy",
        "n": n,
        "delta_equals_mu": str(delta),
        "mean_terminal_pair_A_energy": str(mean_terminal_pair_energy),
        "mu_times_initial_A_energy": str(mu_energy),
        "proxy_over_mu_energy": str(relative_proxy),
        "proxy_over_mu_energy_decimal": f"{float(relative_proxy):.17g}",
        "delta_to_zero_asymptotic": "mean pair energy ~ 4*mu/n and ratio to mu*initial energy ~ 4/n",
        "scalar_dissipation_pair_difference": "0 for every transposition",
    }


def equicorrelation_permutation_martingale_check() -> dict:
    """Exact Doob-innovation decomposition on the locked obstruction family."""
    n = 17
    delta = sp.Rational(1, 100)
    rho = 1 - delta
    high_eigenvalue = delta + n * rho
    weights = [delta**j for j in range(n)]
    weight_mean = sp.factor(sum(weights) / n)
    centered_weight_sum = sp.factor(sum((value - weight_mean) ** 2 for value in weights))
    endpoint_variance = sp.factor(delta * centered_weight_sum)

    innovation_terms = []
    for step in range(1, n):
        remaining = n - step + 1
        old_remaining_mean = sp.factor(
            sum(delta**j for j in range(step - 1, n)) / remaining
        )
        difference = sp.factor(delta ** (step - 1) - old_remaining_mean)
        innovation_terms.append(
            sp.factor(delta * sp.Rational(remaining, remaining - 1) * difference**2)
        )
    innovation_sum = sp.factor(sum(innovation_terms))
    assert innovation_sum == endpoint_variance

    initial_energy = sp.factor(sp.Rational(n, 1) / high_eigenvalue)
    dissipation_value = sp.factor(sum(delta ** (2 * j) for j in range(n)))
    mean_endpoint_coefficient = sp.factor(1 / high_eigenvalue - weight_mean)
    mean_endpoint_energy = sp.factor(
        n * high_eigenvalue * mean_endpoint_coefficient**2
    )
    assert sp.factor(mean_endpoint_energy + endpoint_variance) == sp.factor(
        initial_energy - dissipation_value
    )

    average_pair_difference_energy = sp.factor(
        sp.Rational(4, n - 1) * endpoint_variance
    )
    assert sp.factor(
        sp.Rational(n - 1, 4) * average_pair_difference_energy
    ) == endpoint_variance
    return {
        "family": "signed_equicorrelation_high_eigen_residual",
        "n": n,
        "delta_equals_mu": str(delta),
        "revealed_weight_at_step_t": "delta^(t-1)",
        "unrevealed_conditional_weight": "average of the remaining powers of delta",
        "innovation_energy_formula": "delta*m*(delta^(t-1)-a_(t-1))^2/(m-1), m=n-t+1",
        "innovation_sum": str(innovation_sum),
        "endpoint_variance": str(endpoint_variance),
        "innovation_sum_equals_endpoint_variance": True,
        "mean_energy_plus_variance_equals_initial_energy_minus_dissipation": True,
        "transposition_dirichlet_times_n_minus_1_over_4_equals_variance": True,
        "interpretation": "The Doob martingale and global transposition proxy are both exact on this standard-representation family; this avoids dimensional loss here but proves no universal contraction.",
    }


def arrow_family_check() -> dict:
    # m=s^2 leaves, hub-leaf coupling q/s.  Eigenvalues are 1-q,1,1+q.
    s = 4
    m = s * s
    q = sp.Rational(99, 100)
    a = q / s
    A = sp.eye(m + 1)
    for j in range(1, m + 1):
        A[0, j] = a
        A[j, 0] = a
    r_high = sp.Matrix([s] + [1] * m)
    r_low = sp.Matrix([-s] + [1] * m)
    assert A * r_high == (1 + q) * r_high
    assert A * r_low == (1 - q) * r_low

    values = []
    low_values = []
    for k in range(m + 1):
        d_hub = s * (1 - q * sp.Rational(k, m))
        d_late = 1 - q + q**2 * sp.Rational(k, m)
        Dk = sp.factor(k + d_hub**2 + (m - k) * d_late**2)
        values.append(Dk)
        low_d_hub = -s * (1 + q * sp.Rational(k, m))
        low_d_late = 1 + q + q**2 * sp.Rational(k, m)
        low_values.append(sp.factor(k + low_d_hub**2 + (m - k) * low_d_late**2))
    average_D = sp.factor(sum(values) / (m + 1))
    low_average_D = sp.factor(sum(low_values) / (m + 1))
    residual_ratio = sp.factor(average_D / (2 * m))
    energy = sp.factor((r_high.T * A.inv() * r_high)[0])
    mu_energy = sp.factor((1 - q) * energy)
    target_ratio = sp.factor(average_D / mu_energy)
    low_target_ratio = sp.factor(low_average_D / (2 * m))
    commutator = update(A, 1) * update(A, 0) - update(A, 0) * update(A, 1)
    assert commutator != sp.zeros(m + 1)
    return {
        "family": "hub_leaf_arrow",
        "dimension": m + 1,
        "m_leaves": m,
        "q": str(q),
        "hub_leaf_entry": str(a),
        "eigenvalues": [str(1 - q), "1 (multiplicity m-1)", str(1 + q)],
        "initial_residual": "(sqrt(m),1,...,1), high-eigenvalue direction",
        "average_dissipation": str(average_D),
        "dissipation_over_residual_norm_squared": str(residual_ratio),
        "dissipation_over_mu_energy": str(target_ratio),
        "low_eigen_residual": "(-sqrt(m),1,...,1)",
        "low_eigen_average_dissipation": str(low_average_D),
        "low_eigen_dissipation_over_mu_energy": str(low_target_ratio),
        "q_to_one_and_m_to_infinity_residual_ratio": "11/24",
    }


def block_signed_check() -> dict:
    # Unequal, signed 2x2 blocks give a nonsymmetric block family.  Inter-block
    # updates commute; within each nonzero block they do not.
    qs = [sp.Rational(9, 10), sp.Rational(-4, 5), sp.Rational(2, 3)]
    blocks = [sp.Matrix([[1, q], [q, 1]]) for q in qs]
    A = sp.diag(*blocks)
    r = sp.Matrix([1, 1, 1, -1, 2, -1])
    perms = list(itertools.permutations(range(6)))
    average_D = sp.factor(sum(dissipation(A, r, p) for p in perms) / len(perms))
    ratio = sp.factor(average_D / (r.T * r)[0])
    eig_lower_bounds = [1 - abs(q) for q in qs]
    assert min(eig_lower_bounds) > 0
    return {
        "family": "unequal_signed_two_by_two_blocks",
        "block_correlations": [str(q) for q in qs],
        "minimum_eigenvalue": str(min(eig_lower_bounds)),
        "initial_residual": [str(v) for v in r],
        "exact_average_dissipation": str(average_D),
        "dissipation_over_residual_norm_squared": str(ratio),
        "permutations_enumerated": len(perms),
    }


def epoch_matrix(A: sp.Matrix, order: tuple[int, ...]) -> sp.Matrix:
    T = sp.eye(A.rows)
    for i in order:
        T = update(A, i) * T
    return sp.simplify(T)


def all_principal_minors(M: sp.Matrix) -> list[sp.Rational]:
    vals = []
    for size in range(1, M.rows + 1):
        for idx in itertools.combinations(range(M.rows), size):
            vals.append(sp.factor(M.extract(idx, idx).det()))
    return vals


def exact_pair_proxy_slice(A: sp.Matrix, mu: sp.Rational, label: str) -> dict:
    """Check B <= (1-mu)A and E[T^TAT] <= B on one rational slice."""
    n = A.rows
    perms = list(itertools.permutations(range(n)))
    matrices = {p: epoch_matrix(A, p) for p in perms}
    mean_T = sum(matrices.values(), sp.zeros(n)) / len(perms)
    actual = sum((T.T * A * T for T in matrices.values()), sp.zeros(n)) / len(perms)
    pair_sum = sp.zeros(n)
    pair_count = 0
    for p, T in matrices.items():
        for i in range(n):
            for j in range(i + 1, n):
                pp = list(p)
                pp[i], pp[j] = pp[j], pp[i]
                diff = T - matrices[tuple(pp)]
                pair_sum += diff.T * A * diff
                pair_count += 1
    pair_average = pair_sum / pair_count
    proxy = sp.simplify(mean_T.T * A * mean_T + sp.Rational(n - 1, 4) * pair_average)
    poincare_slack = sp.simplify(proxy - actual)
    gap_at_c_one = sp.simplify((1 - mu) * A - proxy)
    slack_minors = all_principal_minors(poincare_slack)
    gap_minors = all_principal_minors(gap_at_c_one)
    assert all(v >= 0 for v in slack_minors)
    assert all(v >= 0 for v in gap_minors)
    return {
        "label": label,
        "dimension": n,
        "mu": str(mu),
        "permutations": len(perms),
        "ordered_permutation_unordered_pair_cases": pair_count,
        "poincare_slack_all_principal_minors_nonnegative": True,
        "c_equals_one_gap_all_principal_minors_nonnegative": True,
        "poincare_slack_determinant": str(sp.factor(poincare_slack.det())),
        "c_equals_one_gap_determinant": str(sp.factor(gap_at_c_one.det())),
        "smallest_poincare_slack_principal_minor": str(min(slack_minors)),
        "smallest_c_equals_one_gap_principal_minor": str(min(gap_minors)),
    }


def exact_pair_proxy_slices() -> list[dict]:
    rho = sp.Rational(9, 10)
    eq = signed_equicorrelation(5, rho, [1, -1, 1, 1, -1])

    q = sp.Rational(9, 10)
    star = sp.eye(5)
    for j in range(1, 5):
        star[0, j] = q / 2
        star[j, 0] = q / 2

    blocks = sp.diag(
        sp.Matrix([[1, sp.Rational(9, 10)], [sp.Rational(9, 10), 1]]),
        sp.Matrix([[1, sp.Rational(-4, 5)], [sp.Rational(-4, 5), 1]]),
    )
    three_blocks = sp.diag(
        blocks,
        sp.Matrix([[1, sp.Rational(2, 3)], [sp.Rational(2, 3), 1]]),
    )
    interacting_hadamard = sp.Matrix(
        [
            [1, sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(-1, 10)],
            [sp.Rational(1, 2), 1, sp.Rational(-1, 10), sp.Rational(1, 4)],
            [sp.Rational(1, 4), sp.Rational(-1, 10), 1, sp.Rational(1, 2)],
            [sp.Rational(-1, 10), sp.Rational(1, 4), sp.Rational(1, 2), 1],
        ]
    )
    return [
        exact_pair_proxy_slice(eq, sp.Rational(1, 10), "signed_equicorrelation_n5_rho_9_over_10"),
        exact_pair_proxy_slice(star, sp.Rational(1, 10), "symmetry_breaking_star_n5_q_9_over_10"),
        exact_pair_proxy_slice(blocks, sp.Rational(1, 10), "unequal_signed_blocks_n4"),
        exact_pair_proxy_slice(three_blocks, sp.Rational(1, 10), "unequal_signed_blocks_n6"),
        exact_pair_proxy_slice(
            interacting_hadamard,
            sp.Rational(3, 20),
            "interacting_signed_hadamard_n4",
        ),
    ]


def exact_two_epoch_proxy_control() -> dict:
    n = 3
    rho = sp.Rational(9, 10)
    mu = 1 - rho
    A = (1 - rho) * sp.eye(n) + rho * sp.ones(n)
    permutations = list(itertools.permutations(range(n)))
    one_epoch = {p: epoch_matrix(A, p) for p in permutations}
    sequences = list(itertools.product(permutations, repeat=2))
    endpoints = {(p, q): one_epoch[q] * one_epoch[p] for p, q in sequences}
    mean_endpoint = sum(endpoints.values(), sp.zeros(n)) / len(sequences)
    actual = sum(
        (T.T * A * T for T in endpoints.values()), sp.zeros(n)
    ) / len(sequences)
    dirichlet_sum = sp.zeros(n)
    cases_per_slot = 0
    for slot in range(2):
        slot_sum = sp.zeros(n)
        slot_cases = 0
        for seq, T in endpoints.items():
            for i, j in itertools.combinations(range(n), 2):
                changed = [list(seq[0]), list(seq[1])]
                changed[slot][i], changed[slot][j] = changed[slot][j], changed[slot][i]
                changed_key = (tuple(changed[0]), tuple(changed[1]))
                diff = T - endpoints[changed_key]
                slot_sum += diff.T * A * diff
                slot_cases += 1
        dirichlet_sum += slot_sum / slot_cases
        cases_per_slot = slot_cases
    proxy = sp.simplify(mean_endpoint.T * A * mean_endpoint + sp.Rational(n - 1, 4) * dirichlet_sum)
    poincare_slack = sp.simplify(proxy - actual)
    gap = sp.simplify((1 - mu) * A - proxy)
    slack_minors = all_principal_minors(poincare_slack)
    gap_minors = all_principal_minors(gap)
    assert all(v >= 0 for v in slack_minors)
    assert all(v >= 0 for v in gap_minors)
    return {
        "family": "positive_equicorrelation_n3_rho_9_over_10",
        "epochs": 2,
        "mu": str(mu),
        "permutation_sequences": len(sequences),
        "transposition_cases_per_epoch_slot": cases_per_slot,
        "poincare_slack_all_principal_minors_nonnegative": True,
        "c_equals_one_gap_all_principal_minors_nonnegative": True,
        "poincare_slack_determinant": str(sp.factor(poincare_slack.det())),
        "c_equals_one_gap_determinant": str(sp.factor(gap.det())),
        "evidence_level": "E2 finite verification only",
    }


def exact_two_epoch_interacting_control() -> dict:
    n = 4
    mu = sp.Rational(3, 20)
    A = sp.Matrix(
        [
            [1, sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(-1, 10)],
            [sp.Rational(1, 2), 1, sp.Rational(-1, 10), sp.Rational(1, 4)],
            [sp.Rational(1, 4), sp.Rational(-1, 10), 1, sp.Rational(1, 2)],
            [sp.Rational(-1, 10), sp.Rational(1, 4), sp.Rational(1, 2), 1],
        ]
    )
    # Hadamard eigenbasis gives these exact eigenvalues.
    assert sorted(A.eigenvals().keys()) == [
        sp.Rational(3, 20),
        sp.Rational(17, 20),
        sp.Rational(27, 20),
        sp.Rational(33, 20),
    ]
    permutations = list(itertools.permutations(range(n)))
    one_epoch = {p: epoch_matrix(A, p) for p in permutations}
    endpoints = {
        (p, q): one_epoch[q] * one_epoch[p]
        for p, q in itertools.product(permutations, repeat=2)
    }
    mean_endpoint = sum(endpoints.values(), sp.zeros(n)) / len(endpoints)
    actual = sum(
        (T.T * A * T for T in endpoints.values()), sp.zeros(n)
    ) / len(endpoints)
    dirichlet_sum = sp.zeros(n)
    cases_per_slot = 0
    for slot in range(2):
        slot_sum = sp.zeros(n)
        slot_cases = 0
        for seq, T in endpoints.items():
            for i, j in itertools.combinations(range(n), 2):
                changed = [list(seq[0]), list(seq[1])]
                changed[slot][i], changed[slot][j] = changed[slot][j], changed[slot][i]
                diff = T - endpoints[(tuple(changed[0]), tuple(changed[1]))]
                slot_sum += diff.T * A * diff
                slot_cases += 1
        dirichlet_sum += slot_sum / slot_cases
        cases_per_slot = slot_cases
    proxy = sp.simplify(mean_endpoint.T * A * mean_endpoint + sp.Rational(n - 1, 4) * dirichlet_sum)
    poincare_slack = sp.simplify(proxy - actual)
    gap = sp.simplify((1 - mu) * A - proxy)
    slack_minors = all_principal_minors(poincare_slack)
    gap_minors = all_principal_minors(gap)
    assert all(v >= 0 for v in slack_minors)
    assert all(v >= 0 for v in gap_minors)
    return {
        "family": "interacting_signed_hadamard_n4",
        "matrix_offdiagonal_parameters": ["1/2", "1/4", "-1/10"],
        "epochs": 2,
        "mu": str(mu),
        "permutation_sequences": len(endpoints),
        "transposition_cases_per_epoch_slot": cases_per_slot,
        "poincare_slack_all_principal_minors_nonnegative": True,
        "c_equals_one_gap_all_principal_minors_nonnegative": True,
        "poincare_slack_determinant": str(sp.factor(poincare_slack.det())),
        "c_equals_one_gap_determinant": str(sp.factor(gap.det())),
        "evidence_level": "E2 finite verification only",
    }


def multiepoch_metric_map_recursion_control() -> dict:
    """Avoid factorial-in-epochs enumeration while retaining the pair coupling."""
    n = 4
    mu = sp.Rational(3, 20)
    A = sp.Matrix(
        [
            [1, sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(-1, 10)],
            [sp.Rational(1, 2), 1, sp.Rational(-1, 10), sp.Rational(1, 4)],
            [sp.Rational(1, 4), sp.Rational(-1, 10), 1, sp.Rational(1, 2)],
            [sp.Rational(-1, 10), sp.Rational(1, 4), sp.Rational(1, 2), 1],
        ]
    )
    permutations = list(itertools.permutations(range(n)))
    matrices = {p: epoch_matrix(A, p) for p in permutations}
    mean_matrix = sum(matrices.values(), sp.zeros(n)) / len(permutations)
    pairs = list(itertools.combinations(range(n), 2))

    def energy_map(Q: sp.Matrix) -> sp.Matrix:
        return sp.simplify(
            sum((T.T * Q * T for T in matrices.values()), sp.zeros(n))
            / len(permutations)
        )

    def dirichlet_map(Q: sp.Matrix) -> sp.Matrix:
        total = sp.zeros(n)
        for p, T in matrices.items():
            for i, j in pairs:
                pp = list(p)
                pp[i], pp[j] = pp[j], pp[i]
                difference = T - matrices[tuple(pp)]
                total += difference.T * Q * difference
        return sp.simplify(
            sp.Rational(n - 1, 4) * total / (len(permutations) * len(pairs))
        )

    def energy_power(Q: sp.Matrix, power: int) -> sp.Matrix:
        for _ in range(power):
            Q = energy_map(Q)
        return Q

    checks = {}
    for epochs in range(1, 5):
        mean_endpoint = mean_matrix**epochs
        proxy = mean_endpoint.T * A * mean_endpoint
        for slot in range(1, epochs + 1):
            suffix_metric = energy_power(A, epochs - slot)
            slot_metric = dirichlet_map(suffix_metric)
            proxy += energy_power(slot_metric, slot - 1)
        proxy = sp.simplify(proxy)
        actual = energy_power(A, epochs)
        poincare_slack = sp.simplify(proxy - actual)
        gap = sp.simplify((1 - mu) * A - proxy)
        slack_minors = all_principal_minors(poincare_slack)
        gap_minors = all_principal_minors(gap)
        assert all(value >= 0 for value in slack_minors)
        assert all(value >= 0 for value in gap_minors)
        quotient_matrix = sp.simplify(A.inv() * (A - proxy) / mu)
        assert sp.simplify(quotient_matrix - quotient_matrix.T) == sp.zeros(n)
        quotient_eigenvalues = sorted(quotient_matrix.eigenvals().keys())
        checks[str(epochs)] = {
            "poincare_slack_all_principal_minors_nonnegative": True,
            "c_equals_one_gap_all_principal_minors_nonnegative": True,
            "minimum_generalized_proxy_gap_over_mu": str(quotient_eigenvalues[0]),
            "minimum_generalized_proxy_gap_over_mu_decimal": f"{float(quotient_eigenvalues[0]):.17g}",
            "poincare_slack_determinant": str(sp.factor(poincare_slack.det())),
            "c_equals_one_gap_determinant": str(sp.factor(gap.det())),
        }
    return {
        "family": "interacting_signed_hadamard_n4",
        "mu": str(mu),
        "epochs_checked": [1, 2, 3, 4],
        "recursion": "B_m=(M^m)^T A M^m+sum_{ell=1}^m H^(ell-1) G(H^(m-ell)(A))",
        "energy_map": "H(Q)=E_pi T_pi^T Q T_pi",
        "dirichlet_map": "G(Q)=(n-1)E_{pi,pair}(T_pi-T_pi')^T Q(T_pi-T_pi')/4",
        "checks": checks,
        "interpretation": "Exact E2 controls; the recursion is algebraic and does not diagonalize the covariance superoperator or prove an all-dimensional gap.",
    }


def symbolic_signed_block_proxy() -> dict:
    """Symbolic endpoint quotients for every signed 2x2 block and all n."""
    q = sp.symbols("q", nonnegative=True, real=True)
    c = sp.Rational(4, 3)  # worst allowed inflation, since c_n<4/3
    r_plus = sp.factor(q**2 * (1 - q) * (c * (q + 1) - q + 1) / 4)
    r_minus = sp.factor(q**2 * (q + 1) * (c * (1 - q) + q + 1) / 4)
    gap_plus = sp.factor(q - r_plus)
    gap_minus = sp.factor(q - r_minus)
    assert gap_plus == q * (q**3 + 6 * q**2 - 7 * q + 12) / 12
    assert gap_minus == q * (q - 1) * (q**2 - 5 * q - 12) / 12
    flip_probability_checks = {}
    for n in range(2, 13):
        pair_count = sp.binomial(n, 2)
        flip_count_sum = sum(
            n - (b - a)
            for a in range(1, n + 1)
            for b in range(a + 1, n + 1)
        )
        enumerated_probability = sp.factor(flip_count_sum / pair_count**2)
        formula_probability = sp.factor(sp.Rational(2) * (2 * n - 1) / (3 * n * (n - 1)))
        assert enumerated_probability == formula_probability
        flip_probability_checks[str(n)] = str(enumerated_probability)
    return {
        "orientation_flip_probability": "2(2n-1)/(3n(n-1))",
        "variance_inflation_c_n": "2(2n-1)/(3n), in [1,4/3)",
        "flip_probability_exact_checks_n2_through_n12": flip_probability_checks,
        "worst_inflation_used": str(c),
        "symmetric_generalized_endpoint_quotient": str(r_plus),
        "antisymmetric_generalized_endpoint_quotient": str(r_minus),
        "q_minus_symmetric_quotient": str(gap_plus),
        "q_minus_antisymmetric_quotient": str(gap_minus),
        "sign_on_unit_interval": "both gaps are nonnegative for 0<=q<=1",
        "conclusion": "B_A <= (1-mu)A for arbitrary direct sums of signed 2x2 blocks and isolates",
        "evidence_level": "E3 proof draft; no independent audit",
    }


def permutation_sign(order: tuple[int, ...]) -> int:
    inversions = sum(
        order[i] > order[j]
        for i in range(len(order))
        for j in range(i + 1, len(order))
    )
    return -1 if inversions % 2 else 1


def alternating_mode_checks() -> dict:
    u, v, w = sp.symbols("u v w", real=True)
    symbolic_three = sp.Matrix([[1, u, v], [u, 1, w], [v, w, 1]])
    symbolic_alt_three = sum(
        (
            permutation_sign(p) * epoch_matrix(symbolic_three, p)
            for p in itertools.permutations(range(3))
        ),
        sp.zeros(3),
    ) / sp.factorial(3)
    symbolic_formula = sp.Matrix(
        [
            [v**2 - u**2, u * (w**2 - 1), v * (1 - w**2)],
            [u * (1 - v**2), u**2 - w**2, w * (v**2 - 1)],
            [v * (u**2 - 1), w * (1 - u**2), w**2 - v**2],
        ]
    ) / 6
    assert sp.simplify(symbolic_alt_three - symbolic_formula) == sp.zeros(3)
    assert sp.factor(symbolic_alt_three.det()) == 0

    insertion_sign_sums = {
        str(n): str(sum(sp.Integer(-1) ** j for j in range(n)))
        for n in range(2, 13)
    }
    assert all(
        value == ("0" if int(n) % 2 == 0 else "1")
        for n, value in insertion_sign_sums.items()
    )

    # Exact rationalization of a numerical scout that falsified the tempting
    # stronger comparison E D-||Alt x||_A^2 >= ||Ax||_2^2 at n=3.
    denominator = 10**8
    near_rank_one = sp.Matrix(
        [
            [1, sp.Rational(-99808621, denominator), sp.Rational(99557499, denominator)],
            [sp.Rational(-99808621, denominator), 1, sp.Rational(-99431702, denominator)],
            [sp.Rational(99557499, denominator), sp.Rational(-99431702, denominator), 1],
        ]
    )
    near_minors = [sp.factor(near_rank_one[:k, :k].det()) for k in range(1, 4)]
    assert all(value > 0 for value in near_minors)
    near_matrices = {
        p: epoch_matrix(near_rank_one, p) for p in itertools.permutations(range(3))
    }
    near_endpoint_energy = sum(
        (T.T * near_rank_one * T for T in near_matrices.values()), sp.zeros(3)
    ) / 6
    near_alt = sum(
        (permutation_sign(p) * T for p, T in near_matrices.items()), sp.zeros(3)
    ) / 6
    strong_difference = sp.simplify(
        near_rank_one
        - near_endpoint_energy
        - near_alt.T * near_rank_one * near_alt
        - near_rank_one**2
    )
    strong_witness = sp.Matrix([1, -1, 1])
    strong_witness_value = sp.factor(
        (strong_witness.T * strong_difference * strong_witness)[0]
    )
    assert strong_witness_value < 0

    near_mean = sum(near_matrices.values(), sp.zeros(3)) / 6
    near_pair_sum = sp.zeros(3)
    near_pair_cases = 0
    for p, T in near_matrices.items():
        for i, j in itertools.combinations(range(3), 2):
            pp = list(p)
            pp[i], pp[j] = pp[j], pp[i]
            difference = T - near_matrices[tuple(pp)]
            near_pair_sum += difference.T * near_rank_one * difference
            near_pair_cases += 1
    near_proxy = sp.simplify(
        near_mean.T * near_rank_one * near_mean
        + sp.Rational(1, 2) * near_pair_sum / near_pair_cases
    )
    rational_mu_upper = sp.Rational(1, 550)
    shifted_determinant = sp.factor(
        (near_rank_one - rational_mu_upper * sp.eye(3)).det()
    )
    # Negative shifted determinant plus trace(A)=3>3/550 excludes three
    # eigenvalues below 1/550, hence mu<1/550.
    assert shifted_determinant < 0
    near_c_one_gap = sp.simplify(
        (1 - rational_mu_upper) * near_rank_one - near_proxy
    )
    near_c_one_minors = all_principal_minors(near_c_one_gap)
    assert all(value >= 0 for value in near_c_one_minors)

    rational_three = sp.Matrix(
        [
            [1, sp.Rational(1, 3), sp.Rational(-1, 5)],
            [sp.Rational(1, 3), 1, sp.Rational(1, 4)],
            [sp.Rational(-1, 5), sp.Rational(1, 4), 1],
        ]
    )
    alt_three = sum(
        (
            permutation_sign(p) * epoch_matrix(rational_three, p)
            for p in itertools.permutations(range(3))
        ),
        sp.zeros(3),
    ) / sp.factorial(3)
    assert alt_three != sp.zeros(3)

    blocks = sp.diag(
        sp.Matrix([[1, sp.Rational(9, 10)], [sp.Rational(9, 10), 1]]),
        sp.Matrix([[1, sp.Rational(-4, 5)], [sp.Rational(-4, 5), 1]]),
    )
    alt_blocks = sum(
        (
            permutation_sign(p) * epoch_matrix(blocks, p)
            for p in itertools.permutations(range(4))
        ),
        sp.zeros(4),
    ) / sp.factorial(4)
    assert alt_blocks == sp.zeros(4)
    return {
        "symbolic_unit_diagonal_n3_alternant": [
            [str(sp.factor(symbolic_alt_three[i, j])) for j in range(3)]
            for i in range(3)
        ],
        "symbolic_n3_alternant_determinant": "0",
        "omitted_one_label_insertion_sign_sums_n2_through_n12": insertion_sign_sums,
        "weak_coupling_order": "O(epsilon^(n-2)) for odd n and O(epsilon^(n-1)) for even n when A=I+epsilon H with diag(H)=0",
        "stronger_n3_comparison_counterexample": {
            "matrix": [
                [str(near_rank_one[i, j]) for j in range(3)] for i in range(3)
            ],
            "leading_principal_minors": [str(value) for value in near_minors],
            "witness": [1, -1, 1],
            "witness_quadratic_value": str(strong_witness_value),
            "witness_quadratic_value_decimal": f"{float(strong_witness_value):.17g}",
            "actual_c_equals_one_proxy_control": {
                "rational_upper_bound_on_mu": str(rational_mu_upper),
                "determinant_of_A_minus_upper_bound_I": str(shifted_determinant),
                "reason_mu_is_below_upper_bound": "The determinant is negative, while trace(A)=3 excludes all three eigenvalues being below 1/550.",
                "all_principal_minors_of_(1-1/550)A_minus_B_nonnegative": True,
                "gap_determinant": str(sp.factor(near_c_one_gap.det())),
                "conclusion": "B<=(1-1/550)A<=(1-mu)A exactly on this matrix.",
            },
            "conclusion": "Exact refutation only of E D-||Alt x||_A^2 >= ||Ax||_2^2; it does not refute EP or C050.",
        },
        "rational_noncommuting_n3_alternant": [
            [str(sp.factor(alt_three[i, j])) for j in range(3)] for i in range(3)
        ],
        "rational_noncommuting_n3_alternant_frobenius_squared": str(
            sp.factor(sp.trace(alt_three.T * alt_three))
        ),
        "unequal_signed_two_block_n4_alternant_is_zero": True,
        "interpretation": "The sign mode is present generically at n=3 but cancels on the independent-block control; no general gap conclusion.",
    }


def symbolic_positive_equicorrelation_n3_proxy() -> dict:
    q = sp.symbols("q", nonnegative=True, real=True)
    n = 3
    A = (1 - q) * sp.eye(n) + q * sp.ones(n)
    permutations = list(itertools.permutations(range(n)))
    matrices = {p: epoch_matrix(A, p) for p in permutations}
    mean_T = sum(matrices.values(), sp.zeros(n)) / len(permutations)
    pair_sum = sp.zeros(n)
    pair_count = 0
    for p, T in matrices.items():
        for i, j in itertools.combinations(range(n), 2):
            pp = list(p)
            pp[i], pp[j] = pp[j], pp[i]
            diff = T - matrices[tuple(pp)]
            pair_sum += diff.T * A * diff
            pair_count += 1
    proxy = sp.simplify(mean_T.T * A * mean_T + sp.Rational(1, 2) * pair_sum / pair_count)
    one = sp.ones(n, 1)
    transverse = sp.Matrix([1, -1, 0])
    r_one = sp.factor((one.T * proxy * one)[0] / (one.T * A * one)[0])
    r_transverse = sp.factor(
        (transverse.T * proxy * transverse)[0] / (transverse.T * A * transverse)[0]
    )
    q_minus_one = sp.factor(q - r_one)
    q_minus_transverse = sp.factor(q - r_transverse)
    a = sp.symbols("a", nonnegative=True, real=True)
    negative_r_one = sp.factor(r_one.subs(q, -a))
    negative_r_transverse = sp.factor(r_transverse.subs(q, -a))
    negative_gap_one = sp.factor(2 * a - negative_r_one)
    negative_gap_transverse = sp.factor(2 * a - negative_r_transverse)
    return {
        "range": "0<=q<1, mu=1-q",
        "symmetric_proxy_quotient": str(r_one),
        "transverse_proxy_quotient": str(r_transverse),
        "q_minus_symmetric_quotient": str(q_minus_one),
        "q_minus_transverse_quotient": str(q_minus_transverse),
        "negative_range": "q=-a, 0<=a<1/2, mu=1-2a",
        "two_a_minus_negative_symmetric_quotient": str(negative_gap_one),
        "two_a_minus_negative_transverse_quotient": str(negative_gap_transverse),
        "conclusion": "The displayed differences are nonnegative on their ranges, so B_A<=(1-mu)A for all n=3 equicorrelations",
        "evidence_level": "E3 symbolic proof draft; no independent audit",
    }


def numerical_scan(seed: int, samples: int) -> dict:
    rng = np.random.default_rng(seed)
    records = []
    proxy_records = []
    for n in range(3, 8):
        best = math.inf
        best_mu = None
        best_proxy_gap_over_mu = math.inf
        best_proxy_mu = None
        for _ in range(samples):
            G = rng.normal(size=(n, n))
            C = G @ G.T
            d = np.sqrt(np.diag(C))
            A = C / np.outer(d, d)
            # Mix toward I to avoid accidental numerical singularity.
            eta = float(rng.uniform(1e-4, 0.2))
            A = (1 - eta) * A + eta * np.eye(n)
            K = np.zeros((n, n))
            for p in itertools.permutations(range(n)):
                P = np.eye(n)[list(p), :]
                M = np.tril(P @ A @ P.T)
                B = np.linalg.inv(M)
                K += P.T @ B.T @ B @ P
            K /= math.factorial(n)
            val = float(np.linalg.eigvalsh(K)[0])
            if val < best:
                best = val
                best_mu = float(np.linalg.eigvalsh(A)[0])
            # Mean-plus-transposition-Dirichlet proxy.  This is an exhaustive
            # permutation average but still float64, so it remains E1.
            permutations = list(itertools.permutations(range(n)))
            Ts = {}
            for p in permutations:
                T = np.eye(n)
                for i in p:
                    U = np.eye(n)
                    U[i, :] -= A[i, :]
                    T = U @ T
                Ts[p] = T
            mean_T = sum(Ts.values()) / len(permutations)
            pair_sum = np.zeros((n, n))
            pair_count = 0
            for p, T in Ts.items():
                for i in range(n):
                    for j in range(i + 1, n):
                        pp = list(p)
                        pp[i], pp[j] = pp[j], pp[i]
                        diff = T - Ts[tuple(pp)]
                        pair_sum += diff.T @ A @ diff
                        pair_count += 1
            proxy = mean_T.T @ A @ mean_T + (n - 1) * pair_sum / (4 * pair_count)
            eigvals, eigvecs = np.linalg.eigh(A)
            invsqrt = eigvecs @ np.diag(1 / np.sqrt(eigvals)) @ eigvecs.T
            proxy_max = float(np.linalg.eigvalsh(invsqrt @ proxy @ invsqrt)[-1])
            proxy_gap_over_mu = (1 - proxy_max) / float(eigvals[0])
            if proxy_gap_over_mu < best_proxy_gap_over_mu:
                best_proxy_gap_over_mu = proxy_gap_over_mu
                best_proxy_mu = float(eigvals[0])
        records.append({"n": n, "min_lambda_K": best, "mu_at_min": best_mu})
        proxy_records.append(
            {
                "n": n,
                "minimum_proxy_gap_over_mu": best_proxy_gap_over_mu,
                "mu_at_minimum": best_proxy_mu,
            }
        )
    return {
        "label": "numerical_observation_only",
        "seed": seed,
        "samples_per_dimension": samples,
        "dimensions": [3, 4, 5, 6, 7],
        "float_dtype": "float64",
        "records": records,
        "compensated_proxy_records": proxy_records,
    }


def numerical_proxy_matrix(A: np.ndarray, permutations: list[tuple[int, ...]] | None = None) -> np.ndarray:
    n = A.shape[0]
    permutations = permutations or list(itertools.permutations(range(n)))
    Ts = {}
    for p in permutations:
        T = np.eye(n)
        for i in p:
            U = np.eye(n)
            U[i, :] -= A[i, :]
            T = U @ T
        Ts[p] = T
    mean_T = sum(Ts.values()) / len(permutations)
    pair_sum = np.zeros_like(A)
    pair_count = 0
    for p, T in Ts.items():
        for i, j in itertools.combinations(range(n), 2):
            pp = list(p)
            pp[i], pp[j] = pp[j], pp[i]
            diff = T - Ts[tuple(pp)]
            pair_sum += diff.T @ A @ diff
            pair_count += 1
    return mean_T.T @ A @ mean_T + (n - 1) * pair_sum / (4 * pair_count)


def numerical_proxy_gap(A: np.ndarray, proxy: np.ndarray) -> float:
    eigvals, eigvecs = np.linalg.eigh(A)
    invsqrt = eigvecs @ np.diag(1 / np.sqrt(eigvals)) @ eigvecs.T
    proxy_max = float(np.linalg.eigvalsh(invsqrt @ proxy @ invsqrt)[-1])
    return (1 - proxy_max) / float(eigvals[0])


def numerical_two_epoch_proxy_matrix(
    A: np.ndarray, permutations: list[tuple[int, ...]]
) -> np.ndarray:
    n = A.shape[0]
    one_epoch = {}
    for p in permutations:
        T = np.eye(n)
        for i in p:
            U = np.eye(n)
            U[i, :] -= A[i, :]
            T = U @ T
        one_epoch[p] = T
    endpoints = {
        (p, q): one_epoch[q] @ one_epoch[p]
        for p, q in itertools.product(permutations, repeat=2)
    }
    mean_endpoint = sum(endpoints.values()) / len(endpoints)
    dirichlet_sum = np.zeros_like(A)
    for slot in range(2):
        slot_sum = np.zeros_like(A)
        slot_cases = 0
        for seq, T in endpoints.items():
            for i, j in itertools.combinations(range(n), 2):
                changed = [list(seq[0]), list(seq[1])]
                changed[slot][i], changed[slot][j] = changed[slot][j], changed[slot][i]
                diff = T - endpoints[(tuple(changed[0]), tuple(changed[1]))]
                slot_sum += diff.T @ A @ diff
                slot_cases += 1
        dirichlet_sum += slot_sum / slot_cases
    return mean_endpoint.T @ A @ mean_endpoint + (n - 1) * dirichlet_sum / 4


def extended_numerical_scout(seed: int) -> dict:
    """Small reproducible mechanism scouts; all outputs remain E1."""
    n = 12

    def epoch_float(A: np.ndarray, p: np.ndarray) -> np.ndarray:
        T = np.eye(A.shape[0])
        for i in p:
            T[i, :] -= A[i, :] @ T
        return T

    def mc_proxy_gap(A: np.ndarray, count: int, local_seed: int) -> float:
        local_rng = np.random.default_rng(local_seed)
        mean_T = np.zeros_like(A)
        pair_sum = np.zeros_like(A)
        for _ in range(count):
            p = local_rng.permutation(A.shape[0])
            T = epoch_float(A, p)
            mean_T += T
            i, j = local_rng.choice(A.shape[0], 2, replace=False)
            pp = p.copy()
            pp[i], pp[j] = pp[j], pp[i]
            diff = T - epoch_float(A, pp)
            pair_sum += diff.T @ A @ diff
        mean_T /= count
        pair_sum /= count
        proxy = mean_T.T @ A @ mean_T + (A.shape[0] - 1) * pair_sum / 4
        return numerical_proxy_gap(A, proxy)

    def mc_two_epoch_proxy_gap(A: np.ndarray, count: int, local_seed: int) -> float:
        local_rng = np.random.default_rng(local_seed)
        mean_endpoint = np.zeros_like(A)
        dirichlet = [np.zeros_like(A), np.zeros_like(A)]
        for _ in range(count):
            p = local_rng.permutation(A.shape[0])
            q = local_rng.permutation(A.shape[0])
            Tp = epoch_float(A, p)
            Tq = epoch_float(A, q)
            endpoint = Tq @ Tp
            mean_endpoint += endpoint
            for slot in range(2):
                changed = (p.copy(), q.copy())
                i, j = local_rng.choice(A.shape[0], 2, replace=False)
                changed[slot][i], changed[slot][j] = changed[slot][j], changed[slot][i]
                changed_endpoint = epoch_float(A, changed[1]) @ epoch_float(A, changed[0])
                diff = endpoint - changed_endpoint
                dirichlet[slot] += diff.T @ A @ diff
        mean_endpoint /= count
        proxy = mean_endpoint.T @ A @ mean_endpoint
        proxy += (A.shape[0] - 1) * sum(term / count for term in dirichlet) / 4
        return numerical_proxy_gap(A, proxy)

    families = {}
    path = np.eye(n)
    cycle = np.eye(n)
    for i in range(n - 1):
        path[i, i + 1] = path[i + 1, i] = 0.49
        cycle[i, i + 1] = cycle[i + 1, i] = 0.49
    cycle[0, -1] = cycle[-1, 0] = 0.49
    frustrated_cycle = cycle.copy()
    frustrated_cycle[0, -1] = frustrated_cycle[-1, 0] = -0.49
    ar1 = np.fromfunction(lambda i, j: 0.99 ** np.abs(i - j), (n, n))
    matching = np.eye(n)
    for b in range(0, n, 2):
        matching[b, b + 1] = matching[b + 1, b] = 0.8 * (-1 if (b // 2) % 3 == 1 else 1)
    for b in range(1, n - 2, 2):
        matching[b, b + 1] = matching[b + 1, b] = 0.04 * (-1 if b % 4 == 1 else 1)
    family_list = (
        ("path", path),
        ("cycle", cycle),
        ("frustrated_signed_cycle", frustrated_cycle),
        ("ar1", ar1),
        ("weak_matching_chain", matching),
    )
    for index, (label, A) in enumerate(family_list):
        families[label] = {
            "dimension": n,
            "mu": float(np.linalg.eigvalsh(A)[0]),
            "mc_samples": 2000,
            "family_seed": seed + 9001 + index,
            "proxy_gap_over_mu": mc_proxy_gap(A, 2000, seed + 9001 + index),
        }
        families[label]["two_epoch_family_seed"] = seed + 9101 + index
        families[label]["two_epoch_proxy_gap_over_mu"] = mc_two_epoch_proxy_gap(
            A, 2000, seed + 9101 + index
        )

    arrow = np.eye(17)
    arrow[0, 1:] = 0.99 / 4
    arrow[1:, 0] = 0.99 / 4
    families["near_singular_arrow"] = {
        "dimension": 17,
        "mu": float(np.linalg.eigvalsh(arrow)[0]),
        "mc_samples": 2000,
        "family_seed": seed + 9010,
        "proxy_gap_over_mu": mc_proxy_gap(arrow, 2000, seed + 9010),
        "two_epoch_family_seed": seed + 9110,
        "two_epoch_proxy_gap_over_mu": mc_two_epoch_proxy_gap(arrow, 2000, seed + 9110),
    }

    # Deterministic symmetry-breaking Hadamard family grid at n=4.
    grid_values = [-0.6, -0.3, 0.0, 0.3, 0.6]
    best_grid = math.inf
    best_two_epoch_grid = math.inf
    grid_spd_cases = 0
    perms4 = list(itertools.permutations(range(4)))
    for a, b, c in itertools.product(grid_values, repeat=3):
        A = np.array(
            [[1, a, b, c], [a, 1, c, b], [b, c, 1, a], [c, b, a, 1]],
            dtype=float,
        )
        if float(np.linalg.eigvalsh(A)[0]) <= 1e-12:
            continue
        grid_spd_cases += 1
        best_grid = min(best_grid, numerical_proxy_gap(A, numerical_proxy_matrix(A, perms4)))
        best_two_epoch_grid = min(
            best_two_epoch_grid,
            numerical_proxy_gap(A, numerical_two_epoch_proxy_matrix(A, perms4)),
        )

    return {
        "label": "numerical_observation_only",
        "seed_base": seed + 9000,
        "dtype": "float64",
        "tolerance": "No theorem/pass tolerance; SPD grid filter 1e-12 only",
        "monte_carlo_families": families,
        "hadamard_grid": {
            "grid_values": grid_values,
            "spd_cases": grid_spd_cases,
            "minimum_proxy_gap_over_mu": best_grid,
            "minimum_two_epoch_proxy_gap_over_mu": best_two_epoch_grid,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--extended-scan", action="store_true")
    parser.add_argument("--seed", type=int, default=14320260825)
    parser.add_argument("--samples", type=int, default=20)
    args = parser.parse_args()
    result = {
        "schema_version": "1.0",
        "arithmetic": "sympy exact rational except optional explicitly labelled float64 scan",
        "locked_core_counterexample": exact_counterexample(),
        "adjacent_swap_identity": adjacent_swap_identity_check(),
        "random_transposition_dirichlet": random_transposition_dirichlet_check(),
        "equicorrelation_pair_variance": equicorrelation_pair_variance_check(),
        "equicorrelation_permutation_martingale": equicorrelation_permutation_martingale_check(),
        "symmetry_breaking_arrow": arrow_family_check(),
        "block_signed_family": block_signed_check(),
        "exact_pair_proxy_slices": exact_pair_proxy_slices(),
        "exact_two_epoch_proxy_control": exact_two_epoch_proxy_control(),
        "exact_two_epoch_interacting_control": exact_two_epoch_interacting_control(),
        "multiepoch_metric_map_recursion_control": multiepoch_metric_map_recursion_control(),
        "symbolic_signed_block_proxy": symbolic_signed_block_proxy(),
        "alternating_mode_checks": alternating_mode_checks(),
        "symbolic_positive_equicorrelation_n3_proxy": symbolic_positive_equicorrelation_n3_proxy(),
    }
    if args.scan:
        result["numerical_scan"] = numerical_scan(args.seed, args.samples)
    if args.extended_scan:
        result["extended_numerical_scout"] = extended_numerical_scout(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
