"""Independent symbolic hostile audit of the equal-weight-star W4 slice."""

from __future__ import annotations

import json

import sympy as sp


def bernstein(poly: sp.Expr, t: sp.Symbol) -> list[sp.Expr]:
    numerator = sp.fraction(sp.factor(poly))[0]
    p = sp.Poly(sp.expand(numerator), t)
    degree = p.degree()
    return [
        sp.factor(sum(
            p.coeff_monomial(t**j) * sp.binomial(i, j) / sp.binomial(degree, j)
            for j in range(i + 1)
        ))
        for i in range(degree + 1)
    ]


def coefficient_sign_digest(values: list[sp.Expr], variables: tuple[sp.Symbol, ...]) -> dict[str, int]:
    power_coefficients: list[sp.Expr] = []
    for value in values:
        numerator = sp.fraction(sp.together(value))[0]
        power_coefficients.extend(sp.Poly(sp.expand(numerator), *variables).coeffs())
    assert all(value >= 0 for value in power_coefficients)
    return {
        "power_coefficient_count": len(power_coefficients),
        "zero_count": sum(value == 0 for value in power_coefficients),
    }


def main() -> None:
    p, d, t, a, h = sp.symbols("p d t a h", nonnegative=True)
    w = t**2 / p + (p - 1) * t**4 / p**2

    # Definition-level reconstruction of the retained star sectors.
    s_cc = sp.factor((d - 3) * t**2 + t**2)
    s_uu = sp.factor((d - 3) * t**2 + w)
    s_cu = sp.factor(-2 * t**3 + t**3 * (1 + 1 / p))
    assert s_cc == (d - 2) * t**2
    assert s_cu == -t**3 * (p - 1) / p

    H = sp.Matrix([[0, t], [t, 0]])
    D = sp.diag(t**2, t**2 / p)
    S = sp.Matrix([[s_cc, s_cu], [s_cu, s_uu]])
    base = 4 * (d - 1) * (d - 2)
    N = base * sp.eye(2) - 10 * (d - 2) * H + 8 * t**2 * sp.eye(2) + (3 * d - 14) * D + 2 * S / (d - 2)
    R = sp.Matrix([[1 + t, -t], [-t, 1 + t]]) / (1 + 2 * t)
    M = sp.simplify((d - 2) * N - 4 * (d - 1) * (d - 2) ** 2 * R)

    transverse_N = base + (3 * d - 14) * t**2 / p + 2 * w / (d - 2)
    transverse = sp.factor((d - 2) * transverse_N - 4 * (d - 1) * (d - 2) ** 2 / (1 + t))
    sectors = {
        "center": M[0, 0],
        "uniform": M[1, 1],
        "determinant": sp.factor(M.det()),
        "transverse": transverse,
    }
    expected_degrees = {"center": 3, "uniform": 5, "determinant": 7, "transverse": 5}
    regimes = {
        "p3": ({p: 3, d: 6 + h}, (h,)),
        "p4": ({p: 4, d: 6 + h}, (h,)),
        "p_ge_5": ({p: 5 + a, d: 6 + a + h}, (a, h)),
    }
    digest: dict[str, object] = {}
    for name, expression in sectors.items():
        den = sp.factor(sp.fraction(sp.factor(expression))[1])
        # The exact forms below are positive for p>=3 and 0<=t<=1.
        assert (name == "center" and den == 1 + 2 * t) or (
            name in {"uniform", "determinant"} and den == p**2 * (1 + 2 * t)
        ) or (name == "transverse" and den == p**2 * (1 + t))
        b = bernstein(expression, t)
        assert len(b) - 1 == expected_degrees[name]
        digest[name] = {
            "degree_t": len(b) - 1,
            "regimes": {
                regime: coefficient_sign_digest(
                    [sp.factor(value.subs(substitution)) for value in b], variables
                )
                for regime, (substitution, variables) in regimes.items()
            },
        }

    fixed = {p: 7, d: 12, t: sp.Rational(99, 100)}
    fixed_values = {name: str(sp.factor(value.subs(fixed))) for name, value in sectors.items()}
    assert all(sp.Rational(value) > 0 for value in fixed_values.values())

    print(json.dumps({
        "schema_version": "1.0",
        "verdict": "PASS",
        "scope": "all p>=3,d>=max(6,p+1), equal-magnitude K_(1,p) direct_sum isolates",
        "evidence_level": "E4 internal proof candidate after independent hostile reconstruction; no formal or external review",
        "sector_digest": digest,
        "fixed_p7_d12_values": fixed_values,
        "caveat": "Equal-magnitude star slice only, not arbitrary stars or unrestricted W4.",
    }, indent=2))


if __name__ == "__main__":
    main()
