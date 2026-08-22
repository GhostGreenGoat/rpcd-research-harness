"""Independent exact-algebra audit of the Iteration-6 L3 proof candidate.

This file was written from the displayed mathematical claims, without
importing the sibling verifier.  It checks the scalar factorizations,
reconstructs the tensor Bernstein coefficients from monomial coefficients,
and checks every parent-level cancellation.  The operator arguments and
inequality directions are audited separately in L3_HOSTILE_AUDIT.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def bernstein_tensor(
    polynomial: sp.Expr,
    variables: tuple[sp.Symbol, ...],
    degrees: tuple[int, ...],
) -> list:
    """Return tensor Bernstein coefficients in nested first-variable order."""
    poly = sp.Poly(sp.expand(polynomial), *variables)

    def coefficient_at(position: tuple[int, ...]) -> sp.Expr:
        total = sp.Integer(0)
        for monomial, coefficient in poly.terms():
            if all(power <= slot for power, slot in zip(monomial, position)):
                weight = sp.Integer(1)
                for power, slot, degree in zip(monomial, position, degrees):
                    weight *= sp.binomial(slot, power) / sp.binomial(degree, power)
                total += coefficient * weight
        return sp.factor(total)

    def build(axis: int, prefix: tuple[int, ...]) -> list | sp.Expr:
        if axis == len(variables):
            return coefficient_at(prefix)
        return [build(axis + 1, prefix + (slot,)) for slot in range(degrees[axis] + 1)]

    return build(0, tuple())


def strings(value):
    if isinstance(value, list):
        return [strings(item) for item in value]
    return str(sp.factor(value))


def main() -> None:
    lam, mu, d = sp.symbols("lambda mu d", positive=True)
    p = ((3 * d + 1) - 4 * lam + 2 * (lam - 1) ** 2 / (d - 1)) / (
        2 * d * (d - 1)
    )
    g = p - 3 * mu / (2 * d * lam)

    low_factor = (1 - lam) * (2 * d - lam - 1) / (d * (d - 1) ** 2)
    assert sp.factor(g.subs(mu, lam) - low_factor) == 0
    assert sp.factor(g - g.subs(mu, lam) - 3 * (lam - mu) / (2 * d * lam)) == 0

    b_poly = 2 * lam**2 - (4 * d - 2) * lam + 3 * (d - 1) ** 2
    high_factor = (lam - 1) * b_poly / (2 * d * lam * (d - 1) ** 2)
    assert sp.factor(g - 3 * (1 - mu) / (2 * d * lam) - high_factor) == 0
    b_at_vertex = sp.factor(b_poly.subs(lam, d - sp.Rational(1, 2)))
    assert sp.factor(b_at_vertex - (2 * d**2 - 8 * d + 5) / 2) == 0

    # Exceptional d=3 scalar gap, reconstructed directly.
    t, v = sp.symbols("t v", nonnegative=True)
    mu3 = 1 - v
    lam3 = 1 - v + 3 * v * t
    g3 = sp.factor(g.subs({d: 3, mu: mu3, lam: lam3}))
    target3 = 3 * (lam3 - mu3) * (1 - mu3) / (
        6 * lam3 * (lam3 + 1 - mu3)
    )
    gap3 = sp.factor(g3 - target3)
    q3 = sp.factor(sp.cancel(gap3 * 12 * (1 + 3 * t * v) / v))
    assert sp.denom(q3) == 1
    table3 = bernstein_tensor(q3, (t, v), (3, 2))
    expected3 = [
        [4, sp.Rational(9, 2), 5],
        [6, sp.Rational(15, 2), 10],
        [8, 6, 0],
        [10, 0, 2],
    ]
    assert table3 == expected3

    # Child d=2, low-mu compensator kappa=mu/2.  Multiplication by the
    # displayed positive denominator reconstructs a polynomial independently.
    p2 = sp.factor(p.subs(d, 2))
    g2 = sp.factor(g.subs(d, 2))
    mu_low = 1 - v
    lam_low = 1 - v + 2 * v * t
    gap_low = sp.factor(
        g2.subs({mu: mu_low, lam: lam_low})
        - sp.Rational(1, 2)
        * (lam_low - mu_low)
        * (1 - mu_low)
        / (lam_low * (lam_low + 1 - mu_low))
    )
    numerator_low, denominator_low = sp.fraction(sp.cancel(gap_low))
    numerator_low = sp.factor(numerator_low)
    denominator_low = sp.factor(denominator_low)
    # Divide only the manifest endpoint factor; the quotient must be a
    # polynomial.  A positive rational scaling does not affect positivity.
    q_low = sp.factor(numerator_low / v)
    assert sp.denom(q_low) == 1
    degree_low = (sp.degree(q_low, t), sp.degree(q_low, v))
    table_low = bernstein_tensor(q_low, (t, v), degree_low)

    # Child d=2, high-mu compensator kappa=(5mu-2)/4.  Use w=3(1-mu).
    w = sp.symbols("w", nonnegative=True)
    mu_high = 1 - w / 3
    lam_high = 1 - w / 3 + 2 * w * t / 3
    kappa_over_mu_high = (5 * mu_high - 2) / (4 * mu_high)
    gap_high = sp.factor(
        g2.subs({mu: mu_high, lam: lam_high})
        - kappa_over_mu_high
        * (lam_high - mu_high)
        * (1 - mu_high)
        / (lam_high * (lam_high + 1 - mu_high))
    )
    # Normalize exactly as in the displayed rational gap, but derive Q from
    # the gap rather than importing any coefficients.
    q_high = sp.factor(
        sp.cancel(
            gap_high
            * 18
            * (3 - w)
            * (3 + 2 * t * w)
            * (3 - w + 2 * t * w)
            / w
        )
    )
    assert sp.denom(q_high) == 1
    table_high = bernstein_tensor(q_high, (t, w), (4, 4))
    expected_high = [
        [162, sp.Rational(567, 4), sp.Rational(243, 2), 102, 84],
        [sp.Rational(567, 4), sp.Rational(1053, 8), sp.Rational(975, 8), sp.Rational(897, 8), sp.Rational(205, 2)],
        [sp.Rational(243, 2), sp.Rational(459, 4), sp.Rational(437, 4), sp.Rational(211, 2), 103],
        [sp.Rational(405, 4), sp.Rational(729, 8), sp.Rational(669, 8), sp.Rational(621, 8), sp.Rational(147, 2)],
        [81, sp.Rational(243, 4), 45, 36, 34],
    ]
    assert table_high == expected_high

    # Parent-level coefficient identities, checked independently.
    m = sp.symbols("m", integer=True, positive=True)
    beta_general = 3 * mu / (2 * (m - 1))
    closure_general = sp.factor(
        beta_general
        - 2 * mu / m
        + mu * (sp.Rational(1, 2) / m - beta_general / m)
    )
    assert sp.factor(
        closure_general - 3 * mu * (1 - mu) / (2 * m * (m - 1))
    ) == 0

    beta3 = 3 * mu / 4
    q_parent = (2 - 3 * mu) / 12
    kappa_low = mu / 2
    closure_low = sp.factor(
        beta3 - 2 * mu / 3 - (beta3 - kappa_low) * (1 - mu) + q_parent * mu
    )
    assert closure_low == 0
    kappa_high = (5 * mu - 2) / 4
    closure_high = sp.factor(
        beta3
        - 2 * mu / 3
        - (beta3 - kappa_high) * (1 - mu)
        + q_parent * (3 - 2 * mu)
    )
    assert closure_high == 0

    result = {
        "status": "PASS",
        "evidence_level": "exact algebra audit plus separate handwritten operator audit",
        "d3_bernstein": strings(table3),
        "d2_low_gap_denominator": str(denominator_low),
        "d2_low_polynomial_degree": [int(value) for value in degree_low],
        "d2_low_bernstein": strings(table_low),
        "d2_high_bernstein": strings(table_high),
        "general_parent_remainder": str(closure_general),
        "m3_low_parent_remainder": str(closure_low),
        "m3_high_parent_remainder": str(closure_high),
    }
    output = Path(__file__).with_name("L3_INDEPENDENT_EXACT_AUDIT.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
