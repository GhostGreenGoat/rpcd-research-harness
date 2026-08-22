"""Exact symbolic invariant reduction attempt for the n=3 corank-one slice.

The output is exploratory algebra.  A polynomial with mixed coefficients is
not a positivity certificate.
"""

from itertools import permutations

import sympy as sp


def main() -> None:
    a, b, c = sp.symbols("a b c", real=True)
    gram = sp.Matrix([[1, a, b], [a, 1, c], [b, c, 1]])
    k = sp.zeros(3)
    for order in permutations(range(3)):
        permutation = sp.eye(3)[:, list(order)]
        cp = permutation.T * gram * permutation
        lower = sp.Matrix(3, 3, lambda i, j: cp[i, j] if i >= j else 0)
        m = permutation * lower * permutation.T
        inverse = m.inv()
        k += inverse.T * inverse / 6
    u = sp.Matrix([a * c - b, a * b - c, 1 - a**2])
    gap = sp.cancel(u.dot(u) - 2 * (u.T * k.inv() * u)[0])
    numerator, denominator = sp.fraction(gap)
    determinant_relation = 1 + 2 * a * b * c - a**2 - b**2 - c**2
    # Reduce powers of c modulo det(C)=0.  This is only a normal form on the
    # algebraic hypersurface, not a sign certificate.
    numerator_reduced = sp.rem(
        sp.Poly(numerator, c, domain=sp.QQ.frac_field(a, b)),
        sp.Poly(determinant_relation, c, domain=sp.QQ.frac_field(a, b)),
    ).as_expr()
    denominator_reduced = sp.rem(
        sp.Poly(denominator, c, domain=sp.QQ.frac_field(a, b)),
        sp.Poly(determinant_relation, c, domain=sp.QQ.frac_field(a, b)),
    ).as_expr()
    print("generic_numerator_factor=")
    print(sp.factor(numerator))
    print("generic_denominator_factor=")
    print(sp.factor(denominator))
    print("det_reduced_numerator_factor=")
    print(sp.factor(numerator_reduced))
    print("det_reduced_denominator_factor=")
    print(sp.factor(denominator_reduced))


if __name__ == "__main__":
    main()
