"""Exact rational regression for the rank-two spectral region.

The universal proof is in spectral_geometry_region.md.  This script checks
one strict n=8 instance beyond the determinant, J2, and fixed-L3 scalar
regions, using only exact SymPy arithmetic.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    n = 8
    r = 4
    mu = sp.Rational(1, 100)
    high = sp.Rational(133, 100)
    directions = [
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (sp.Rational(3, 5), sp.Rational(4, 5)),
        (-sp.Rational(3, 5), -sp.Rational(4, 5)),
        (-sp.Rational(4, 5), sp.Rational(3, 5)),
        (sp.Rational(4, 5), -sp.Rational(3, 5)),
    ]
    u = sp.Matrix(
        [[sp.sympify(x) / 2, sp.sympify(y) / 2] for x, y in directions]
    )
    projector = sp.simplify(u * u.T)
    assert u.T * u == sp.eye(2)
    assert projector * projector == projector
    assert projector.rank() == 2
    assert all(projector[i, i] == sp.Rational(1, 4) for i in range(n))

    matrix = sp.simplify(high * sp.eye(n) - (high - mu) * projector)
    assert all(matrix[i, i] == 1 for i in range(n))
    assert matrix * u == mu * u
    assert sp.simplify(matrix * (sp.eye(n) - projector) - high * (sp.eye(n) - projector)) == sp.zeros(n)

    a0 = sp.Rational(r * (n - r), n * (n - 1))
    b0 = sp.Rational(r * (r - 1), n * (n - 1))
    exterior_low_over_mu = sp.factor(high ** (r - 2) * (a0 * high + b0 * mu))
    assert exterior_low_over_mu == sp.Rational(1892723, 2800000)
    assert exterior_low_over_mu > sp.Rational(1, 2)

    determinant = sp.factor(mu**2 * high ** (n - 2))
    determinant_ratio = sp.factor(determinant / (mu / 2))
    j2_low_over_mu = sp.factor(2 * (n - mu) / (n * (n - 1)))
    l3_prefix_over_mu = sp.Rational(3, n)
    assert determinant_ratio < 1
    assert j2_low_over_mu == sp.Rational(799, 2800)
    assert j2_low_over_mu < sp.Rational(1, 2)
    assert l3_prefix_over_mu < sp.Rational(1, 2)

    # Independent symbolic reconstruction of the rank-three endpoint bounds.
    m, k = sp.symbols("m k", integer=True, positive=True)
    even_x = sp.Rational(3, 1) / (2 * m - 3)
    even_truncation = sum(
        sp.binomial(m - 1, degree) * even_x**degree for degree in range(4)
    )
    even_gap = sp.factor(
        sp.expand_func(even_truncation - (4 - sp.Rational(2, 1) / m))
    )
    even_shifted_numerator = sp.factor(
        sp.together(even_gap).as_numer_denom()[0].subs(m, k + 2)
    )
    assert even_shifted_numerator == 3 * k**4 + 41 * k**3 + 48 * k**2 + 12 * k + 4

    odd_x = sp.Rational(3, 1) / (2 * (m - 1))
    odd_truncation = sum(
        sp.binomial(m, degree) * odd_x**degree for degree in range(4)
    )
    odd_gap = sp.factor(
        sp.expand_func(
            odd_truncation - (4 + sp.Rational(3, 1) / (m**2 - 1))
        )
    )
    expected_odd_gap = 3 * m * (m**2 + 13 * m - 20) / (
        16 * (m - 1) ** 2 * (m + 1)
    )
    assert sp.factor(odd_gap - expected_odd_gap) == 0

    rank4_boundary_ratio = sp.factor(
        sp.binomial(5, 4) * sp.Rational(9, 5) ** 4 / sp.binomial(9, 5)
    )
    assert rank4_boundary_ratio == sp.Rational(729, 1750)
    assert rank4_boundary_ratio < sp.Rational(1, 2)

    three_low_concentrated_ratio = sp.factor(
        (sp.binomial(4, 3) + 4 * sp.binomial(4, 2)) / sp.binomial(8, 4)
    )
    assert three_low_concentrated_ratio == sp.Rational(2, 5)
    p3_mu = sp.symbols("p3_mu", real=True)
    p3_exterior_gap_cleared = sp.factor(
        sp.binomial(4, 3)
        + (4 - p3_mu) * sp.binomial(4, 2)
        + (8 * p3_mu - 5 * p3_mu**2) * sp.binomial(4, 1)
        + (4 * p3_mu**2 - 3 * p3_mu**3)
        - sp.binomial(8, 4) / 2
    )
    assert sp.factor(
        p3_exterior_gap_cleared
        - (1 - p3_mu) * (3 * p3_mu**2 + 19 * p3_mu - 7)
    ) == 0

    # Parity endpoint identities for the general <=2-subunit-eigenvalue
    # corollary, reconstructed as rational functions of m.
    even_two_low_endpoint = sp.factor(m / (2 * m - 1))
    odd_two_low_endpoint = sp.factor(
        (m + 1) * (4 * m - 1) / (2 * (4 * m**2 - 1))
    )
    assert sp.factor(
        even_two_low_endpoint
        - sp.Rational(1, 2)
        - sp.Rational(1, 1) / (2 * (2 * m - 1))
    ) == 0
    assert sp.factor(
        odd_two_low_endpoint
        - sp.Rational(1, 2)
        - 3 * m / (2 * (4 * m**2 - 1))
    ) == 0

    even_margin_mu = sp.symbols("even_margin_mu", real=True)
    even_margin_formula = sp.factor(
        (1 - even_margin_mu)
        * (1 + (m - 2) * even_margin_mu)
        / (2 * (2 * m - 1))
    )
    even_candidate_ratio = sp.factor(
        m
        / (4 * (2 * m - 1))
        * (
            4
            - even_margin_mu
            + (3 * even_margin_mu - 2 * even_margin_mu**2) * (m - 2) / m
        )
    )
    assert sp.factor(
        even_candidate_ratio - sp.Rational(1, 2) - even_margin_formula
    ) == 0

    # A non-two-point exact spectrum in the broad <=2-subunit region.
    n7_mu = sp.Rational(1, 10)
    n7_large = sp.Rational(14, 5)
    n7_exterior_low_over_mu = sp.factor(
        (
            sp.binomial(4, 3)
            + (3 - n7_mu) * sp.binomial(4, 2)
            + (3 * n7_mu - 2 * n7_mu**2) * sp.binomial(4, 1)
        )
        / sp.binomial(7, 4)
    )
    n7_determinant_over_target = sp.factor(
        (n7_mu**2 * n7_large) / (n7_mu / 2)
    )
    assert n7_exterior_low_over_mu == sp.Rational(563, 875)
    assert n7_exterior_low_over_mu > sp.Rational(1, 2)
    assert n7_determinant_over_target == sp.Rational(14, 25)
    assert n7_determinant_over_target < 1

    result = {
        "status": "PASS",
        "evidence_level": (
            "E2 exact finite regression for an independently audited "
            "internal E4 proof candidate"
        ),
        "n": n,
        "r": r,
        "mu": str(mu),
        "high_eigenvalue": str(high),
        "projector_rank": projector.rank(),
        "projector_diagonal": str(projector[0, 0]),
        "exterior_low_over_mu": str(exterior_low_over_mu),
        "exterior_margin_over_half": str(exterior_low_over_mu - sp.Rational(1, 2)),
        "determinant_over_target": str(determinant_ratio),
        "j2_low_over_mu": str(j2_low_over_mu),
        "fixed_l3_prefix_over_mu": str(l3_prefix_over_mu),
        "rank3_even_endpoint_shifted_numerator": str(even_shifted_numerator),
        "rank3_odd_endpoint_gap": str(odd_gap),
        "rank4_n9_boundary_ratio_barrier": str(rank4_boundary_ratio),
        "three_low_concentrated_n8_barrier": str(three_low_concentrated_ratio),
        "three_low_n8_positive_mu_gap_cleared": str(p3_exterior_gap_cleared),
        "two_subunit_even_endpoint": str(even_two_low_endpoint),
        "two_subunit_odd_endpoint": str(odd_two_low_endpoint),
        "two_subunit_even_robust_margin": str(even_margin_formula),
        "two_subunit_n7_exterior_low_over_mu": str(n7_exterior_low_over_mu),
        "two_subunit_n7_determinant_over_target": str(n7_determinant_over_target),
        "scope": (
            "The matrix is a strict exact example inside the rank-two spectral "
            "region.  The all-n quantifiers come from the symbolic proof, not "
            "from this finite computation."
        ),
    }
    output = Path(__file__).with_name("SPECTRAL_RANK2_EXACT.json")
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
