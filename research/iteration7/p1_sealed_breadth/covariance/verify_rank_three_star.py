#!/usr/bin/env python3
"""Exact symbolic attack on a rank-three singular-boundary star family.

The family has three orthogonal leaves and a hub with unequal rational
couplings (36,24,23)/49.  The script tests the stronger one-epoch inequality
H1 <= (1-eps) A_eps by exact factorization and Bernstein coefficients.  A
successful check proves only this analytic slice of the locked route.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


HERE = Path(__file__).resolve().parent


def epoch_products(a: sp.Matrix) -> list[sp.Matrix]:
    n = a.rows
    identity = sp.eye(n)
    updates = [identity - identity[:, i] * a[i, :] for i in range(n)]
    products = []
    for order in itertools.permutations(range(n)):
        product = identity
        for index in order:
            product = updates[index] * product
        products.append(product)
    return products


def bernstein_coefficients(polynomial: sp.Expr, variable: sp.Symbol) -> list[sp.Expr]:
    polynomial = sp.Poly(sp.expand(polynomial), variable)
    degree = polynomial.degree()
    monomial = [polynomial.nth(j) for j in range(degree + 1)]
    return [
        sp.cancel(
            sum(
                monomial[j] * sp.binomial(k, j) / sp.binomial(degree, j)
                for j in range(k + 1)
            )
        )
        for k in range(degree + 1)
    ]


def main() -> None:
    eps = sp.Symbol("eps", real=True)
    u = [sp.Rational(36, 49), sp.Rational(24, 49), sp.Rational(23, 49)]
    boundary = sp.eye(4)
    for index, value in enumerate(u):
        boundary[index, 3] = value
        boundary[3, index] = value
    assert sp.cancel(sum(value**2 for value in u)) == 1
    assert boundary.det() == 0 and boundary.rank() == 3
    a = sp.simplify(eps * sp.eye(4) + (1 - eps) * boundary)
    products = epoch_products(a)
    identity = sp.eye(4)
    updates = [identity - identity[:, i] * a[i, :] for i in range(4)]
    update_commutator = sp.simplify(updates[0] * updates[3] - updates[3] * updates[0])
    nonzero_commutator_entries = [sp.factor(value) for value in update_commutator if value != 0]
    h1 = sp.simplify(sum((t.T * a * t for t in products), sp.zeros(4)) / len(products))
    difference = sp.simplify((1 - eps) * a - h1)
    minors = [sp.factor(difference[:k, :k].det()) for k in range(1, 5)]

    # Divide the manifestly nonnegative endpoint factors observed exactly.
    endpoint_factors = [
        1 - eps,
        (1 - eps) ** 2,
        (1 - eps) ** 3,
        eps**2 * (2 - eps) * (1 - eps) ** 4,
    ]
    residuals = [sp.factor(sp.cancel(m / f)) for m, f in zip(minors, endpoint_factors)]
    positive_scalars = []
    primitive_polynomials = []
    bernstein = []
    for residual in residuals:
        polynomial = sp.Poly(residual, eps)
        denominator = sp.ilcm(*[term.q for term in polynomial.all_coeffs()])
        integer_poly = sp.Poly(sp.expand(residual * denominator), eps)
        content, primitive = integer_poly.primitive()
        if content < 0:
            content = -content
            primitive = -primitive
        scalar = sp.Rational(content, denominator)
        coefficients = bernstein_coefficients(primitive.as_expr(), eps)
        positive_scalars.append(scalar)
        primitive_polynomials.append(primitive.as_expr())
        bernstein.append(coefficients)

    exact_eigen_polynomial = sp.factor(a.charpoly().as_expr())
    all_positive = all(
        scalar > 0 and all(coefficient > 0 for coefficient in coefficients)
        for scalar, coefficients in zip(positive_scalars, bernstein)
    )
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "exact analytic rank-three star slice",
        "arithmetic": "SymPy exact symbolic rational arithmetic",
        "seed": None,
        "tolerance": "0",
        "family": "A_eps=eps I+(1-eps)Gram(e1,e2,e3,(36e1+24e2+23e3)/49)",
        "quantifier": "every real 0<eps<1; eps=1 is a separate zero-map endpoint",
        "boundary_rank": boundary.rank(),
        "couplings": [str(value) for value in u],
        "couplings_squared_sum": str(sum(value**2 for value in u)),
        "characteristic_polynomial": str(exact_eigen_polynomial),
        "all_24_permutations_averaged": True,
        "coordinate_updates_noncommute": bool(nonzero_commutator_entries),
        "coordinate_update_commutator_witness": str(nonzero_commutator_entries[0]),
        "candidate": "H1 <= (1-eps)A_eps",
        "leading_principal_minors": [str(value) for value in minors],
        "endpoint_factors": [str(value) for value in endpoint_factors],
        "positive_scalars": [str(value) for value in positive_scalars],
        "primitive_residual_polynomials": [str(value) for value in primitive_polynomials],
        "bernstein_coefficients_on_0_1": [
            [str(value) for value in coefficients] for coefficients in bernstein
        ],
        "all_bernstein_coefficients_strictly_positive_exact": all_positive,
        "conclusion": (
            "Sylvester plus positive Bernstein coefficients proves H1<(1-eps)A_eps for 0<eps<1."
            if all_positive
            else "The proposed one-epoch slice proof failed; inspect the first nonpositive coefficient."
        ),
        "scope": (
            "If positive, this is an E3 proof draft only for the displayed rank-three family and its "
            "signed conjugates/direct sums. It does not prove the general warm inequality, locked block "
            "lemma, C051, or C050."
        ),
    }
    output_path = HERE / "rank_three_star_exact.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not all_positive:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
