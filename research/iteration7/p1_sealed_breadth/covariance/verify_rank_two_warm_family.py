#!/usr/bin/env python3
"""Exact all-parameter test of the warm inequality on a signed rank-two family.

For a fixed rational rank-two correlation boundary C and
A_eps=eps I+(1-eps)C, compute H1 and H2 by averaging all 24 epoch
permutations.  Positivity of (1-eps)H1-H2 is certified by exact factorization
of leading principal minors and Sturm root counts of their residual factors.
This is a route-local analytic slice, not a general theorem.
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


def endpoint_multiplicity(polynomial: sp.Poly, endpoint: int) -> int:
    variable = polynomial.gens[0]
    divisor = sp.Poly(variable - endpoint, variable)
    multiplicity = 0
    quotient = polynomial
    while quotient.eval(endpoint) == 0:
        quotient, remainder = sp.div(quotient, divisor)
        assert remainder.is_zero
        multiplicity += 1
    return multiplicity


def certify_positive_on_open_unit_interval(expression: sp.Expr, eps: sp.Symbol) -> dict[str, object]:
    polynomial = sp.Poly(sp.cancel(expression), eps)
    multiplicity_zero = endpoint_multiplicity(polynomial, 0)
    multiplicity_one = endpoint_multiplicity(polynomial, 1)
    residual = sp.Poly(
        sp.cancel(polynomial.as_expr() / (eps**multiplicity_zero * (eps - 1) ** multiplicity_one)),
        eps,
    )
    roots_open = int(residual.count_roots(sp.Rational(0), sp.Rational(1)))
    value_half = sp.cancel(residual.eval(sp.Rational(1, 2)))
    endpoint_factor_sign = (-1) ** multiplicity_one
    total_sign_at_half = endpoint_factor_sign * sp.sign(value_half)
    certified = roots_open == 0 and total_sign_at_half > 0
    return {
        "degree": polynomial.degree(),
        "multiplicity_at_zero": multiplicity_zero,
        "multiplicity_at_one": multiplicity_one,
        "residual_degree": residual.degree(),
        "residual_real_roots_in_open_0_1": roots_open,
        "residual_value_at_one_half": str(value_half),
        "sign_of_full_expression_on_open_0_1": int(total_sign_at_half),
        "positive_on_open_0_1_exact": bool(certified),
        "factored_expression": str(sp.factor(expression)),
    }


def main() -> None:
    eps = sp.Symbol("eps", real=True)
    vectors = [
        sp.Matrix([1, 0]),
        sp.Matrix([0, 1]),
        sp.Matrix([sp.Rational(3, 5), sp.Rational(4, 5)]),
        sp.Matrix([sp.Rational(4, 5), -sp.Rational(3, 5)]),
    ]
    boundary = sp.Matrix([[left.dot(right) for right in vectors] for left in vectors])
    assert boundary.rank() == 2
    a = sp.simplify(eps * sp.eye(4) + (1 - eps) * boundary)
    products = epoch_products(a)
    h1 = sp.simplify(sum((t.T * a * t for t in products), sp.zeros(4)) / len(products))
    h2 = sp.simplify(sum((t.T * h1 * t for t in products), sp.zeros(4)) / len(products))
    difference = sp.simplify((1 - eps) * h1 - h2)
    minors = [sp.factor(difference[:k, :k].det()) for k in range(1, 5)]
    certificates = [certify_positive_on_open_unit_interval(minor, eps) for minor in minors]

    identity = sp.eye(4)
    updates = [identity - identity[:, i] * a[i, :] for i in range(4)]
    commutator = sp.simplify(updates[0] * updates[2] - updates[2] * updates[0])
    commutator_witnesses = [sp.factor(value) for value in commutator if value != 0]
    all_positive = all(item["positive_on_open_0_1_exact"] for item in certificates)
    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "exact analytic signed rank-two warm slice",
        "arithmetic": "SymPy exact rational polynomial arithmetic and Sturm root counts",
        "seed": None,
        "tolerance": "0",
        "family": "A_eps=eps I+(1-eps)Gram((1,0),(0,1),(3,4)/5,(4,-3)/5)",
        "quantifier": "every real 0<eps<1",
        "boundary_rank": boundary.rank(),
        "characteristic_polynomial": str(sp.factor(a.charpoly().as_expr())),
        "all_24_permutations_averaged": True,
        "coordinate_updates_noncommute": bool(commutator_witnesses),
        "coordinate_update_commutator_witness": str(commutator_witnesses[0]),
        "candidate": "H2 <= (1-eps)H1",
        "leading_principal_minor_certificates": certificates,
        "all_leading_principal_minors_positive_on_open_0_1_exact": all_positive,
        "conclusion": (
            "Sylvester's criterion proves H2<(1-eps)H1 for every 0<eps<1 on this family."
            if all_positive
            else "The direct all-epsilon proof attempt failed; the first nonpositive minor is recorded."
        ),
        "scope": (
            "This is at most an E3 proof draft for the displayed family and signed conjugates/direct "
            "sums. It does not prove the general warm inequality, the locked block lemma, C051, or C050."
        ),
    }
    output_path = HERE / "rank_two_warm_exact.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not all_positive:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
