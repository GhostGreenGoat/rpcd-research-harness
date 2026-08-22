"""Exact Bernstein certificate for the `d=6` three-path W4 slice."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def bernstein_table(poly: sp.Expr, x: sp.Symbol, y: sp.Symbol) -> list[list[sp.Expr]]:
    expanded = sp.Poly(sp.expand(poly), x, y)
    dx, dy = expanded.degree(x), expanded.degree(y)
    table: list[list[sp.Expr]] = []
    for i in range(dx + 1):
        row: list[sp.Expr] = []
        for j in range(dy + 1):
            value = 0
            for aa in range(i + 1):
                for bb in range(j + 1):
                    value += (
                        expanded.coeff_monomial(x**aa * y**bb)
                        * sp.binomial(i, aa)
                        / sp.binomial(dx, aa)
                        * sp.binomial(j, bb)
                        / sp.binomial(dy, bb)
                    )
            row.append(sp.factor(value))
        table.append(row)
    return table


def main() -> None:
    q, t = sp.symbols("q t", nonnegative=True)
    r = t * sp.sqrt(q)
    s = t * sp.sqrt(1 - q)
    d = 6
    path_h = sp.Matrix([[0, r, 0], [r, 0, s], [0, s, 0]])
    H = sp.diag(path_h, sp.zeros(3))
    I = sp.eye(d)
    D = sp.diag(*[(H**2)[i, i] for i in range(d)])
    E = sp.diag(*[(H**3)[i, i] for i in range(d)])
    F = H + H**2 - D
    S = (
        (d - 3) * H**2
        - 2 * H**3
        + H * D
        + D * H
        + sp.diag(*[(F**2)[i, i] for i in range(d)])
    )
    L3 = (
        4 * (d - 1) * (d - 2) * I
        - 10 * (d - 2) * H
        + 8 * H**2
        + (3 * d - 14) * D
        - 4 * E
        + 2 * S / (d - 2)
    ) / (2 * d * (d - 1) * (d - 2))
    C = I + H
    gap = sp.simplify(L3 - sp.Rational(1, 3) * (C + t * I).inv())
    active = gap[:3, :3]

    expected_denominators = {
        "0": 480 * (t + 1) * (2 * t + 1),
        "1": 120 * (2 * t + 1),
        "2": 480 * (t + 1) * (2 * t + 1),
        "01": 230400 * (t + 1) * (2 * t + 1),
        "02": 230400 * (t + 1) * (2 * t + 1),
        "12": 230400 * (t + 1) * (2 * t + 1),
        "012": 110592000 * (t + 1) * (2 * t + 1),
    }
    certificates: dict[str, object] = {}
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(3), size):
            determinant = sp.factor(active.extract(subset, subset).det())
            numerator, denominator = sp.fraction(determinant)
            assert not numerator.has(sp.sqrt(q))
            assert not numerator.has(sp.sqrt(1 - q))
            table = bernstein_table(numerator, q, t)
            coefficients = [value for row in table for value in row]
            assert all(value >= 0 for value in coefficients)
            # The reconstructed denominators have only positive constant and
            # (1+t),(1+2t) factors on the unit square.
            normalized_denominator = sp.factor(denominator)
            key = "".join(str(i) for i in subset)
            assert sp.factor(normalized_denominator - expected_denominators[key]) == 0
            certificates[key] = {
                "subset": list(subset),
                "denominator": str(normalized_denominator),
                "degrees_q_t": [len(table) - 1, len(table[0]) - 1],
                "bernstein_coefficients": [
                    [str(value) for value in row] for row in table
                ],
                "coefficient_count": len(coefficients),
                "zero_count": sum(value == 0 for value in coefficients),
            }

    isolated_gap = sp.factor(
        gap[3, 3]
    )
    assert sp.factor(isolated_gap - t / (3 * (1 + t))) == 0

    result = {
        "schema_version": "1.0",
        "evidence_level": "E3 exact Bernstein proof candidate",
        "verdict": "PASS",
        "scope": "d=6, weighted three-vertex path plus three isolated coordinates",
        "hardest_mu": "1-t",
        "isolated_gap": str(isolated_gap),
        "principal_minor_certificates": certificates,
    }
    output = Path("research/iteration6/route_l3/evidence/W4_THREE_PATH_D6_EXACT.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "scope": result["scope"],
                "subsets": list(certificates),
                "isolated_gap": result["isolated_gap"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
