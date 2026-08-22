"""Exact reconstruction for the matching-block `W4` slice."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def main() -> None:
    d, a, u, k = sp.symbols("d a u k", nonnegative=True)
    t = a * u
    base = 4 * (d - 1) * (d - 2)

    n_plus = sp.factor(
        base * (a + t)
        + (3 * d - 4) * t**2 * (1 + a + t)
        - 10 * (d - 2) * t * (1 + a + t)
    )
    n_minus = sp.factor(
        base * (a - t)
        + (3 * d - 4) * t**2 * (1 + a - t)
        + 10 * (d - 2) * t * (1 + a - t)
    )

    n6 = sp.factor(n_plus.subs(d, 6))
    dn6 = sp.factor(sp.diff(n_plus, d).subs(d, 6))
    expected_n6 = sp.factor(
        2
        * a
        * (
            40
            + 20 * u
            - 20 * a * u
            - 13 * a * u**2
            + 7 * a**2 * u**2
            + 7 * a**2 * u**3
        )
    )
    expected_dn6 = sp.factor(
        a
        * (
            36
            + 26 * u
            - 10 * a * u
            - 7 * a * u**2
            + 3 * a**2 * u**2
            + 3 * a**2 * u**3
        )
    )
    assert sp.factor(n6 - expected_n6) == 0
    assert sp.factor(dn6 - expected_dn6) == 0
    dimension_expansion = sp.factor(
        n_plus.subs(d, 6 + k)
        - (expected_n6 + k * expected_dn6 + 4 * a * (1 + u) * k**2)
    )
    assert dimension_expansion == 0

    # A concrete exact matrix reconstruction verifies the retained-state
    # simplification on unequal signed blocks plus a singleton.
    r1, r2 = sp.Rational(3, 5), -sp.Rational(2, 7)
    H = sp.diag(
        *[
            sp.Matrix([[0, r1], [r1, 0]]),
            sp.Matrix([[0, r2], [r2, 0]]),
            sp.zeros(1),
            sp.zeros(1),
        ]
    )
    size = H.rows
    D = sp.diag(*[H.pow(2)[i, i] for i in range(size)])
    F = H + H.pow(2) - D
    E = sp.diag(*[H.pow(3)[i, i] for i in range(size)])
    S = (
        (size - 3) * H.pow(2)
        - 2 * H.pow(3)
        + H * D
        + D * H
        + sp.diag(*[F.pow(2)[i, i] for i in range(size)])
    )
    assert H.pow(2) == D
    assert F == H
    assert E == sp.zeros(size)
    assert S == (size - 2) * D

    result = {
        "schema_version": "1.0",
        "evidence_level": "E3 analytic proof candidate plus E2 exact reconstruction",
        "verdict": "PASS",
        "n_plus_d6": str(n6),
        "n_plus_dimension_derivative_d6": str(dn6),
        "dimension_taylor_remainder": "4*a*(u + 1)*k**2",
        "n_minus_manifest_form": str(n_minus),
        "matrix_control": {
            "dimension": size,
            "block_correlations": [str(r1), str(r2)],
            "H2_equals_D": True,
            "S_equals_d_minus_2_D": True,
        },
    }
    output = Path("research/iteration6/route_l3/evidence/W4_MATCHING_BLOCK_EXACT.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
