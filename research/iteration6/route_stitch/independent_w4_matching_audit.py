"""Independent exact audit of the matching-support W4 slice.

This deliberately reconstructs the displayed identities without importing or
calling the route_l3 checker.  It is regression evidence for the analytic
sign argument in W4_MATCHING_BLOCK_HOSTILE_AUDIT.md.
"""

from __future__ import annotations

import json

import sympy as sp


def main() -> None:
    d, a, u, k = sp.symbols("d a u k", nonnegative=True)
    mu, lam = sp.symbols("mu lam", positive=True)
    t = a * u

    # Reconstruct the two block eigenline numerators from the L3 eigenvalue.
    def numerator(h: sp.Expr) -> sp.Expr:
        ell = (
            4 * (d - 1) * (d - 2)
            - 10 * (d - 2) * h
            + (3 * d - 4) * t**2
        ) / (2 * d * (d - 1) * (d - 2))
        rhs = 2 / (d * (1 + a + h))
        return sp.factor(
            (ell - rhs)
            * 2
            * d
            * (d - 1)
            * (d - 2)
            * (1 + a + h)
        )

    n_plus = sp.factor(numerator(t))
    n_minus = sp.factor(numerator(-t))
    expected_plus = sp.factor(
        4 * (d - 1) * (d - 2) * (a + t)
        + (3 * d - 4) * t**2 * (1 + a + t)
        - 10 * (d - 2) * t * (1 + a + t)
    )
    expected_minus = sp.factor(
        4 * (d - 1) * (d - 2) * (a - t)
        + (3 * d - 4) * t**2 * (1 + a - t)
        + 10 * (d - 2) * t * (1 + a - t)
    )
    assert sp.factor(n_plus - expected_plus) == 0
    assert sp.factor(n_minus - expected_minus) == 0

    b6 = 40 + 20 * u - 20 * a * u - 13 * a * u**2 + 7 * a**2 * u**2 + 7 * a**2 * u**3
    db6 = 36 + 26 * u - 10 * a * u - 7 * a * u**2 + 3 * a**2 * u**2 + 3 * a**2 * u**3
    assert sp.factor(n_plus.subs(d, 6) - 2 * a * b6) == 0
    assert sp.factor(sp.diff(n_plus, d).subs(d, 6) - a * db6) == 0
    assert sp.factor(
        n_plus.subs(d, 6 + k)
        - 2 * a * b6
        - k * a * db6
        - 4 * a * (1 + u) * k**2
    ) == 0

    # Direct retained-state reconstruction on unequal, oppositely signed blocks.
    r1, r2 = sp.Rational(3, 5), -sp.Rational(2, 7)
    H = sp.diag(
        sp.Matrix([[0, r1], [r1, 0]]),
        sp.Matrix([[0, r2], [r2, 0]]),
        sp.zeros(1),
        sp.zeros(1),
    )
    dim = H.rows
    D = sp.diag(*[(H**2)[i, i] for i in range(dim)])
    E = sp.diag(*[(H**3)[i, i] for i in range(dim)])
    F = H + H**2 - D
    S = (
        (dim - 3) * H**2
        - 2 * H**3
        + H * D
        + D * H
        + sp.diag(*[(F**2)[i, i] for i in range(dim)])
    )
    assert H**2 == D
    assert F == H
    assert E == sp.zeros(dim)
    assert S == (dim - 2) * D

    # Reconstruct the spectral simplification behind the uniform outer envelope.
    envelope_sum = (
        2 * mu / (d * lam)
        + 2 * (1 - mu) * (lam - mu) / (d * lam * (lam + 1 - mu))
    )
    assert sp.factor(envelope_sum - 2 / (d * (lam + 1 - mu))) == 0
    schur_den = lam**2 / (lam - mu) - (1 - mu) * lam
    assert sp.factor(
        schur_den - mu * lam * (lam + 1 - mu) / (lam - mu)
    ) == 0

    # Fixed exact, nonuniform signed-block control at d=6 and mu=1/5.
    mu0 = sp.Rational(1, 5)
    gaps = []
    for corr in (r1, r2):
        mag = abs(corr)
        for h in (mag, -mag):
            ell = (
                4 * 5 * 4 - 10 * 4 * h + 14 * mag**2
            ) / (2 * 6 * 5 * 4)
            gaps.append(sp.factor(ell - sp.Rational(1, 3) / (1 + 1 - mu0 + h)))
    assert all(gap >= 0 for gap in gaps)

    result = {
        "schema_version": "1.0",
        "verdict": "PASS",
        "evidence_level": "E4 internal proof candidate after independent exact hostile reconstruction; no formal or external review",
        "scope": "d>=6, unit-diagonal SPD matching-support C, 0<mu<=lambda_min(C)",
        "checked": [
            "retained-state H^2=D, F=H, E=0, S=(d-2)D",
            "L3 block eigenline numerators for both signs",
            "exact Taylor expansion about d=6",
            "uniform outer-Schur-envelope spectral simplification",
            "unequal oppositely signed rational block control",
        ],
        "fixed_exact_gaps": [str(x) for x in gaps],
        "caveat": "This is a matching-support slice, not the universal W4 lemma.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
