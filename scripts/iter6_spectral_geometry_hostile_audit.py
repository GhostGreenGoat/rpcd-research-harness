"""Independent exact audit of the spectral-geometry certificate.

This is deliberately a reconstruction from the displayed definitions in
``spectral_geometry_region.md``.  It does not import or invoke that route's
verifier.  Symbolic algebra is used only to check identities whose analytic
sign arguments are recorded in the accompanying hostile-audit note.
"""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    n, r, mu, a = sp.symbols("n r mu a", positive=True)
    A0 = r * (n - r) / (n * (n - 1))
    B0 = r * (r - 1) / (n * (n - 1))
    c2 = 2 / (n - 2)
    R2 = a ** (r - 2) * (A0 * a + B0 * mu)
    reconstructed_R2_prime = sp.factor(
        sp.diff(R2, mu) + sp.diff(R2, a) * (-c2)
    )
    claimed_R2_prime = sp.factor(
        a ** (r - 3)
        * (a * (B0 - A0 * c2 * (r - 1)) - B0 * c2 * (r - 2) * mu)
    )
    assert sp.factor(reconstructed_R2_prime - claimed_R2_prime) == 0
    assert sp.factor(B0 / A0 - (r - 1) / (n - r)) == 0

    denominator = n * (n - 1) * (n - 2)
    A3 = r * (n - r) * (n - r - 1) / denominator
    B3 = 2 * r * (r - 1) * (n - r) / denominator
    C3 = r * (r - 1) * (r - 2) / denominator
    c3 = 3 / (n - 3)
    R3 = a ** (r - 3) * (A3 * a**2 + B3 * mu * a + C3 * mu**2)
    reconstructed_R3_prime = sp.factor(
        sp.diff(R3, mu) + sp.diff(R3, a) * (-c3)
    )
    d0 = B3 - A3 * c3 * (r - 1)
    d1 = 2 * C3 - B3 * c3 * (r - 2)
    d2 = C3 * c3 * (r - 3)
    claimed_R3_prime = sp.factor(
        a ** (r - 4) * (a**2 * d0 + mu * a * d1 - mu**2 * d2)
    )
    assert sp.factor(reconstructed_R3_prime - claimed_R3_prime) == 0
    d1_factor = sp.factor(
        2
        * r
        * (r - 1)
        * (r - 2)
        * (3 * r - 2 * n - 3)
        / (n * (n - 1) * (n - 2) * (n - 3))
    )
    assert sp.factor(d1 - d1_factor) == 0

    # Reconstruct the two rank-three endpoint estimates without calling the
    # source route's checker.
    m, k = sp.symbols("m k", positive=True, integer=True)
    x_even = 3 / (2 * m - 3)
    even_first_four = (
        1
        + (m - 1) * x_even
        + (m - 1) * (m - 2) * x_even**2 / 2
        + (m - 1) * (m - 2) * (m - 3) * x_even**3 / 6
    )
    even_gap = sp.factor(even_first_four - (4 - 2 / m))
    even_gap_k = sp.factor(even_gap.subs(m, k + 2))
    expected_even_gap_k = sp.factor(
        (3 * k**4 + 41 * k**3 + 48 * k**2 + 12 * k + 4)
        / (2 * (k + 2) * (2 * k + 1) ** 3)
    )
    assert sp.factor(even_gap_k - expected_even_gap_k) == 0

    x_odd = 3 / (2 * (m - 1))
    odd_first_four = (
        1
        + m * x_odd
        + m * (m - 1) * x_odd**2 / 2
        + m * (m - 1) * (m - 2) * x_odd**3 / 6
    )
    odd_gap = sp.factor(odd_first_four - (4 + 3 / (m**2 - 1)))
    expected_odd_gap = sp.factor(
        3 * m * (m**2 + 13 * m - 20) / (16 * (m - 1) ** 2 * (m + 1))
    )
    assert sp.factor(odd_gap - expected_odd_gap) == 0

    # Reconstruct the endpoint formulas in the broad two-subunit region.
    even_E0_ratio = sp.factor(
        (
            sp.binomial(2 * m - 3, m - 1)
            + 3 * sp.binomial(2 * m - 3, m - 2)
        )
        / sp.binomial(2 * m, m)
    )
    odd_E0_ratio = sp.factor(
        (
            sp.binomial(2 * m - 2, m)
            + 3 * sp.binomial(2 * m - 2, m - 1)
        )
        / sp.binomial(2 * m + 1, m + 1)
    )
    # SymPy does not always simplify symbolic binomials, so verify after
    # rewriting in factorials.
    even_E0_ratio = sp.factor(sp.combsimp(even_E0_ratio))
    odd_E0_ratio = sp.factor(sp.combsimp(odd_E0_ratio))
    assert sp.factor(even_E0_ratio - m / (2 * m - 1)) == 0
    expected_odd_ratio = (m + 1) * (4 * m - 1) / (2 * (4 * m**2 - 1))
    assert sp.factor(odd_E0_ratio - expected_odd_ratio) == 0

    # J2 endpoint ordering.
    lam = sp.symbols("lambda", real=True)
    L = n - (n - 1) * mu
    f = lambda z: 2 * z * (n - z) / (n * (n - 1))
    j2_endpoint_gap = sp.factor(f(L) - f(mu))
    expected_j2_gap = sp.factor(2 * mu * (n - 2) * (1 - mu) / (n - 1))
    assert sp.factor(j2_endpoint_gap - expected_j2_gap) == 0

    result = {
        "schema_version": "1.0",
        "verdict": "PASS_WITH_SCOPE_CORRECTION",
        "independence": "Does not import or invoke verify_spectral_rank2_region.py.",
        "two_subunit_endpoint_ratios": {
            "even_n_2m": str(even_E0_ratio),
            "odd_n_2m_plus_1": str(odd_E0_ratio),
        },
        "rank2_derivative": str(reconstructed_R2_prime),
        "rank3_d1_factor": str(d1_factor),
        "rank3_even_first_four_gap_k_m_minus_2": str(even_gap_k),
        "rank3_odd_first_four_gap": str(odd_gap),
        "j2_endpoint_gap": str(j2_endpoint_gap),
        "scope_correction": (
            "State the two-subunit corollary for n>=3; n=2 is separate because "
            "the N=n-3 compression notation is not defined there."
        ),
    }
    output = Path("research/iteration6/route_l3/evidence/SPECTRAL_GEOMETRY_HOSTILE_AUDIT.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
