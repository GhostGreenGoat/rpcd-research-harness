"""Symbolic all-leaf-count certificate for the equal-weight star slice."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def bernstein_coefficients(poly: sp.Expr, t: sp.Symbol) -> list[sp.Expr]:
    numerator = sp.fraction(sp.factor(poly))[0]
    expanded = sp.Poly(sp.expand(numerator), t)
    degree = expanded.degree()
    return [
        sp.factor(
            sum(
                expanded.coeff_monomial(t**j)
                * sp.binomial(i, j)
                / sp.binomial(degree, j)
                for j in range(i + 1)
            )
        )
        for i in range(degree + 1)
    ]


def nonnegative_power_coefficients(poly: sp.Expr, variables: tuple[sp.Symbol, ...]) -> bool:
    numerator, denominator = sp.fraction(sp.cancel(poly))
    numerator_poly = sp.Poly(sp.expand(numerator), *variables)
    denominator_poly = sp.Poly(sp.expand(denominator), *variables)
    denominator_coefficients = denominator_poly.coeffs()
    denominator_at_origin = denominator_poly.as_expr().subs(
        {variable: 0 for variable in variables}
    )
    return (
        all(value >= 0 for value in numerator_poly.coeffs())
        and all(value >= 0 for value in denominator_coefficients)
        and denominator_at_origin > 0
    )


def main() -> None:
    p, d, t, a, h = sp.symbols("p d t a h", nonnegative=True)
    base = 4 * (d - 1) * (d - 2)
    w = t**2 / p + (p - 1) * t**4 / p**2
    H = sp.Matrix([[0, t], [t, 0]])
    D = sp.diag(t**2, t**2 / p)
    S = sp.Matrix(
        [
            [(d - 2) * t**2, -t**3 * (p - 1) / p],
            [-t**3 * (p - 1) / p, (d - 3) * t**2 + w],
        ]
    )
    numerator_l3 = (
        base * sp.eye(2)
        - 10 * (d - 2) * H
        + 8 * t**2 * sp.eye(2)
        + (3 * d - 14) * D
        + 2 * S / (d - 2)
    )
    shifted_inverse = sp.Matrix([[1 + t, -t], [-t, 1 + t]]) / (1 + 2 * t)
    M = sp.simplify(
        (d - 2) * numerator_l3
        - 4 * (d - 1) * (d - 2) ** 2 * shifted_inverse
    )

    numerator_transverse = (
        base + (3 * d - 14) * t**2 / p + 2 * w / (d - 2)
    )
    transverse = sp.factor(
        (d - 2) * numerator_transverse
        - 4 * (d - 1) * (d - 2) ** 2 / (1 + t)
    )
    sectors = {
        "center_diagonal": M[0, 0],
        "uniform_leaf_diagonal": M[1, 1],
        "center_uniform_determinant": sp.factor(M.det()),
        "leaf_transverse": transverse,
    }
    substitutions = {
        "p3": ({p: 3, d: h + 6}, (h,)),
        "p4": ({p: 4, d: h + 6}, (h,)),
        "p_ge_5": ({p: a + 5, d: a + h + 6}, (a, h)),
    }

    output_sectors: dict[str, object] = {}
    for name, expression in sectors.items():
        denominator = sp.factor(sp.fraction(sp.factor(expression))[1])
        bernstein = bernstein_coefficients(expression, t)
        checks: dict[str, object] = {}
        for regime, (substitution, variables) in substitutions.items():
            expressions = [sp.factor(value.subs(substitution)) for value in bernstein]
            assert all(nonnegative_power_coefficients(value, variables) for value in expressions)
            checks[regime] = {
                "variables": [str(variable) for variable in variables],
                "bernstein_coefficients_after_substitution": [
                    str(value) for value in expressions
                ],
            }
        output_sectors[name] = {
            "denominator": str(denominator),
            "degree_t": len(bernstein) - 1,
            "regime_checks": checks,
        }

    result = {
        "schema_version": "1.0",
        "evidence_level": "E3 symbolic proof candidate",
        "verdict": "PASS",
        "scope": "all p>=3 and d>=max(6,p+1), equal-magnitude weighted star plus isolates",
        "sectors": output_sectors,
    }
    output = Path("research/iteration6/route_l3/evidence/W4_EQUAL_STAR_SYMBOLIC.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "scope": result["scope"],
                "degrees": {
                    name: value["degree_t"] for name, value in output_sectors.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
