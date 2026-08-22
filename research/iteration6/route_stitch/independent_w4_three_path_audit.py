"""Independent exact audit for the d=6 three-vertex-path W4 slice."""

from __future__ import annotations

import itertools
import json

import sympy as sp


def bernstein_coefficients(poly: sp.Expr, x: sp.Symbol, y: sp.Symbol) -> list[sp.Expr]:
    power = sp.Poly(sp.expand(poly), x, y)
    dx, dy = power.degree(x), power.degree(y)
    out: list[sp.Expr] = []
    for i in range(dx + 1):
        for j in range(dy + 1):
            out.append(
                sp.factor(
                    sum(
                        power.coeff_monomial(x**aa * y**bb)
                        * sp.binomial(i, aa)
                        * sp.binomial(j, bb)
                        / (sp.binomial(dx, aa) * sp.binomial(dy, bb))
                        for aa in range(i + 1)
                        for bb in range(j + 1)
                    )
                )
            )
    return out


def main() -> None:
    q, t = sp.symbols("q t", nonnegative=True)
    r, s = t * sp.sqrt(q), t * sp.sqrt(1 - q)
    h3 = sp.Matrix([[0, r, 0], [r, 0, s], [0, s, 0]])
    spectral = h3.charpoly()
    z = spectral.gen
    assert sp.factor(spectral.as_expr() - z * (z - t) * (z + t)) == 0

    dim = 6
    H = sp.diag(h3, sp.zeros(3))
    I = sp.eye(dim)
    D = sp.diag(*[(H**2)[i, i] for i in range(dim)])
    E = sp.diag(*[(H**3)[i, i] for i in range(dim)])
    F = H + H**2 - D
    S = (
        3 * H**2
        - 2 * H**3
        + H * D
        + D * H
        + sp.diag(*[(F**2)[i, i] for i in range(dim)])
    )
    L3 = (
        80 * I - 40 * H + 8 * H**2 + 4 * D - 4 * E + S / 2
    ) / 240
    C = I + H
    gap = sp.simplify(L3 - (C + t * I).inv() / 3)
    active = gap[:3, :3]

    expected_denominators = {
        "0": 480 * (1 + t) * (1 + 2 * t),
        "1": 120 * (1 + 2 * t),
        "2": 480 * (1 + t) * (1 + 2 * t),
        "01": 230400 * (1 + t) * (1 + 2 * t),
        "02": 230400 * (1 + t) * (1 + 2 * t),
        "12": 230400 * (1 + t) * (1 + 2 * t),
        "012": 110592000 * (1 + t) * (1 + 2 * t),
    }
    digest: dict[str, object] = {}
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(3), size):
            key = "".join(map(str, subset))
            det = sp.factor(active.extract(subset, subset).det())
            num, den = sp.fraction(det)
            assert sp.factor(den - expected_denominators[key]) == 0
            assert not num.has(sp.sqrt(q), sp.sqrt(1 - q))
            coeffs = bernstein_coefficients(num, q, t)
            assert all(c >= 0 for c in coeffs)
            positive = [c for c in coeffs if c > 0]
            digest[key] = {
                "coefficient_count": len(coeffs),
                "zero_count": sum(c == 0 for c in coeffs),
                "minimum_positive_coefficient": str(min(positive)),
                "denominator": str(den),
            }

    assert sp.factor(gap[3, 3] - t / (3 * (1 + t))) == 0
    # Rational interior control: t=2/3, (sqrt(q),sqrt(1-q))=(3/5,4/5).
    fixed = sp.simplify(active.subs({q: sp.Rational(9, 25), t: sp.Rational(2, 3)}))
    fixed_minors = []
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(3), size):
            value = sp.factor(fixed.extract(subset, subset).det())
            assert value >= 0
            fixed_minors.append(str(value))

    print(
        json.dumps(
            {
                "schema_version": "1.0",
                "verdict": "PASS",
                "scope": "d=6, three-vertex path direct_sum I_3",
                "evidence_level": "E4 internal proof candidate after independent hostile reconstruction; no formal or external review",
                "seven_principal_minor_digest": digest,
                "fixed_rational_principal_minors": fixed_minors,
                "caveat": "Sparse d=6 slice only; no dimension-uniform or general W4 claim.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
