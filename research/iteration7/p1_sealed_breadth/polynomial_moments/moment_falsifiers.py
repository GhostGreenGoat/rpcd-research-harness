#!/usr/bin/env python3
"""Deterministic exact and numerical attacks on RC-T143-NCPM-001.

Exact calculations use SymPy rationals.  The random scan is explicitly a
float64 scout and is not used to certify a general statement.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math

import numpy as np
import sympy as sp


def exact_epoch_adjoint(a: sp.Matrix, x: sp.Matrix) -> sp.Matrix:
    """Return E_pi[T_pi.T*x*T_pi] by an exact subset recursion."""
    n = a.rows
    eye = sp.eye(n)
    updates = [eye - eye[:, i] * a[i, :] for i in range(n)]
    states: dict[int, sp.Matrix] = {0: x}
    for mask in range(1, 1 << n):
        total = sp.zeros(n)
        for i in range(n):
            if mask & (1 << i):
                u = updates[i]
                total += u.T * states[mask ^ (1 << i)] * u
        states[mask] = sp.simplify(total / mask.bit_count())
    return states[(1 << n) - 1]


def leading_principal_minors(x: sp.Matrix) -> list[sp.Expr]:
    return [sp.factor(x[:j, :j].det()) for j in range(1, x.rows + 1)]


def frac(x: sp.Expr) -> str:
    return str(sp.factor(x))


def bernstein_coefficients(poly: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
    """Power-to-Bernstein coefficients on [0,1], exactly."""
    expanded = sp.Poly(sp.expand(poly), variable)
    degree = expanded.degree()
    power = [expanded.coeff_monomial(variable ** j) for j in range(degree + 1)]
    return [
        sp.factor(
            sum(
                power[j] * sp.binomial(k, j) / sp.binomial(degree, j)
                for j in range(k + 1)
            )
        )
        for k in range(degree + 1)
    ]


def equicorrelation_records() -> dict[str, object]:
    records = []
    for n in range(2, 13):
        delta = sp.Rational(1, n * n)
        rho = 1 - delta
        lower = sp.eye(n)
        for i in range(n):
            for j in range(i):
                lower[i, j] = rho
        rinv = sp.zeros(n)
        for i in range(n):
            rinv[i, i] = 1
            for j in range(i):
                rinv[i, j] = -rho * delta ** (i - j - 1)
        assert lower * rinv == sp.eye(n)
        p_contrast = sp.eye(n) - sp.ones(n) / n
        contrast_loss = sp.factor(
            delta
            * sp.trace(p_contrast * rinv.T * rinv * p_contrast)
            / (n - 1)
        )
        lam_mean = n - (n - 1) * delta
        mean_loss = sp.factor(
            lam_mean
            * sum(delta ** (2 * j) for j in range(n))
            / n
        )
        records.append(
            {
                "n": n,
                "delta": frac(delta),
                "contrast_loss_over_delta": frac(contrast_loss / delta),
                "mean_loss": frac(mean_loss),
                "card_margin_contrast": frac(contrast_loss - delta / 16),
                "card_margin_mean": frac(mean_loss - delta / 16),
            }
        )
    return {
        "family": "A=delta*I+(1-delta)*11^T, delta=n^-2",
        "mu": "delta",
        "analytic_bounds": {
            "contrast": "d_contrast >= (3/2)*delta: use exact n=2,3 records; for n>=4 retain diagonal and first-subdiagonal terms, giving d_contrast/delta >= (n-1)/n+(1-delta)^2 >3/2",
            "mean": "d_mean >= 1-delta >= 3/4 >= (3/2)*delta",
            "consequence": "D >= (3/2)*mu*I and the proposed m=ceil(1/mu) trace-moment certificate holds on this family",
        },
        "finite_exact_records": records,
    }


def negative_equicorrelation_records() -> dict[str, object]:
    records = []
    for n in range(2, 13):
        mu = sp.Rational(1, n * n)
        alpha = -(1 - mu) / (n - 1)
        contrast_eigenvalue = 1 - alpha
        lower = sp.eye(n)
        for i in range(n):
            for j in range(i):
                lower[i, j] = alpha
        rinv = sp.zeros(n)
        for i in range(n):
            rinv[i, i] = 1
            for j in range(i):
                rinv[i, j] = -alpha * contrast_eigenvalue ** (i - j - 1)
        assert lower * rinv == sp.eye(n)
        p_contrast = sp.eye(n) - sp.ones(n) / n
        contrast_loss = sp.factor(
            contrast_eigenvalue
            * sp.trace(p_contrast * rinv.T * rinv * p_contrast)
            / (n - 1)
        )
        mean_loss = sp.factor(
            mu
            * sum(contrast_eigenvalue ** (2 * j) for j in range(n))
            / n
        )
        records.append(
            {
                "n": n,
                "mu": frac(mu),
                "contrast_loss_over_mu": frac(contrast_loss / mu),
                "mean_loss_over_mu": frac(mean_loss / mu),
                "card_margin_contrast": frac(contrast_loss - mu / 16),
                "card_margin_mean": frac(mean_loss - mu / 16),
            }
        )
    return {
        "family": "A has off-diagonal -(1-mu)/(n-1), mu=n^-2",
        "analytic_bounds": {
            "mean": "d_mean/mu=(1/n)sum_j(1+(1-mu)/(n-1))^(2j) >=2-mu >=7/4",
            "contrast": "the first row alone gives d_contrast >=(1+(1-mu)/(n-1))/n >=1/n >=2mu",
            "consequence": "D >= (7/4)*mu*I and the proposed trace-moment certificate holds",
        },
        "finite_exact_records": records,
    }


def anisotropic_exact() -> dict[str, object]:
    eps = sp.symbols("eps")
    b = sp.Matrix(
        [
            [1, 0],
            [0, 1],
            [sp.Rational(3, 5), sp.Rational(4, 5)],
            [sp.Rational(4, 5), sp.Rational(3, 5)],
        ]
    )
    c = b * b.T
    a = eps * sp.eye(4) + (1 - eps) * c
    loss = sp.simplify(a - exact_epoch_adjoint(a, a))
    selected_residual = sp.simplify(loss - eps * a)
    bernstein_records = []
    for minor in leading_principal_minors(selected_residual):
        numerator, denominator = sp.fraction(sp.together(minor))
        coefficients = bernstein_coefficients(numerator, eps)
        positive = [x for x in coefficients if x > 0]
        bernstein_records.append(
            {
                "degree": len(coefficients) - 1,
                "denominator_positive": bool(denominator > 0),
                "negative_coefficients": sum(bool(x < 0) for x in coefficients),
                "zero_coefficients": sum(bool(x == 0) for x in coefficients),
                "positive_coefficients": len(positive),
                "minimum_positive_coefficient": frac(min(positive)),
                "value_at_eps_1": frac(minor.subs(eps, 1)),
            }
        )

    # Kernel/range singular perturbation.  K spans ker(C), and B spans ran(C).
    ker = sp.Matrix([[-3, -4], [-4, -3], [5, 0], [0, 5]])
    lkk = sp.simplify(ker.T * loss * ker)
    lkr = sp.simplify(ker.T * loss * b)
    lrr = sp.simplify(b.T * loss * b)
    coeff = lambda x, j: x.applyfunc(lambda z: sp.expand(z).coeff(eps, j))
    lrr0 = coeff(lrr, 0)
    lkr1 = coeff(lkr, 1)
    lkk2 = coeff(lkk, 2)
    effective = sp.simplify(lkk2 - lkr1 * lrr0.inv() * lkr1.T)
    gram = ker.T * ker
    z = sp.symbols("z")
    pencil = sp.factor((effective - z * gram).det())
    asym_card = effective - sp.Rational(1, 16) * gram

    # Exact near-singular instance.
    eps0 = sp.Rational(1, 1000)
    a0 = a.subs(eps, eps0)
    loss0 = loss.subs(eps, eps0)
    card_residual = sp.simplify(loss0 - eps0 * a0 / 16)
    moment_residual = sp.simplify(loss0 - sp.Rational(3, 2) * eps0 * a0)
    eye = sp.eye(4)
    updates0 = [eye - eye[:, i] * a0[i, :] for i in range(4)]
    commutator = sp.simplify(updates0[0] * updates0[2] - updates0[2] * updates0[0])

    # H_2 != H_1^2 in whitened coordinates.  Congruence by A^(1/2)
    # turns the difference into this entirely rational matrix.
    g1 = exact_epoch_adjoint(a0, a0)
    g2 = exact_epoch_adjoint(a0, g1)
    noncomm_delta = sp.simplify(g2 - g1 * a0.inv() * g1)

    return {
        "family": "A_eps=eps*I+(1-eps)*C",
        "C": [[frac(c[i, j]) for j in range(4)] for i in range(4)],
        "spectrum": ["eps", "eps", "(26-eps)/25", "(74-49*eps)/25"],
        "kernel_basis": [[int(ker[i, j]) for j in range(2)] for i in range(4)],
        "noncommuting_witness_at_eps_1_over_1000": {
            "commutator_entry_00": frac(commutator[0, 0]),
            "nonzero": commutator != sp.zeros(4),
        },
        "exact_instance_eps": "1/1000",
        "card_residual_leading_principal_minors": [
            frac(x) for x in leading_principal_minors(card_residual)
        ],
        "card_residual_positive_definite": all(
            bool(x > 0) for x in leading_principal_minors(card_residual)
        ),
        "selected_one_mu_all_eps_bernstein_certificate": bernstein_records,
        "selected_one_mu_all_eps_conclusion": "Every leading-minor numerator has nonnegative Bernstein coefficients and is positive in 0<eps<1; at eps=1 the residual is zero. Hence L-eps*A is positive semidefinite for every 0<eps<=1.",
        "three_halves_residual_leading_principal_minors": [
            frac(x) for x in leading_principal_minors(moment_residual)
        ],
        "three_halves_residual_positive_definite": all(
            bool(x > 0) for x in leading_principal_minors(moment_residual)
        ),
        "singular_limit": {
            "effective_loss": [
                [frac(effective[i, j]) for j in range(2)] for i in range(2)
            ],
            "kernel_gram": [[frac(gram[i, j]) for j in range(2)] for i in range(2)],
            "generalized_characteristic_polynomial": frac(pencil),
            "loss_over_mu_roots_decimal_15": [
                str(x.evalf(15)) for x in sp.solve(pencil, z)
            ],
            "minus_one_sixteenth_leading_principal_minors": [
                frac(x) for x in leading_principal_minors(asym_card)
            ],
        },
        "noncommuting_epoch_obstruction": {
            "claim_rejected": "H_2=H_1^2 (and either universal Loewner ordering)",
            "rational_congruence_entry_00": frac(noncomm_delta[0, 0]),
            "weighted_trace": frac(sp.trace(a0.inv() * noncomm_delta)),
            "determinant": frac(noncomm_delta.det()),
            "conclusion": "nonzero, trace-zero after whitening, and indefinite",
        },
    }


def signed_block_exact() -> dict[str, object]:
    """A block and sign-frustrated exact control beyond positive correlation."""
    delta = sp.Rational(1, 16)
    positive = delta * sp.eye(2) + (1 - delta) * sp.ones(2)
    eta = sp.Rational(1, 25)
    off = (1 - eta) / 2
    negative = sp.eye(3) - off * (sp.ones(3) - sp.eye(3))
    a = sp.diag(positive, negative)
    mu = eta
    loss = sp.simplify(a - exact_epoch_adjoint(a, a))
    residual = sp.simplify(loss - mu * a / 16)
    moment_residual = sp.simplify(loss - sp.Rational(3, 2) * mu * a)
    eye = sp.eye(5)
    updates = [eye - eye[:, i] * a[i, :] for i in range(5)]
    signed_commutator = sp.simplify(updates[2] * updates[3] - updates[3] * updates[2])
    return {
        "matrix": [[frac(a[i, j]) for j in range(5)] for i in range(5)],
        "description": "2x2 positive equicorrelation block plus a sign-frustrated 3x3 negative equicorrelation block",
        "spectrum": ["1/25", "1/16", "37/25", "37/25", "31/16"],
        "mu": "1/25",
        "signed_block_commutator_entry_22": frac(signed_commutator[2, 2]),
        "card_residual_leading_principal_minors": [
            frac(x) for x in leading_principal_minors(residual)
        ],
        "card_residual_positive_definite": all(
            bool(x > 0) for x in leading_principal_minors(residual)
        ),
        "three_halves_residual_leading_principal_minors": [
            frac(x) for x in leading_principal_minors(moment_residual)
        ],
        "three_halves_residual_positive_definite": all(
            bool(x > 0) for x in leading_principal_minors(moment_residual)
        ),
    }


def high_mu_two_epoch_exact() -> dict[str, object]:
    """An exact case where MC is not obtained from a 3mu/2 one-step gap."""
    a = sp.Matrix([[1, sp.Rational(1, 10)], [sp.Rational(1, 10), 1]])
    mu = sp.Rational(9, 10)
    g1 = exact_epoch_adjoint(a, a)
    g2 = exact_epoch_adjoint(a, g1)
    loss = a - g1
    z = sp.symbols("z")
    loss_roots = sp.solve(sp.factor((loss - z * a).det()), z)
    tau_h2 = sp.factor(sp.trace(a.inv() * g2) / 2)
    return {
        "A": [["1", "1/10"], ["1/10", "1"]],
        "mu": frac(mu),
        "m=ceil(1/mu)": 2,
        "p=ceil(log(2))": 1,
        "one_epoch_loss_generalized_eigenvalues": [frac(x) for x in loss_roots],
        "three_halves_one_epoch_gap_fails": bool(min(loss_roots) < sp.Rational(3, 2) * mu),
        "tau_H_2": frac(tau_h2),
        "exact_elementary_bound": "tau(H_2)=101/4000000 <1/100<exp(-3/2)",
        "interpretation": "MC holds here although D>=(3/2)mu I does not",
    }


def seven_dimensional_second_prefix_certificate() -> dict[str, object]:
    """Exact scalar algebra used by the n=7, p=2 proof draft.

    The matrix part of the argument is analytic: the first prefix loses trace
    one, while the second loses at least 2*mu-mu**2 after maximizing tr(A**2)
    over eigenvalues bounded below by mu.  Here we certify the remaining
    one-variable logarithmic comparison.
    """
    m = sp.symbols("m", positive=True, integer=True)
    x = sp.Rational(3, 7) / m
    y = (1 + sp.Rational(2, 1) / m - 1 / m**2) / 7
    log_upper_plus_one = sp.factor(
        1 - y - y**2 / 2 - (2 * m - 1) * (x + x**2 / 2)
    )
    positivity_polynomial = m**4 + 8 * m**3 - 21 * m**2 - 4 * m + 1
    m2_bound = sp.Rational(3, 4) * sp.Rational(11, 14) ** 3
    e_series_upper = sp.Rational(87, 32)
    return {
        "dimension": 7,
        "moment_order": 2,
        "second_prefix_trace_loss_lower_bound": "2*mu-mu^2",
        "full_trace_loss_lower_bound": "tr(D)>=1+2*mu-mu^2",
        "ceiling_interval_scalar_bound": "((6-2/m+1/m^2)/7)*(1-3/(7m))^(2m-1)",
        "log_upper_plus_one": str(log_upper_plus_one),
        "positivity_polynomial": str(positivity_polynomial),
        "polynomial_at_m3": str(positivity_polynomial.subs(m, 3)),
        "polynomial_derivative_at_m3": str(sp.diff(positivity_polynomial, m).subs(m, 3)),
        "m2_scalar_bound": frac(m2_bound),
        "e_series_upper": frac(e_series_upper),
        "m2_strict_integer_gap": int(
            m2_bound.q * e_series_upper.q
            - m2_bound.p * e_series_upper.p
        ),
        "interpretation": "For m>=3 the displayed polynomial is positive and the log bound is below -1; m=2 follows from e<87/32<1/m2_bound; m=1 forces mu=1 and A=I.",
    }


def temporal_third_moment_shortcut_exact() -> dict[str, object]:
    """Reject tr(H_m**p)<=tr(H_(m*p)) at the first new moment order."""
    a = sp.Matrix([[1, sp.Rational(1, 10)], [sp.Rational(1, 10), 1]])
    g1 = exact_epoch_adjoint(a, a)
    g2 = exact_epoch_adjoint(a, g1)
    g3 = exact_epoch_adjoint(a, g2)
    trace_h1_cubed = sp.trace((a.inv() * g1) ** 3)
    trace_h3 = sp.trace(a.inv() * g3)
    return {
        "A": [["1", "1/10"], ["1/10", "1"]],
        "m": 1,
        "p": 3,
        "trace_H1_cubed": frac(trace_h1_cubed),
        "trace_H3": frac(trace_h3),
        "strict_difference": frac(sp.factor(trace_h1_cubed - trace_h3)),
        "rejected_step": "tr(H_m^p)<=tr(H_(m*p)) for p>=3",
    }


def eight_dimensional_third_moment_stress_exact() -> dict[str, object]:
    """Fully coupled rational n=8 instance at the first unresolved p=3."""
    rows = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (sp.Rational(3, 5), sp.Rational(4, 5), 0),
        (sp.Rational(4, 5), 0, sp.Rational(3, 5)),
        (0, sp.Rational(5, 13), sp.Rational(12, 13)),
        (-sp.Rational(3, 5), sp.Rational(4, 5), 0),
        (sp.Rational(12, 13), -sp.Rational(5, 13), 0),
    ]
    b = sp.Matrix(rows)
    c = b * b.T
    a = (sp.eye(8) + c) / 2
    g1 = exact_epoch_adjoint(a, a)
    g2 = exact_epoch_adjoint(a, g1)
    normalized_third_moment = sp.factor(sp.trace((a.inv() * g2) ** 3) / 8)
    a_quarter = sp.eye(8) / 4 + 3 * c / 4
    g_quarter = a_quarter
    for _ in range(4):
        g_quarter = exact_epoch_adjoint(a_quarter, g_quarter)
    quarter_third_moment = sp.factor(
        sp.trace((a_quarter.inv() * g_quarter) ** 3) / 8
    )
    return {
        "construction": "A=(I+BB^T)/2 with the listed rational unit rows",
        "B_rows": [[str(entry) for entry in row] for row in rows],
        "rank_BBT": c.rank(),
        "mu": "1/2 (the kernel of BB^T has dimension five)",
        "m": 2,
        "p": 3,
        "noncommuting_witness": "(U_1U_4-U_4U_1)_(1,1)=9/100",
        "normalized_third_moment": frac(normalized_third_moment),
        "decimal": float(normalized_third_moment),
        "strict_gap_to_one_eighth": frac(sp.Rational(1, 8) - normalized_third_moment),
        "target_comparison": "tau(H_2^3)<1/8<exp(-3/2), using e<3",
        "quarter_parameter_stress": {
            "mu": "1/4",
            "m": 4,
            "p": 3,
            "normalized_third_moment": frac(quarter_third_moment),
            "decimal": float(quarter_third_moment),
            "strict_gap_to_one_eighth": frac(
                sp.Rational(1, 8) - quarter_third_moment
            ),
        },
        "evidence_level": "E2 exact finite verification",
    }


def linearized_replica_obstruction_exact() -> dict[str, object]:
    """Reject a tempting linearized trace-dissipation lower bound exactly."""
    n = 10
    mu = sp.Rational(1, n * n)
    alpha = -(1 - mu) / (n - 1)
    contrast_eigenvalue = 1 - alpha
    lower_inv = sp.zeros(n)
    for i in range(n):
        lower_inv[i, i] = 1
        for j in range(i):
            lower_inv[i, j] = -alpha * contrast_eigenvalue ** (i - j - 1)
    p_contrast = sp.eye(n) - sp.ones(n) / n
    d_contrast = sp.factor(
        contrast_eigenvalue
        * sp.trace(p_contrast * lower_inv.T * lower_inv * p_contrast)
        / (n - 1)
    )
    d_mean = sp.factor(
        mu
        * sum(contrast_eigenvalue ** (2 * j) for j in range(n))
        / n
    )
    p = 3
    cross_ratio = sp.factor(
        (
            (1 - d_mean) ** (p - 1) * d_mean
            + (n - 1) * (1 - d_contrast) ** (p - 1) * d_contrast
        )
        / (mu * n)
    )
    trace_ratio = sp.factor(
        ((1 - d_mean) ** p + (n - 1) * (1 - d_contrast) ** p) / n
    )
    return {
        "family": "negative equicorrelation n=10, mu=1/100",
        "p": p,
        "d_mean": frac(d_mean),
        "d_contrast": frac(d_contrast),
        "cross_ratio": frac(cross_ratio),
        "cross_ratio_decimal_15": str(cross_ratio.evalf(15)),
        "three_halves_minus_cross_ratio": frac(sp.Rational(3, 2) - cross_ratio),
        "one_step_normalized_trace_power_ratio": frac(trace_ratio),
        "claim_rejected": "tr(H_1^(p-1)D) >=(3/2)mu tr(I^p)",
        "interpretation": "linearizing tr(X^p) at H_1 discards the nonlinear gain from directions almost annihilated in one epoch",
    }


def negative_replica_word_exact() -> dict[str, object]:
    """An exact RPCD p=3 replica word with negative trace."""
    a = sp.Matrix(
        [
            [1, sp.Rational(1, 5), sp.Rational(1, 5)],
            [sp.Rational(1, 5), 1, sp.Rational(1, 5)],
            [sp.Rational(1, 5), sp.Rational(1, 5), 1],
        ]
    )
    eye = sp.eye(3)
    updates = [eye - eye[:, i] * a[i, :] for i in range(3)]

    def epoch(order: tuple[int, ...]) -> sp.Matrix:
        result = eye
        for i in order:
            result = updates[i] * result
        return result

    # S_pi=Q_pi Q_pi^T is similar, in a trace word, to
    # Z_pi=T_pi A^(-1)T_pi^T A; this keeps the calculation rational.
    def rational_s(order: tuple[int, ...]) -> sp.Matrix:
        t = epoch(order)
        return sp.simplify(t * a.inv() * t.T * a)

    orders = ((1, 2, 0), (1, 0, 2), (2, 0, 1))
    value = sp.factor(
        sp.trace(rational_s(orders[0]) * rational_s(orders[1]) * rational_s(orders[2]))
    )
    return {
        "A": [[frac(a[i, j]) for j in range(3)] for i in range(3)],
        "spectrum": ["4/5", "4/5", "7/5"],
        "orders_zero_based": [list(x) for x in orders],
        "trace_S1_S2_S3": frac(value),
        "negative": bool(value < 0),
        "interpretation": "individual p=3 terms in the independent-replica expansion need not be nonnegative even inside RPCD",
    }


def epoch_adjoint_float(a: np.ndarray, x: np.ndarray) -> np.ndarray:
    n = a.shape[0]
    eye = np.eye(n)
    updates = [eye - np.outer(eye[:, i], a[i, :]) for i in range(n)]
    states: list[np.ndarray | None] = [None] * (1 << n)
    states[0] = x
    for mask in range(1, 1 << n):
        total = np.zeros_like(a)
        work = mask
        while work:
            bit = work & -work
            i = bit.bit_length() - 1
            u = updates[i]
            total += u.T @ states[mask ^ bit] @ u  # type: ignore[operator]
            work ^= bit
        states[mask] = total / mask.bit_count()
    return states[-1]  # type: ignore[return-value]


def generalized_loss_eigenvalues(a: np.ndarray) -> np.ndarray:
    loss = a - epoch_adjoint_float(a, a)
    eig, vec = np.linalg.eigh((a + a.T) / 2)
    ainvhalf = (vec / np.sqrt(eig)) @ vec.T
    whitened = ainvhalf @ ((loss + loss.T) / 2) @ ainvhalf
    return np.linalg.eigvalsh((whitened + whitened.T) / 2)


def eight_dimensional_ray_scout() -> dict[str, object]:
    """Float64 continuation of the exact n=8 rational ray."""
    rows = np.array(
        [
            (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (3 / 5, 4 / 5, 0), (4 / 5, 0, 3 / 5),
            (0, 5 / 13, 12 / 13), (-3 / 5, 4 / 5, 0),
            (12 / 13, -5 / 13, 0),
        ],
        dtype=float,
    )
    c = rows @ rows.T
    records = []
    eps_grid = np.concatenate((np.geomspace(0.02, 0.9, 25), [0.01, 0.005, 0.002]))
    for eps in eps_grid:
        a = eps * np.eye(8) + (1 - eps) * c
        m = math.ceil(1 / eps)
        g = a.copy()
        for _ in range(m):
            g = epoch_adjoint_float(a, g)
        eig, vec = np.linalg.eigh(a)
        ainvhalf = (vec / np.sqrt(eig)) @ vec.T
        h = ainvhalf @ g @ ainvhalf
        h = (h + h.T) / 2
        trace_root = float((np.trace(h @ h @ h) / 8) ** (1 / 3))
        records.append(
            {
                "eps": float(eps),
                "m": m,
                "normalized_third_moment_root": trace_root,
                "lambda_max_H_m": float(np.linalg.eigvalsh(h)[-1]),
            }
        )
    maximum = max(records, key=lambda item: item["normalized_third_moment_root"])
    return {
        "dtype": "float64",
        "grid": "25 log-spaced eps values in [0.02,0.9] plus 0.01,0.005,0.002",
        "threshold": math.exp(-0.5),
        "maximum": maximum,
        "hit": bool(maximum["normalized_third_moment_root"] > math.exp(-0.5)),
        "evidence_level": "E1",
    }


def seven_dimensional_prefix_regression() -> dict[str, object]:
    """Float64 orientation regression for tr(D)>=1+2*mu-mu**2."""
    seed = 70720260825
    trials = 1000
    rng = np.random.default_rng(seed)
    minimum = None
    for trial in range(trials):
        rows = rng.normal(size=(7, 7))
        gram = rows @ rows.T
        normalizer = 1 / np.sqrt(np.diag(gram))
        a = normalizer[:, None] * gram * normalizer[None, :]
        mu = float(np.linalg.eigvalsh(a)[0])
        loss = a - epoch_adjoint_float(a, a)
        trace_loss = float(np.trace(np.linalg.solve(a, loss)))
        margin = trace_loss - (1 + 2 * mu - mu * mu)
        item = {"trial": trial, "mu": mu, "trace_loss": trace_loss, "margin": margin}
        if minimum is None or margin < minimum["margin"]:
            minimum = item
    return {
        "seed": seed,
        "trials": trials,
        "dtype": "float64",
        "decision_tolerance": 1e-10,
        "minimum": minimum,
        "hit": bool(minimum and minimum["margin"] < -1e-10),
        "evidence_level": "E1 orientation regression only",
    }


def numerical_scout(seed: int, trials: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    records = []
    best = None
    for n in (7, 8, 9, 10):
        local_best = None
        for trial in range(trials):
            rank = int(rng.integers(2, n))
            rows = rng.normal(size=(n, rank))
            rows /= np.linalg.norm(rows, axis=1)[:, None]
            c = rows @ rows.T
            delta = 10.0 ** rng.uniform(-5.0, -1.0)
            a = delta * np.eye(n) + (1.0 - delta) * c
            vals = generalized_loss_eigenvalues(a)
            ratio = float(vals[0] / delta)
            item = {
                "n": n,
                "trial": trial,
                "rank_C": rank,
                "delta": delta,
                "min_loss_over_delta": ratio,
                "min_eigen_A_minus_delta": float(np.linalg.eigvalsh(a)[0] - delta),
            }
            if local_best is None or ratio < local_best["min_loss_over_delta"]:
                local_best = item
            if best is None or ratio < best["min_loss_over_delta"]:
                best = item
        records.append(local_best)
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "seed": seed,
        "trials_per_dimension": trials,
        "dimensions": [7, 8, 9, 10],
        "construction": "A=delta*I+(1-delta)*VV^T with unit Gaussian rows and rank(V)<n",
        "counterexample_threshold": 0.0625,
        "per_dimension_minima": records,
        "global_minimum": best,
        "hit": bool(best and best["min_loss_over_delta"] < 0.0625),
        "interpretation": "A null float64 scout is not a proof.",
    }


def hierarchical_scout(seed: int, trials: int) -> dict[str, object]:
    """Multi-scale full-rank Gram scout with a conservative conditioning cut."""
    rng = np.random.default_rng(seed)
    records = []
    global_best = None
    for n in (7, 8, 9, 10, 11):
        local_best = None
        accepted = 0
        for trial in range(trials):
            span = rng.uniform(0.5, 2.8)
            scales = 10.0 ** (-np.linspace(0.0, span, n))
            scales *= 10.0 ** rng.uniform(-0.15, 0.15, n)
            rows = rng.normal(size=(n, n)) * scales
            rows /= np.linalg.norm(rows, axis=1)[:, None]
            a = rows @ rows.T
            mu = float(np.linalg.eigvalsh(a)[0])
            if mu < 1.0e-6 or mu > 0.2:
                continue
            accepted += 1
            ratio = float(generalized_loss_eigenvalues(a)[0] / mu)
            item = {
                "n": n,
                "trial": trial,
                "mu": mu,
                "span_decades": span,
                "min_loss_over_mu": ratio,
            }
            if local_best is None or ratio < local_best["min_loss_over_mu"]:
                local_best = item
            if global_best is None or ratio < global_best["min_loss_over_mu"]:
                global_best = item
        records.append({"n": n, "accepted": accepted, "minimum": local_best})
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "seed": seed,
        "trials_per_dimension": trials,
        "conditioning_cut": "1e-6 <= lambda_min(A) <= 0.2",
        "construction": "unit-row Gram matrices with geometrically scaled random columns",
        "counterexample_threshold": 0.0625,
        "per_dimension": records,
        "global_minimum": global_best,
        "hit": bool(global_best and global_best["min_loss_over_mu"] < 0.0625),
        "interpretation": "A null scout is E1 only; rejected ill-conditioned cases are not evidence.",
    }


def boundary_short_coefficient_float(
    c: np.ndarray, permutations: list[tuple[int, ...]]
) -> float:
    """Singular-ray coefficient from the shorted boundary inverse moment."""
    n = c.shape[0]
    inverse_moment = np.zeros((n, n))
    for permutation in permutations:
        order = np.asarray(permutation)
        cp = c[np.ix_(order, order)]
        triangular = np.tril(cp)
        inverse = np.linalg.inv(triangular)
        term = inverse.T @ inverse
        inverse_moment[np.ix_(order, order)] += term
    inverse_moment /= len(permutations)
    eig, vec = np.linalg.eigh((c + c.T) / 2)
    kernel = vec[:, eig < 1.0e-8]
    range_basis = vec[:, eig >= 1.0e-8]
    kk = kernel.T @ inverse_moment @ kernel
    kr = kernel.T @ inverse_moment @ range_basis
    rr = range_basis.T @ inverse_moment @ range_basis
    shorted = kk - kr @ np.linalg.solve(rr, kr.T)
    return float(np.linalg.eigvalsh((shorted + shorted.T) / 2)[0])


def boundary_scout(seed: int, base_trials: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    records = []
    global_best = None
    plan = ((5, 5 * base_trials), (6, 3 * base_trials), (7, base_trials))
    for n, trials in plan:
        permutations = list(itertools.permutations(range(n)))
        local_best = None
        for trial in range(trials):
            rank = int(rng.integers(2, n))
            rows = rng.normal(size=(n, rank))
            rows /= np.linalg.norm(rows, axis=1)[:, None]
            c = rows @ rows.T
            coefficient = boundary_short_coefficient_float(c, permutations)
            item = {
                "n": n,
                "trial": trial,
                "rank_C": rank,
                "singular_ray_loss_over_mu": coefficient,
            }
            if local_best is None or coefficient < local_best["singular_ray_loss_over_mu"]:
                local_best = item
            if global_best is None or coefficient < global_best["singular_ray_loss_over_mu"]:
                global_best = item
        records.append({"n": n, "trials": trials, "minimum": local_best})
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "seed": seed,
        "construction": "rank-deficient unit-row Gram C; exact enumeration of every permutation for each float64 instance",
        "shorting_formula": "K_NN-K_NR*K_RR^(-1)*K_RN for K=E[M_C^(-T)M_C^(-1)]",
        "spectral_kernel_tolerance": 1.0e-8,
        "counterexample_threshold": 0.0625,
        "per_dimension": records,
        "global_minimum": global_best,
        "hit": bool(global_best and global_best["singular_ray_loss_over_mu"] < 0.0625),
        "interpretation": "Null boundary search is E1; the anisotropic rational instance is the separate exact control.",
    }


def epoch_adjoint_superoperator_float(
    a: np.ndarray, permutations: list[tuple[int, ...]]
) -> np.ndarray:
    n = a.shape[0]
    eye = np.eye(n)
    updates = [eye - np.outer(eye[:, i], a[i, :]) for i in range(n)]
    operator = np.zeros((n * n, n * n))
    for permutation in permutations:
        epoch = eye.copy()
        for i in permutation:
            epoch = updates[i] @ epoch
        operator += np.kron(epoch.T, epoch.T)
    return operator / len(permutations)


def block_operator_value_float(
    a: np.ndarray, permutations: list[tuple[int, ...]]
) -> tuple[float, int, float]:
    eig, vec = np.linalg.eigh((a + a.T) / 2)
    mu = float(eig[0])
    m = math.ceil(1.0 / mu)
    operator = epoch_adjoint_superoperator_float(a, permutations)
    g_vector = np.linalg.matrix_power(operator, m) @ a.reshape(-1, order="F")
    g = g_vector.reshape(a.shape, order="F")
    ainvhalf = (vec / np.sqrt(eig)) @ vec.T
    h = ainvhalf @ g @ ainvhalf
    h = (h + h.T) / 2
    return mu, m, float(np.linalg.eigvalsh(h)[-1])


def block_operator_scout(seed: int, base_trials: int) -> dict[str, object]:
    """Direct-sum falsifier: seek a base block with lambda_max(H_m)>e^-1/2."""
    rng = np.random.default_rng(seed)
    records = []
    global_best = None
    plan = ((3, 300 * base_trials), (4, 100 * base_trials),
            (5, 30 * base_trials), (6, 8 * base_trials))
    for n, trials in plan:
        permutations = list(itertools.permutations(range(n)))
        local_best = None
        accepted = 0
        for trial in range(trials):
            if n == 3:
                off = rng.uniform(-0.999, 0.999, size=3)
                a = np.array(
                    [[1.0, off[0], off[1]],
                     [off[0], 1.0, off[2]],
                     [off[1], off[2], 1.0]]
                )
            else:
                rows = rng.normal(size=(n, n))
                scales = 10.0 ** rng.uniform(-2.5, 1.0, size=n)
                gram = (rows * scales) @ rows.T
                normalizer = 1.0 / np.sqrt(np.diag(gram))
                a = normalizer[:, None] * gram * normalizer[None, :]
            mu = float(np.linalg.eigvalsh((a + a.T) / 2)[0])
            if mu < 0.002 or mu > 0.8:
                continue
            accepted += 1
            mu, m, value = block_operator_value_float(a, permutations)
            item = {
                "n": n,
                "trial": trial,
                "mu": mu,
                "m": m,
                "lambda_max_H_m": value,
            }
            if local_best is None or value > local_best["lambda_max_H_m"]:
                local_best = item
            if global_best is None or value > global_best["lambda_max_H_m"]:
                global_best = item
        records.append(
            {"n": n, "trials": trials, "accepted": accepted, "maximum": local_best}
        )
    threshold = math.exp(-0.5)
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "seed": seed,
        "conditioning_cut": "0.002<=mu<=0.8",
        "construction": "uniform off-diagonal correlations for n=3; normalized random Gram matrices for n=4,5,6",
        "all_permutations_enumerated_per_instance": True,
        "direct_sum_counterexample_threshold": threshold,
        "per_dimension": records,
        "global_maximum": global_best,
        "hit": bool(global_best and global_best["lambda_max_H_m"] > threshold),
        "interpretation": "A hit would replicate to refute MC; a null float64 search is E1 only.",
    }


def block_moment_case(name: str, a: np.ndarray, mu: float) -> dict[str, object]:
    n = a.shape[0]
    p = max(1, math.ceil(math.log(n)))
    eig, vec = np.linalg.eigh((a + a.T) / 2)
    ainvhalf = (vec / np.sqrt(eig)) @ vec.T
    g = a.copy()
    current = 0
    records = []
    for b in (0.5, 1.0, 2.0):
        m = math.ceil(b / mu)
        while current < m:
            g = epoch_adjoint_float(a, g)
            current += 1
        h = ainvhalf @ g @ ainvhalf
        h = (h + h.T) / 2
        tau_p = float(np.trace(np.linalg.matrix_power(h, p)) / n)
        r = tau_p ** (1.0 / p)
        records.append(
            {
                "b": b,
                "m=ceil(b/mu)": m,
                "p=ceil(log(n))": p,
                "lambda_max_H_m": float(np.linalg.eigvalsh(h)[-1]),
                "normalized_trace_moment_root": r,
                "worst_state_upper_bound_n^(1/p)*root": n ** (1.0 / p) * r,
            }
        )
    return {"name": name, "n": n, "mu_used": mu, "records": records}


def block_moment_scout() -> dict[str, object]:
    cases = []
    for n in (3, 4, 6, 8, 10):
        delta = 1.0 / (n * n)
        a = delta * np.eye(n) + (1.0 - delta) * np.ones((n, n))
        cases.append(block_moment_case(f"positive_equicorrelation_n_{n}", a, delta))
    for n in (3, 6, 10):
        mu = 1.0 / (n * n)
        off = (1.0 - mu) / (n - 1)
        a = np.eye(n) - off * (np.ones((n, n)) - np.eye(n))
        cases.append(block_moment_case(f"negative_equicorrelation_n_{n}", a, mu))
    b = np.array([[1.0, 0.0], [0.0, 1.0], [0.6, 0.8], [0.8, 0.6]])
    eps = 0.001
    cases.append(
        block_moment_case(
            "anisotropic_noncommuting_eps_1_over_1000",
            eps * np.eye(4) + (1.0 - eps) * (b @ b.T),
            eps,
        )
    )
    delta = 1.0 / 16.0
    positive = delta * np.eye(2) + (1.0 - delta) * np.ones((2, 2))
    eta = 1.0 / 25.0
    negative = np.eye(3) - (1.0 - eta) / 2.0 * (np.ones((3, 3)) - np.eye(3))
    signed = np.block(
        [[positive, np.zeros((2, 3))], [np.zeros((3, 2)), negative]]
    )
    cases.append(block_moment_case("signed_block", signed, eta))
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "moment": "tau(H_m^p)^(1/p), p=ceil(log n)",
        "cases": cases,
        "interpretation": "Regression for the transfer certificate only; not a general bound.",
    }


def equicorrelation_parameter_scout() -> dict[str, object]:
    records = []
    threshold = math.exp(-0.5)
    for sign in ("positive", "negative"):
        for n in (3, 6, 8):
            best = None
            for mu in np.geomspace(0.005, 1.0, 20):
                if sign == "positive":
                    a = mu * np.eye(n) + (1.0 - mu) * np.ones((n, n))
                else:
                    off = (1.0 - mu) / (n - 1)
                    a = np.eye(n) - off * (np.ones((n, n)) - np.eye(n))
                eig, vec = np.linalg.eigh((a + a.T) / 2)
                ainvhalf = (vec / np.sqrt(eig)) @ vec.T
                g = a.copy()
                m = math.ceil(1.0 / float(mu))
                for _ in range(m):
                    g = epoch_adjoint_float(a, g)
                h = ainvhalf @ g @ ainvhalf
                h = (h + h.T) / 2
                p = max(1, math.ceil(math.log(n)))
                root = float(
                    (np.trace(np.linalg.matrix_power(h, p)) / n) ** (1.0 / p)
                )
                item = {
                    "sign": sign,
                    "n": n,
                    "mu": float(mu),
                    "m": m,
                    "p": p,
                    "trace_moment_root": root,
                    "lambda_max_H_m": float(np.linalg.eigvalsh(h)[-1]),
                }
                if best is None or root > best["trace_moment_root"]:
                    best = item
            records.append(best)
    maximum = max(x["trace_moment_root"] for x in records)
    return {
        "evidence_level": "E1",
        "dtype": "float64",
        "mu_grid": "20 log-spaced values from 0.005 to 1",
        "selected_threshold_exp_minus_1_over_2": threshold,
        "preliminary_overstrong_threshold_exp_minus_3_over_2": math.exp(-1.5),
        "worst_cases": records,
        "maximum_observed": maximum,
        "hit": bool(maximum > threshold),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("exact", "scan", "hierarchy", "boundary", "block", "all"),
        default="all",
    )
    parser.add_argument("--seed", type=int, default=20260825)
    parser.add_argument("--trials", type=int, default=100)
    args = parser.parse_args()
    result: dict[str, object] = {
        "schema_version": "1.0",
        "script": "moment_falsifiers.py",
    }
    if args.mode in ("exact", "all"):
        result["commuting_control"] = {
            "A": "I_n",
            "update_factors_commute": True,
            "epoch_product": "0",
            "D": "I_n",
        }
        result["equicorrelation"] = equicorrelation_records()
        result["negative_equicorrelation"] = negative_equicorrelation_records()
        result["anisotropic"] = anisotropic_exact()
        result["signed_block"] = signed_block_exact()
        result["high_mu_two_epoch"] = high_mu_two_epoch_exact()
        result["seven_dimensional_second_prefix"] = seven_dimensional_second_prefix_certificate()
        result["temporal_third_moment_shortcut"] = temporal_third_moment_shortcut_exact()
        result["eight_dimensional_third_moment_stress"] = eight_dimensional_third_moment_stress_exact()
        result["linearized_replica_obstruction"] = linearized_replica_obstruction_exact()
        result["negative_replica_word"] = negative_replica_word_exact()
    if args.mode in ("scan", "all"):
        result["numerical_scout"] = numerical_scout(args.seed, args.trials)
        result["block_moment_scout"] = block_moment_scout()
        result["equicorrelation_parameter_scout"] = equicorrelation_parameter_scout()
        result["eight_dimensional_ray_scout"] = eight_dimensional_ray_scout()
        result["seven_dimensional_prefix_regression"] = seven_dimensional_prefix_regression()
    if args.mode in ("hierarchy", "all"):
        result["hierarchical_scout"] = hierarchical_scout(args.seed, args.trials)
    if args.mode in ("boundary", "all"):
        result["boundary_scout"] = boundary_scout(args.seed, args.trials)
    if args.mode in ("block", "all"):
        result["block_operator_scout"] = block_operator_scout(args.seed, args.trials)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
