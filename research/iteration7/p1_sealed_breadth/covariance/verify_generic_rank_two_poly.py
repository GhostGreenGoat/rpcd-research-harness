#!/usr/bin/env python3
"""Exact sparse-polynomial reconstruction of the generic rank-two warm slice.

This is the optimized repair of verify_generic_rank_two_coeff.py.  All
matrix entries are coefficient tuples over fractions.Fraction; symbolic
polynomials are created only after the four scalar determinants are formed.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time

import sympy as sp


HERE = Path(__file__).resolve().parent
EPS = sp.Symbol("eps", real=True)
ZERO = (Fraction(0),)
ONE = (Fraction(1),)


def norm(poly: tuple[Fraction, ...] | list[Fraction]) -> tuple[Fraction, ...]:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def add(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    out = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        out[index] += value
    for index, value in enumerate(right):
        out[index] += value
    return norm(out)


def neg(poly: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(-value for value in poly)


def scale(poly: tuple[Fraction, ...], scalar: Fraction) -> tuple[Fraction, ...]:
    return norm(tuple(scalar * value for value in poly))


def multiply(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    if left == ZERO or right == ZERO:
        return ZERO
    out = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        if left_value:
            for j, right_value in enumerate(right):
                if right_value:
                    out[i + j] += left_value * right_value
    return norm(out)


Matrix = list[list[tuple[Fraction, ...]]]


def zero_matrix(rows: int, cols: int | None = None) -> Matrix:
    cols = rows if cols is None else cols
    return [[ZERO for _ in range(cols)] for _ in range(rows)]


def identity_matrix(size: int) -> Matrix:
    out = zero_matrix(size)
    for index in range(size):
        out[index][index] = ONE
    return out


def matrix_add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [add(left[row][col], right[row][col]) for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def matrix_scale(matrix: Matrix, scalar: Fraction) -> Matrix:
    return [[scale(value, scalar) for value in row] for row in matrix]


def matrix_transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    inner = len(right)
    cols = len(right[0])
    out = zero_matrix(rows, cols)
    for row in range(rows):
        for pivot in range(inner):
            left_value = left[row][pivot]
            if left_value == ZERO:
                continue
            for col in range(cols):
                right_value = right[pivot][col]
                if right_value != ZERO:
                    out[row][col] = add(out[row][col], multiply(left_value, right_value))
    return out


def determinant(matrix: Matrix, size: int) -> tuple[Fraction, ...]:
    out = ZERO
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = ONE
        for row, col in enumerate(permutation):
            term = multiply(term, matrix[row][col])
        out = add(out, neg(term) if inversions % 2 else term)
    return out


def to_sympy_poly(poly: tuple[Fraction, ...]) -> sp.Poly:
    dictionary = {
        (degree,): sp.Rational(value.numerator, value.denominator)
        for degree, value in enumerate(poly)
        if value
    }
    return sp.Poly.from_dict(dictionary, gens=(EPS,), domain=sp.QQ)


def evaluate(poly: tuple[Fraction, ...], value: Fraction) -> Fraction:
    output = Fraction(0)
    for coefficient in reversed(poly):
        output = output * value + coefficient
    return output


def rational_digest(value: Fraction) -> str:
    rendered = f"{value.numerator}/{value.denominator}".encode("ascii")
    return hashlib.sha256(rendered).hexdigest()


def endpoint_multiplicity(polynomial: sp.Poly, endpoint: int) -> tuple[int, sp.Poly]:
    divisor = sp.Poly(EPS - endpoint, EPS, domain=sp.QQ)
    quotient = polynomial
    multiplicity = 0
    while quotient.eval(endpoint) == 0:
        quotient, remainder = sp.div(quotient, divisor, domain=sp.QQ)
        assert remainder.is_zero
        multiplicity += 1
    return multiplicity, quotient


def bernstein_coefficients(polynomial: sp.Poly) -> list[sp.Rational]:
    degree = polynomial.degree()
    monomial = [polynomial.nth(index) for index in range(degree + 1)]
    return [
        sp.cancel(
            sum(
                monomial[index] * sp.binomial(level, index) / sp.binomial(degree, index)
                for index in range(level + 1)
            )
        )
        for level in range(degree + 1)
    ]


def split_bernstein_half(coefficients: list[sp.Rational]) -> tuple[list[sp.Rational], list[sp.Rational]]:
    levels = [coefficients]
    while len(levels[-1]) > 1:
        previous = levels[-1]
        levels.append([sp.cancel((previous[index] + previous[index + 1]) / 2) for index in range(len(previous) - 1)])
    left = [level[0] for level in levels]
    right = [levels[index][-1] for index in range(len(levels) - 1, -1, -1)]
    return left, right


def adaptive_bernstein_positive(polynomial: sp.Poly, max_depth: int = 16) -> dict[str, object]:
    initial = bernstein_coefficients(polynomial)
    stack: list[tuple[list[sp.Rational], int, int]] = [(initial, 0, 0)]
    leaves = []
    unresolved = []
    while stack:
        coefficients, depth, index = stack.pop()
        if all(value >= 0 for value in coefficients) and any(value > 0 for value in coefficients):
            rendered = ",".join(str(value) for value in coefficients).encode("ascii")
            leaves.append({
                "depth": depth,
                "dyadic_index": index,
                "minimum_coefficient": str(min(coefficients)),
                "coefficients_sha256": hashlib.sha256(rendered).hexdigest(),
            })
            continue
        if depth >= max_depth:
            unresolved.append({
                "depth": depth,
                "dyadic_index": index,
                "minimum_coefficient": str(min(coefficients)),
            })
            continue
        left, right = split_bernstein_half(coefficients)
        stack.append((right, depth + 1, 2 * index + 1))
        stack.append((left, depth + 1, 2 * index))
    return {
        "max_depth": max_depth,
        "accepted_leaf_count": len(leaves),
        "accepted_leaves": leaves,
        "unresolved_leaf_count": len(unresolved),
        "unresolved_leaves": unresolved,
        "positive_exact": not unresolved,
    }


def certificate(poly: tuple[Fraction, ...]) -> dict[str, object]:
    polynomial = to_sympy_poly(poly)
    multiplicity_zero, residual = endpoint_multiplicity(polynomial, 0)
    multiplicity_one, residual = endpoint_multiplicity(residual, 1)
    value_half = residual.eval(sp.Rational(1, 2))
    full_sign = (-1) ** multiplicity_one * sp.sign(value_half)
    denominator, integer_poly = residual.clear_denoms(convert=True)
    content, primitive = integer_poly.primitive()
    primitive_coefficients = [int(value) for value in primitive.all_coeffs()]
    rendered = ",".join(str(value) for value in primitive_coefficients).encode("ascii")
    signed_residual = sp.Poly(((-1) ** multiplicity_one) * residual.as_expr(), EPS, domain=sp.QQ)
    bernstein_certificate = adaptive_bernstein_positive(signed_residual)
    result = {
        "degree": polynomial.degree(),
        "multiplicity_at_zero": multiplicity_zero,
        "multiplicity_at_one": multiplicity_one,
        "residual_degree": residual.degree(),
        "residual_value_at_one_half": str(value_half),
        "sign_of_full_expression_on_open_0_1": int(full_sign),
        "primitive_content": str(content),
        "cleared_denominator": str(denominator),
        "primitive_coefficients_descending": [str(value) for value in primitive_coefficients],
        "primitive_coefficients_sha256": hashlib.sha256(rendered).hexdigest(),
        "residual_real_roots_in_open_0_1": None,
        "positive_on_open_0_1_exact": bernstein_certificate["positive_exact"],
        "adaptive_bernstein_certificate": bernstein_certificate,
        "nonnegative_on_open_0_1_by_even_square_factorization": False,
    }
    return result


def main() -> None:
    started = time.perf_counter()
    vectors = [
        (Fraction(1), Fraction(0)),
        (-Fraction(24, 25), Fraction(7, 25)),
        (-Fraction(35, 37), Fraction(12, 37)),
        (-Fraction(63, 65), Fraction(16, 65)),
    ]
    boundary = [
        [sum(x * y for x, y in zip(left, right)) for right in vectors]
        for left in vectors
    ]
    identity = identity_matrix(4)
    a = zero_matrix(4)
    for row in range(4):
        for col in range(4):
            delta = Fraction(row == col) - boundary[row][col]
            a[row][col] = norm((boundary[row][col], delta))

    updates: list[Matrix] = []
    for index in range(4):
        update = identity_matrix(4)
        for col in range(4):
            update[index][col] = add(update[index][col], neg(a[index][col]))
        updates.append(update)

    products: list[Matrix] = []
    for order in itertools.permutations(range(4)):
        product = identity_matrix(4)
        for index in order:
            product = matrix_multiply(updates[index], product)
        products.append(product)
    print({"stage": "products", "seconds": time.perf_counter() - started}, flush=True)

    h1 = zero_matrix(4)
    for product in products:
        term = matrix_multiply(matrix_transpose(product), matrix_multiply(a, product))
        h1 = matrix_add(h1, term)
    h1 = matrix_scale(h1, Fraction(1, 24))
    print({"stage": "H1", "seconds": time.perf_counter() - started}, flush=True)

    h2 = zero_matrix(4)
    for product in products:
        term = matrix_multiply(matrix_transpose(product), matrix_multiply(h1, product))
        h2 = matrix_add(h2, term)
    h2 = matrix_scale(h2, Fraction(1, 24))
    print({"stage": "H2", "seconds": time.perf_counter() - started}, flush=True)

    difference = zero_matrix(4)
    for row in range(4):
        for col in range(4):
            difference[row][col] = add(multiply((Fraction(1), -Fraction(1)), h1[row][col]), neg(h2[row][col]))

    certificates = []
    minors = []
    for size in range(1, 5):
        minor = determinant(difference, size)
        minors.append(minor)
        print({"stage": f"minor-{size}-coefficients", "degree": len(minor) - 1, "seconds": time.perf_counter() - started}, flush=True)
        certificates.append(certificate(minor))
        print({"stage": f"minor-{size}-certificate", "seconds": time.perf_counter() - started}, flush=True)
    all_positive = all(item["positive_on_open_0_1_exact"] for item in certificates)
    all_psd = all_positive
    specialization = Fraction(7, 10)
    specialization_digests = [rational_digest(evaluate(minor, specialization)) for minor in minors]
    inherited_direct_digests = [
        "f7f5b0811c242108122ce3d247a6e12261fad3a4b8662f4873670e9dadf0658d",
        "f614e67e1c3deeb0008a0777018ac5f683a45e452c7e0b36f29950c677ebbc18",
        "e2fc94ebaa1e182916a8519074d221672b04f9afbdcdc76424670328f02b4dfd",
        "8b5a9d4c04988180dfb35ac522416aeba7bc16e0258ee6ec9fdd93b05b90cc67",
    ]
    specialization_matches = specialization_digests == inherited_direct_digests

    commutator = matrix_add(
        matrix_multiply(updates[0], updates[1]),
        matrix_scale(matrix_multiply(updates[1], updates[0]), Fraction(-1)),
    )
    witness_poly = next(
        commutator[row][col]
        for row in range(4)
        for col in range(4)
        if commutator[row][col] != ZERO
    )
    witness = to_sympy_poly(witness_poly).as_expr()

    output = {
        "schema_version": "1.0",
        "task_id": "T143-sealed-finite-time-breadth",
        "run_id": "20260825T123453Z-6a1254f4",
        "kind": "exact sparse-polynomial generic signed rank-two warm attack",
        "arithmetic": "fractions.Fraction coefficient convolution plus exact SymPy Sturm root counts",
        "seed": None,
        "tolerance": "0",
        "family": "A_eps=eps I+(1-eps)Gram((1,0),(-24,7)/25,(-35,12)/37,(-63,16)/65)",
        "quantifier": "every real 0<eps<1",
        "boundary_rank": 2,
        "all_24_permutations_averaged": True,
        "coordinate_updates_noncommute": True,
        "coordinate_update_commutator_witness": str(sp.factor(witness)),
        "candidate": "H2 <= (1-eps)H1",
        "degree_bounds": {"epoch_product": 4, "H1": 9, "H2": 17, "difference": 17},
        "actual_degrees": {
            "H1": max(len(h1[row][col]) - 1 for row in range(4) for col in range(4)),
            "H2": max(len(h2[row][col]) - 1 for row in range(4) for col in range(4)),
            "difference": max(len(difference[row][col]) - 1 for row in range(4) for col in range(4)),
        },
        "leading_principal_minor_certificates": certificates,
        "all_leading_principal_minors_positive_on_open_0_1_exact": all_positive,
        "warm_difference_psd_on_open_0_1_exact": all_psd,
        "direct_numeric_formulation_crosscheck": {
            "epsilon": "7/10",
            "coefficient_polynomial_minor_digests": specialization_digests,
            "prior_direct_matrix_minor_digests": inherited_direct_digests,
            "all_four_match_exact": specialization_matches,
        },
        "elapsed_seconds": time.perf_counter() - started,
        "conclusion": (
            "Sylvester's criterion proves H2<(1-eps)H1 for every 0<eps<1 on this generic unequal signed rank-two family."
            if all_psd
            else "The generic unequal signed rank-two family defeats the proposed warm inequality; inspect the first nonpositive certificate."
        ),
        "scope": (
            "This is at most an E3 route-local analytic slice. It resolves the earlier symbolic timeout "
            "for the displayed family but does not prove the general warm inequality, the locked block "
            "lemma, C051, or C050."
        ),
    }
    output_path = HERE / "generic_rank_two_warm_exact.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "minor_summary": [
            {
                "degree": item["degree"],
                "m0": item["multiplicity_at_zero"],
                "m1": item["multiplicity_at_one"],
                "residual_degree": item["residual_degree"],
                "roots_0_1": item["residual_real_roots_in_open_0_1"],
                "sign": item["sign_of_full_expression_on_open_0_1"],
                "positive": item["positive_on_open_0_1_exact"],
                "nonnegative_by_even_square": item["nonnegative_on_open_0_1_by_even_square_factorization"],
            }
            for item in certificates
        ],
        "all_psd": all_psd,
        "elapsed_seconds": output["elapsed_seconds"],
    }, indent=2))
    if not all_psd or not specialization_matches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
