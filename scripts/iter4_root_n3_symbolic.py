"""Symbolic n=3 boundary slice for the Iteration 4 matrix route.

This is an exploratory exact-algebra generator, not a general verifier. It
enumerates all six orderings for a generic 3x3 correlation matrix and then
restricts the corank-one Schur-complement gap to the rational stereographic
parametrization of three unit vectors in R^2.

For a null vector ``u``, nonnegativity of

    ||u||^2 - 2 u^T K(C)^(-1) u

is equivalent to ``K(C) >= 2 P_ker(C)`` when the nullity is one. Polynomial
substitution is done by denominator homogenization; naive nested rational
substitution causes a large, avoidable SymPy expansion.
"""

from __future__ import annotations

from itertools import permutations

import sympy as sp


def lower_triangle(matrix: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(
        matrix.rows,
        matrix.cols,
        lambda row, column: matrix[row, column] if row >= column else 0,
    )


def stereographic_numerator(
    polynomial: sp.Poly,
    p: sp.Symbol,
    q: sp.Symbol,
) -> tuple[sp.Expr, int, int]:
    """Clear the positive stereographic denominators of P(a,b,c)."""
    pa = 1 + p**2
    pb = 1 + q**2
    a_num = 1 - p**2
    b_num = 1 - q**2
    c_num = (1 - p**2) * (1 - q**2) + 4 * p * q
    terms = polynomial.terms()
    max_pa = max(a_power + c_power for (a_power, _, c_power), _ in terms)
    max_pb = max(b_power + c_power for (_, b_power, c_power), _ in terms)
    result = sp.Integer(0)
    for (a_power, b_power, c_power), coefficient in terms:
        result += (
            coefficient
            * a_num**a_power
            * b_num**b_power
            * c_num**c_power
            * pa ** (max_pa - a_power - c_power)
            * pb ** (max_pb - b_power - c_power)
        )
    return sp.expand(result), max_pa, max_pb


def main() -> None:
    a, b, c = sp.symbols("a b c", real=True)
    p, q = sp.symbols("p q", real=True)
    correlation = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])

    expected_inverse_gram = sp.zeros(3)
    for order in permutations(range(3)):
        permutation = sp.eye(3)[:, list(order)]
        permuted = permutation.T * correlation * permutation
        factor = permutation * lower_triangle(permuted) * permutation.T
        inverse = factor.inv()
        expected_inverse_gram += inverse.T * inverse
    expected_inverse_gram = sp.simplify(expected_inverse_gram / 6)

    # Cross product of the first two rows. It is a null vector exactly when
    # det(C)=0; the stereographic slice enforces that identity.
    null_vector = sp.Matrix([a * c - b, a * b - c, 1 - a**2])
    inverse_quadratic = (
        null_vector.T * expected_inverse_gram.inv() * null_vector
    )[0]
    generic_gap = sp.cancel(null_vector.dot(null_vector) - 2 * inverse_quadratic)
    generic_numerator, generic_denominator = sp.fraction(generic_gap)
    numerator, numerator_pa, numerator_pb = stereographic_numerator(
        sp.Poly(generic_numerator, a, b, c), p, q
    )
    denominator, denominator_pa, denominator_pb = stereographic_numerator(
        sp.Poly(generic_denominator, a, b, c), p, q
    )

    # The omitted factor is a product of powers of 1+p^2 and 1+q^2, hence
    # strictly positive on the real stereographic chart.
    print(
        "positive_denominator_exponent_shift=",
        denominator_pa - numerator_pa,
        denominator_pb - numerator_pb,
    )
    print("gap_numerator_factorization=")
    print(sp.factor(numerator))
    print("gap_denominator_factorization=")
    print(sp.factor(denominator))
    print("numerator_total_degree=", sp.Poly(numerator, p, q).total_degree())
    print("denominator_total_degree=", sp.Poly(denominator, p, q).total_degree())


if __name__ == "__main__":
    main()
