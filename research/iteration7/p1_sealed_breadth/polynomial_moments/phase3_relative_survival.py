#!/usr/bin/env python3
"""Exact and numerical attacks on the phase-3 relative-survival repair.

The exact mode uses SymPy rationals.  The scan mode is a seeded float64
falsifier and cannot certify a quantified statement.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import sympy as sp


SCRIPT_DIR = Path(__file__).resolve().parent
MOMENT_SCRIPT = SCRIPT_DIR / "moment_falsifiers.py"


def load_moment_module():
    spec = importlib.util.spec_from_file_location("moment_falsifiers", MOMENT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {MOMENT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MF = load_moment_module()


def frac(value: sp.Expr) -> str:
    return str(sp.factor(value))


def exact_orbit_pair(a: sp.Matrix, step: int) -> tuple[sp.Matrix, sp.Matrix]:
    """Return simultaneous rational similarities of H_step,H_(step+1)."""
    g = a
    for _ in range(step):
        g = MF.exact_epoch_adjoint(a, g)
    g_next = MF.exact_epoch_adjoint(a, g)
    return sp.simplify(a.inv() * g), sp.simplify(a.inv() * g_next)


def exact_relative_record(
    name: str, a: sp.Matrix, mu: sp.Rational, step: int, p: int
) -> dict[str, object]:
    """Certify one ALT relative-survival comparison over the rationals.

    If X,Y are the energy-coordinate SPD orbit matrices, the matrices returned
    by exact_orbit_pair are simultaneously similar to X,Y.  Cyclicity gives

      tr(X^p C^p)=tr(X^(p-1) Y (X^(-1)Y)^(p-1)),

    where C=X^(-1/2)YX^(-1/2).  The right side is therefore rational.
    """
    x, y = exact_orbit_pair(a, step)
    trace_xp = sp.factor(sp.trace(x**p))
    trace_yp = sp.factor(sp.trace(y**p))
    relative_survival = sp.factor(
        sp.trace(x ** (p - 1) * y * (x.inv() * y) ** (p - 1))
    )
    actual_loss = sp.factor(trace_xp - trace_yp)
    alt_loss = sp.factor(trace_xp - relative_survival)
    endpoint_loss = sp.factor(p * sp.trace(y ** (p - 1) * (x - y)))
    alt_gap = sp.factor(actual_loss - alt_loss)
    endpoint_gap = sp.factor(alt_loss - endpoint_loss)
    half_mu_gap = sp.factor((1 - mu / 2) ** p * trace_xp - relative_survival)
    return {
        "name": name,
        "step_j": step,
        "p": p,
        "mu": frac(mu),
        "trace_X_p": frac(trace_xp),
        "trace_Y_p": frac(trace_yp),
        "relative_survival_numerator": frac(relative_survival),
        "relative_survival_ratio_decimal_17": float(relative_survival / trace_xp),
        "actual_trace_power_loss": frac(actual_loss),
        "alt_positive_loss": frac(alt_loss),
        "endpoint_linearized_loss": frac(endpoint_loss),
        "actual_minus_alt": frac(alt_gap),
        "alt_minus_endpoint": frac(endpoint_gap),
        "alt_is_valid": bool(alt_gap >= 0),
        "alt_strictly_improves_endpoint_here": bool(endpoint_gap > 0),
        "gap_to_(1-mu/2)^p_local_bound": frac(half_mu_gap),
        "local_half_mu_bound_survives": bool(half_mu_gap > 0),
        "evidence_level": "E2 exact finite verification",
    }


def exact_suite() -> dict[str, object]:
    eps = sp.Rational(1, 1000)
    b = sp.Matrix(
        [
            [1, 0],
            [0, 1],
            [sp.Rational(3, 5), sp.Rational(4, 5)],
            [sp.Rational(4, 5), sp.Rational(3, 5)],
        ]
    )
    anisotropic = eps * sp.eye(4) + (1 - eps) * b * b.T

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
    b8 = sp.Matrix(rows)
    signed_eight = (sp.eye(8) + b8 * b8.T) / 2
    records = [
        exact_relative_record(
            "anisotropic_noncommuting_eps_1_over_1000", anisotropic, eps, 1, 3
        ),
        exact_relative_record(
            "fully_coupled_signed_n8_mu_1_over_2",
            signed_eight,
            sp.Rational(1, 2),
            1,
            3,
        ),
    ]
    # ALT is a trace inequality.  This rational two-by-two example prevents
    # silently promoting its positive trace gap to a Loewner comparison.
    x = sp.diag(1, sp.Rational(1, 4))
    x_half = sp.diag(1, sp.Rational(1, 2))
    x_three_halves = sp.diag(1, sp.Rational(1, 8))
    c_relative = sp.Matrix(
        [[sp.Rational(1, 2), sp.Rational(2, 5)],
         [sp.Rational(2, 5), sp.Rational(1, 2)]]
    )
    y = x_half * c_relative * x_half
    loewner_residual = sp.simplify(
        x_three_halves * c_relative**3 * x_three_halves - y**3
    )
    operator_promotion_obstruction = {
        "X": [[frac(x[i, j]) for j in range(2)] for i in range(2)],
        "C": [[frac(c_relative[i, j]) for j in range(2)] for i in range(2)],
        "Y=X^(1/2)CX^(1/2)": [[frac(y[i, j]) for j in range(2)] for i in range(2)],
        "det_C": frac(c_relative.det()),
        "det_I_minus_C": frac((sp.eye(2) - c_relative).det()),
        "p": 3,
        "putative_Loewner_residual": [
            [frac(loewner_residual[i, j]) for j in range(2)] for i in range(2)
        ],
        "trace_residual": frac(sp.trace(loewner_residual)),
        "determinant_residual": frac(loewner_residual.det()),
        "conclusion": "The ALT trace residual is positive but the matrix residual is indefinite; trace control cannot be promoted to Loewner order.",
        "evidence_level": "E2 exact finite counterexample to the shortcut",
    }
    # The inherited scalar facts H_1<=(1-3mu/n)I and
    # tr(H_1)<=n-1-2mu+mu^2 do not by themselves prove the desired first-step
    # p-moment loss.  This abstract spectrum saturates both facts at n=8.
    scalar_data_spectrum = [sp.Rational(13, 16)] * 7 + [sp.Rational(9, 16)]
    scalar_data_moment = sum(value**3 for value in scalar_data_spectrum)
    scalar_data_target = 8 * (1 - sp.Rational(1, 4)) ** 3
    scalar_data_obstruction = {
        "n": 8,
        "p": 3,
        "mu": "1/2",
        "abstract_H1_spectrum": [frac(value) for value in scalar_data_spectrum],
        "lambda_max_H1": "13/16=1-3mu/n",
        "trace_H1": frac(sum(scalar_data_spectrum)),
        "inherited_trace_upper_bound": "25/4=n-1-2mu+mu^2",
        "trace_H1_cubed": frac(scalar_data_moment),
        "desired_first_step_upper_bound": frac(scalar_data_target),
        "strict_failure_margin": frac(scalar_data_moment - scalar_data_target),
        "conclusion": "The one-epoch Loewner floor plus the two-prefix scalar trace bound are information-theoretically insufficient for the local half-mu p=3 estimate; more RPCD orbit structure is required.",
        "scope_warning": "This is an abstract compatible spectrum, not an RPCD counterexample.",
        "evidence_level": "E2 exact obstruction to the scalar-data implication",
    }
    assert all(record["alt_is_valid"] for record in records)
    assert all(record["local_half_mu_bound_survives"] for record in records)
    assert sp.trace(loewner_residual) > 0 and loewner_residual.det() < 0
    assert scalar_data_moment > scalar_data_target
    return {
        "engine": "SymPy Rational; all reported signs are exact",
        "records": records,
        "operator_promotion_obstruction": operator_promotion_obstruction,
        "scalar_prefix_data_obstruction": scalar_data_obstruction,
        "scope": "two finite stresses only; no general local inequality is certified",
    }


def whiten(a: np.ndarray, g: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh((a + a.T) / 2)
    inverse_half = (eigenvectors / np.sqrt(eigenvalues)) @ eigenvectors.T
    h = inverse_half @ g @ inverse_half
    return (h + h.T) / 2


def relative_ratio_float(x: np.ndarray, y: np.ndarray, p: int) -> tuple[float, float]:
    eigenvalues, eigenvectors = np.linalg.eigh((x + x.T) / 2)
    if eigenvalues[0] < 1.0e-13:
        raise np.linalg.LinAlgError("orbit support is numerically singular")
    inverse_half = (eigenvectors / np.sqrt(eigenvalues)) @ eigenvectors.T
    c = inverse_half @ y @ inverse_half
    c = (c + c.T) / 2
    x_power = np.linalg.matrix_power(x, p)
    trace_xp = float(np.trace(x_power))
    numerator = float(np.trace(x_power @ np.linalg.matrix_power(c, p)))
    return numerator / trace_xp, float(eigenvalues[0])


def numerical_scout(seed: int) -> dict[str, object]:
    """Attack the sufficient per-step exponent 1/2 on singular Gram rays."""
    rng = np.random.default_rng(seed)
    plan = ((8, 60), (9, 40), (10, 25))
    best: dict[str, object] | None = None
    instance_count = 0
    evaluated_steps = 0
    singular_support_skips = 0
    numerical_violations: list[dict[str, object]] = []
    for n, trials in plan:
        for trial in range(trials):
            rank = int(rng.integers(2, n))
            rows = rng.normal(size=(n, rank))
            rows /= np.linalg.norm(rows, axis=1)[:, None]
            c = rows @ rows.T
            mu = float(10.0 ** rng.uniform(-2.3, -0.25))
            a = mu * np.eye(n) + (1.0 - mu) * c
            p = math.ceil(math.log(n))
            m = math.ceil(1.0 / mu)
            selected_steps = (
                set(range(m))
                if m <= 60
                else set(np.unique(np.linspace(0, m - 1, 60, dtype=int)))
            )
            g = a.copy()
            instance_count += 1
            for step in range(m):
                g_next = MF.epoch_adjoint_float(a, g)
                if step in selected_steps:
                    x = whiten(a, g)
                    y = whiten(a, g_next)
                    try:
                        ratio, minimum_x = relative_ratio_float(x, y, p)
                    except np.linalg.LinAlgError:
                        singular_support_skips += 1
                        break
                    evaluated_steps += 1
                    if ratio <= 0.0 or ratio > 1.0 + 1.0e-6:
                        numerical_violations.append(
                            {
                                "n": n,
                                "trial": trial,
                                "step": step,
                                "mu": mu,
                                "ratio": ratio,
                                "minimum_eigenvalue_X": minimum_x,
                            }
                        )
                    else:
                        clipped_ratio = min(ratio, 1.0)
                        exponent = -math.log(clipped_ratio) / (p * mu)
                        item: dict[str, object] = {
                            "normalized_relative_survival_exponent": exponent,
                            "n": n,
                            "trial": trial,
                            "step": step,
                            "mu": mu,
                            "m": m,
                            "p": p,
                            "rank_C": rank,
                            "relative_survival_ratio": ratio,
                            "minimum_eigenvalue_X": minimum_x,
                        }
                        if best is None or exponent < best[
                            "normalized_relative_survival_exponent"
                        ]:
                            best = item
                g = g_next
    hit = bool(
        best
        and best["normalized_relative_survival_exponent"] < 0.5 - 1.0e-8
    )
    return {
        "seed": seed,
        "dtype": "float64",
        "plan": {str(n): trials for n, trials in plan},
        "instances": instance_count,
        "evaluated_orbit_steps": evaluated_steps,
        "construction": "A=mu*I+(1-mu)*CC^T with normalized Gaussian rows, rank(C)<n",
        "mu_distribution": "log-uniform on [10^-2.3,10^-0.25]",
        "time_sampling": "every step if m<=60; otherwise 60 integer linspace steps in [0,m-1]",
        "support_eigenvalue_cutoff": 1.0e-13,
        "ratio_roundoff_tolerance": 1.0e-6,
        "candidate_exponent_threshold": 0.5,
        "decision_margin": 1.0e-8,
        "minimum_observed": best,
        "singular_support_skips": singular_support_skips,
        "numerical_ratio_violations": numerical_violations,
        "hit": hit,
        "evidence_level": "E1 numerical null search",
        "interpretation": "A hit would refute the per-step sufficient sublemma, not MC or C050. A null scout proves nothing general.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("exact", "scan", "all"), default="all")
    parser.add_argument("--seed", type=int, default=2718281828)
    args = parser.parse_args()
    result: dict[str, object] = {
        "schema_version": "1.0",
        "script": Path(__file__).name,
    }
    if args.mode in ("exact", "all"):
        result["exact_suite"] = exact_suite()
    if args.mode in ("scan", "all"):
        result["numerical_scout"] = numerical_scout(args.seed)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
