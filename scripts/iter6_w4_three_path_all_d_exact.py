"""Dimension-parametric exact certificate for the weighted three-path slice."""

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


def strip_t_power(poly: sp.Expr, t: sp.Symbol) -> tuple[int, sp.Expr]:
    power = 0
    reduced = sp.factor(poly)
    while reduced != 0 and sp.factor(reduced.subs(t, 0)) == 0:
        reduced = sp.factor(reduced / t)
        power += 1
    return power, reduced


def main() -> None:
    q, t, k = sp.symbols("q t k", nonnegative=True)
    d = k + 6
    r = t * sp.sqrt(q)
    s = t * sp.sqrt(1 - q)
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
    numerator_l3 = (
        4 * (d - 1) * (d - 2) * I
        - 10 * (d - 2) * H
        + 8 * H**2
        + (3 * d - 14) * D
        - 4 * E
        + 2 * S / (d - 2)
    )
    C = I + H
    scaled_gap = sp.simplify(
        (d - 2) * numerator_l3
        - 4 * (d - 1) * (d - 2) ** 2 * (C + t * I).inv()
    )

    certificates: dict[str, object] = {}
    for size in (1, 2, 3):
        for subset in itertools.combinations(range(3), size):
            determinant = sp.factor(scaled_gap.extract(subset, subset).det())
            numerator, denominator = sp.fraction(determinant)
            assert not numerator.has(sp.sqrt(q))
            assert not numerator.has(sp.sqrt(1 - q))
            denominator = sp.factor(denominator)
            # These are precisely the only denominators left after the
            # positive dimension scaling in (U3).
            assert sp.factor(denominator / ((1 + t) * (1 + 2 * t))).is_number or sp.factor(
                denominator / (1 + 2 * t)
            ).is_number

            polynomial_k = sp.Poly(sp.expand(numerator), k)
            coefficient_certificates: list[dict[str, object]] = []
            for power in range(polynomial_k.degree() + 1):
                coefficient = sp.factor(polynomial_k.coeff_monomial(k**power))
                t_power, reduced = strip_t_power(coefficient, t)
                table = bernstein_table(reduced, q, t)
                flat = [value for row in table for value in row]
                assert all(value >= 0 for value in flat)
                assert sp.factor(coefficient - t**t_power * reduced) == 0
                coefficient_certificates.append(
                    {
                        "k_power": power,
                        "t_power_stripped": t_power,
                        "degrees_q_t": [len(table) - 1, len(table[0]) - 1],
                        "bernstein_coefficients": [
                            [str(value) for value in row] for row in table
                        ],
                        "coefficient_count": len(flat),
                        "zero_count": sum(value == 0 for value in flat),
                    }
                )

            key = "".join(str(i) for i in subset)
            certificates[key] = {
                "subset": list(subset),
                "denominator": str(denominator),
                "degree_k": polynomial_k.degree(),
                "k_coefficients": coefficient_certificates,
            }

    result = {
        "schema_version": "1.0",
        "evidence_level": "E3 exact dimension-parametric Bernstein proof candidate",
        "verdict": "PASS",
        "scope": "all d>=6, weighted three-vertex path plus d-3 isolates",
        "dimension_parameter": "k=d-6>=0",
        "hardest_mu": "1-t",
        "isolated_gap": "2*t/[d*(1+t)]",
        "principal_minor_certificates": certificates,
    }
    output = Path("research/iteration6/route_l3/evidence/W4_THREE_PATH_ALL_D_EXACT.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "scope": result["scope"],
                "k_degrees": {
                    key: value["degree_k"] for key, value in certificates.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
