"""Independent dimension-parametric audit of the three-path W4 slice."""

from __future__ import annotations

import itertools
import json

import sympy as sp


def bernstein_flat(poly: sp.Expr, x: sp.Symbol, y: sp.Symbol) -> list[sp.Expr]:
    p = sp.Poly(sp.expand(poly), x, y)
    dx, dy = p.degree(x), p.degree(y)
    return [
        sp.factor(
            sum(
                p.coeff_monomial(x**aa * y**bb)
                * sp.binomial(i, aa)
                * sp.binomial(j, bb)
                / (sp.binomial(dx, aa) * sp.binomial(dy, bb))
                for aa in range(i + 1)
                for bb in range(j + 1)
            )
        )
        for i in range(dx + 1)
        for j in range(dy + 1)
    ]


def remove_t_valuation(poly: sp.Expr, t: sp.Symbol) -> tuple[int, sp.Expr]:
    p = sp.Poly(sp.expand(poly), t)
    valuation = min(monomial[0] for monomial, coefficient in p.terms() if coefficient != 0)
    reduced = sp.cancel(poly / t**valuation)
    assert sp.denom(reduced) == 1
    return valuation, sp.factor(reduced)


def main() -> None:
    q, t, k = sp.symbols("q t k", nonnegative=True)
    d = k + 6
    r, s = t * sp.sqrt(q), t * sp.sqrt(1 - q)
    H = sp.Matrix([[0, r, 0], [r, 0, s], [0, s, 0]])
    I = sp.eye(3)
    D = sp.diag(*[(H**2)[i, i] for i in range(3)])
    E = sp.diag(*[(H**3)[i, i] for i in range(3)])
    F = H + H**2 - D
    S = (
        (d - 3) * H**2
        - 2 * H**3
        + H * D
        + D * H
        + sp.diag(*[(F**2)[i, i] for i in range(3)])
    )
    N = (
        4 * (d - 1) * (d - 2) * I
        - 10 * (d - 2) * H
        + 8 * H**2
        + (3 * d - 14) * D
        - 4 * E
        + 2 * S / (d - 2)
    )
    C = I + H
    gap = N / (2 * d * (d - 1) * (d - 2)) - 2 * (C + t * I).inv() / d
    M = sp.simplify(gap * 2 * d * (d - 1) * (d - 2) ** 2)
    expected_M = sp.simplify(
        (d - 2) * N - 4 * (d - 1) * (d - 2) ** 2 * (C + t * I).inv()
    )
    assert all(sp.factor(value) == 0 for value in (M - expected_M))

    digest: dict[str, object] = {}
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(3), size):
            key = "".join(map(str, subset))
            det = sp.factor(M.extract(subset, subset).det())
            numerator, denominator = sp.fraction(det)
            denominator = sp.factor(denominator)
            base = (1 + 2 * t) * ((1 + t) if key != "1" else 1)
            constant = sp.factor(denominator / base)
            assert not constant.free_symbols and constant > 0
            pk = sp.Poly(sp.expand(numerator), k)
            summaries = []
            for power in range(pk.degree() + 1):
                coefficient = sp.factor(pk.coeff_monomial(k**power))
                valuation, reduced = remove_t_valuation(coefficient, t)
                coeffs = bernstein_flat(reduced, q, t)
                assert all(value >= 0 for value in coeffs)
                summaries.append({
                    "k_power": power,
                    "t_valuation": valuation,
                    "coefficient_count": len(coeffs),
                    "zero_count": sum(value == 0 for value in coeffs),
                    "minimum": str(min(coeffs)),
                })
            digest[key] = {"degree_k": pk.degree(), "coefficients": summaries}

    fixed = sp.simplify(M.subs({q: sp.Rational(9, 25), t: sp.Rational(2, 3), k: 5}))
    fixed_minors = [
        str(sp.factor(fixed.extract(subset, subset).det()))
        for size in (1, 2, 3)
        for subset in itertools.combinations(range(3), size)
    ]
    assert all(sp.Rational(value) > 0 for value in fixed_minors)

    print(json.dumps({
        "schema_version": "1.0",
        "verdict": "PASS",
        "scope": "all d>=6, weighted three-path direct_sum I_(d-3)",
        "evidence_level": "E4 internal proof candidate after independent hostile reconstruction; no formal or external review",
        "principal_minor_k_digest": digest,
        "fixed_d11_principal_minors": fixed_minors,
        "caveat": "Structured sparse slice only, not unrestricted W4.",
    }, indent=2))


if __name__ == "__main__":
    main()
