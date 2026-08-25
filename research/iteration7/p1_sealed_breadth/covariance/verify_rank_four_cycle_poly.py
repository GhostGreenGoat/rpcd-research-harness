#!/usr/bin/env python3
"""Exact all-epsilon warm-inequality attack on a rank-four signed cycle.

The singular boundary is the Gram matrix of five rational unit vectors in
R^4.  The displayed five-cycle has negative edge-sign product, so diagonal
sign conjugacy cannot make every cycle edge positive.  We average all 120
epoch permutations and certify (or reject) the leading principal minors of
(1-eps)H1-H2 using exact coefficient convolution and Bernstein positivity.
"""

from __future__ import annotations

from fractions import Fraction
import itertools
import json
from pathlib import Path
import time

import sympy as sp

from verify_generic_rank_two_poly import (
    EPS,
    ZERO,
    add,
    certificate,
    determinant,
    evaluate,
    identity_matrix,
    matrix_add,
    matrix_multiply,
    matrix_scale,
    matrix_transpose,
    multiply,
    neg,
    norm,
    rational_digest,
    to_sympy_poly,
    zero_matrix,
)


HERE = Path(__file__).resolve().parent


def main() -> None:
    started = time.perf_counter()
    vectors = [
        (Fraction(1), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(3, 5), Fraction(4, 5), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(5, 13), Fraction(12, 13), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(7, 25), Fraction(24, 25)),
        (Fraction(8, 17), Fraction(0), Fraction(0), -Fraction(15, 17)),
    ]
    assert all(sum(value * value for value in vector) == 1 for vector in vectors)
    size = len(vectors)
    boundary = [
        [sum(x * y for x, y in zip(left, right)) for right in vectors]
        for left in vectors
    ]
    boundary_sympy = sp.Matrix(
        [[sp.Rational(value.numerator, value.denominator) for value in row] for row in boundary]
    )
    assert boundary_sympy.rank() == 4 and boundary_sympy.det() == 0
    cycle_edges = [boundary[0][1], boundary[1][2], boundary[2][3], boundary[3][4], boundary[4][0]]
    cycle_sign_product = sp.prod(
        sp.Rational(value.numerator, value.denominator) for value in cycle_edges
    )
    assert cycle_sign_product < 0

    identity = identity_matrix(size)
    a = zero_matrix(size)
    for row in range(size):
        for col in range(size):
            delta = Fraction(row == col) - boundary[row][col]
            a[row][col] = norm((boundary[row][col], delta))

    updates = []
    for index in range(size):
        update = identity_matrix(size)
        for col in range(size):
            update[index][col] = add(update[index][col], neg(a[index][col]))
        updates.append(update)

    products = []
    for order in itertools.permutations(range(size)):
        product = identity_matrix(size)
        for index in order:
            product = matrix_multiply(updates[index], product)
        products.append(product)
    print({"stage": "products", "count": len(products), "seconds": time.perf_counter() - started}, flush=True)

    h1 = zero_matrix(size)
    for product in products:
        h1 = matrix_add(
            h1,
            matrix_multiply(matrix_transpose(product), matrix_multiply(a, product)),
        )
    h1 = matrix_scale(h1, Fraction(1, len(products)))
    print({"stage": "H1", "seconds": time.perf_counter() - started}, flush=True)

    h2 = zero_matrix(size)
    for product in products:
        h2 = matrix_add(
            h2,
            matrix_multiply(matrix_transpose(product), matrix_multiply(h1, product)),
        )
    h2 = matrix_scale(h2, Fraction(1, len(products)))
    print({"stage": "H2", "seconds": time.perf_counter() - started}, flush=True)

    difference = zero_matrix(size)
    for row in range(size):
        for col in range(size):
            difference[row][col] = add(
                multiply((Fraction(1), -Fraction(1)), h1[row][col]),
                neg(h2[row][col]),
            )

    certificates = []
    minors = []
    for principal_size in range(1, size + 1):
        minor = determinant(difference, principal_size)
        minors.append(minor)
        print({
            "stage": f"minor-{principal_size}-coefficients",
            "degree": len(minor) - 1,
            "seconds": time.perf_counter() - started,
        }, flush=True)
        certificates.append(certificate(minor))
        print({
            "stage": f"minor-{principal_size}-certificate",
            "positive": certificates[-1]["positive_on_open_0_1_exact"],
            "leaves": certificates[-1]["adaptive_bernstein_certificate"]["accepted_leaf_count"],
            "unresolved": certificates[-1]["adaptive_bernstein_certificate"]["unresolved_leaf_count"],
            "seconds": time.perf_counter() - started,
        }, flush=True)

    all_positive = all(item["positive_on_open_0_1_exact"] for item in certificates)

    # Independent direct rational-matrix specialization checks orientation and
    # the coefficient engine at eps=1/2.
    specialization = sp.Rational(1, 2)
    a_direct = specialization * sp.eye(size) + (1 - specialization) * boundary_sympy
    direct_updates = [
        sp.eye(size) - sp.eye(size)[:, index] * a_direct[index, :]
        for index in range(size)
    ]
    direct_products = []
    for order in itertools.permutations(range(size)):
        product = sp.eye(size)
        for index in order:
            product = direct_updates[index] * product
        direct_products.append(product)
    h1_direct = sum(
        (product.T * a_direct * product for product in direct_products),
        sp.zeros(size),
    ) / len(direct_products)
    h2_direct = sum(
        (product.T * h1_direct * product for product in direct_products),
        sp.zeros(size),
    ) / len(direct_products)
    difference_direct = (1 - specialization) * h1_direct - h2_direct
    direct_minors = [sp.cancel(difference_direct[:k, :k].det()) for k in range(1, size + 1)]
    coefficient_values = [evaluate(minor, Fraction(1, 2)) for minor in minors]
    direct_values = [
        Fraction(int(value.p), int(value.q))
        for value in direct_minors
    ]
    specialization_matches = coefficient_values == direct_values
    commutator = matrix_add(
        matrix_multiply(updates[0], updates[1]),
        matrix_scale(matrix_multiply(updates[1], updates[0]), Fraction(-1)),
    )
    witness_poly = next(
        commutator[row][col]
        for row in range(size)
        for col in range(size)
        if commutator[row][col] != ZERO
    )

    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "exact all-epsilon rank-four sign-frustrated-cycle warm attack",
        "arithmetic": "fractions.Fraction coefficient convolution plus exact adaptive Bernstein certificates",
        "seed": None,
        "tolerance": "0",
        "family": "A_eps=eps I+(1-eps)Gram(e1,(3e1+4e2)/5,(5e2+12e3)/13,(7e3+24e4)/25,(8e1-15e4)/17)",
        "quantifier": "every real 0<eps<1",
        "boundary_rank": 4,
        "all_120_permutations_averaged": True,
        "cycle_edges": [str(value) for value in cycle_edges],
        "cycle_edge_product": str(cycle_sign_product),
        "cycle_is_sign_frustrated": True,
        "coordinate_updates_noncommute": True,
        "coordinate_update_commutator_witness": str(sp.factor(to_sympy_poly(witness_poly).as_expr())),
        "candidate": "H2 <= (1-eps)H1",
        "actual_degrees": {
            "H1": max(len(h1[row][col]) - 1 for row in range(size) for col in range(size)),
            "H2": max(len(h2[row][col]) - 1 for row in range(size) for col in range(size)),
            "difference": max(len(difference[row][col]) - 1 for row in range(size) for col in range(size)),
        },
        "leading_principal_minor_certificates": certificates,
        "all_leading_principal_minors_positive_on_open_0_1_exact": all_positive,
        "direct_rational_matrix_crosscheck": {
            "epsilon": "1/2",
            "coefficient_polynomial_minor_digests": [rational_digest(value) for value in coefficient_values],
            "direct_matrix_minor_digests": [rational_digest(value) for value in direct_values],
            "all_five_match_exact": specialization_matches,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "conclusion": (
            "Sylvester's criterion proves H2<(1-eps)H1 on this rank-four sign-frustrated cycle for every 0<eps<1."
            if all_positive
            else "The direct Bernstein certificate does not close this family; unresolved leaves are retained and no sign conclusion is claimed."
        ),
        "scope": (
            "A positive result is at most an E3 route-local analytic slice; an unresolved Bernstein "
            "leaf is a failed certificate, not a counterexample. This artifact does not prove the "
            "general warm inequality, locked block lemma, C051, or C050."
        ),
    }
    output_path = HERE / "rank_four_cycle_warm_exact.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "all_positive": all_positive,
        "elapsed_seconds": output["elapsed_seconds"],
        "summaries": [
            {
                "degree": item["degree"],
                "m0": item["multiplicity_at_zero"],
                "m1": item["multiplicity_at_one"],
                "positive": item["positive_on_open_0_1_exact"],
                "leaf_count": item["adaptive_bernstein_certificate"]["accepted_leaf_count"],
                "unresolved": item["adaptive_bernstein_certificate"]["unresolved_leaf_count"],
            }
            for item in certificates
        ],
    }, indent=2))
    if not all_positive or not specialization_matches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
