"""Exact checks for the Iteration-6 Route-L3 Schur compensation lemma.

This script is deliberately not a random search.  It checks the symbolic scalar
factorizations used in the proof draft and a short fixed list of rational Gram
families.  The finite checks are regression evidence; the universal claim rests
on the displayed algebra in ``research/iteration6/route_l3``.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import sympy as sp


Q = sp.Rational


def all_principal_minors_nonnegative(matrix: sp.Matrix) -> tuple[bool, sp.Expr]:
    """Exact finite PSD test by all principal minors (tiny matrices only)."""
    smallest = None
    size = matrix.rows
    for width in range(1, size + 1):
        for subset in itertools.combinations(range(size), width):
            value = sp.factor(matrix.extract(subset, subset).det())
            if value < 0:
                return False, value
            if smallest is None or value < smallest:
                smallest = value
    return True, sp.factor(smallest if smallest is not None else 0)


def scalar_factor_checks() -> dict[str, object]:
    lam, mu, d = sp.symbols("lambda mu d", positive=True)
    child_p = (
        (3 * d + 1) - 4 * lam + 2 * (lam - 1) ** 2 / (d - 1)
    ) / (2 * d * (d - 1))
    gap = sp.factor(child_p - 3 * mu / (2 * d * lam))
    rhs = 3 * (lam - mu) * (1 - mu) / (
        2 * d * lam * (lam + 1 - mu)
    )

    # Low spectral regime.  The first summand is nonnegative for
    # mu <= lambda <= 1 and d >= 2; the desired RHS is no larger than
    # the second summand.
    low_endpoint = sp.factor(gap.subs(mu, lam))
    expected_low = -(lam - 1) * (2 * d - lam - 1) / (
        d * (d - 1) ** 2
    )
    assert sp.factor(low_endpoint - expected_low) == 0
    low_increment = sp.factor(gap - low_endpoint)
    assert sp.factor(low_increment - 3 * (lam - mu) / (2 * d * lam)) == 0

    # High spectral regime for d >= 4.  This stronger comparison implies the
    # desired one because (lambda-mu)/(lambda+1-mu) <= 1.
    strong_high = sp.factor(gap - 3 * (1 - mu) / (2 * d * lam))
    high_quadratic = (
        2 * lam**2 - (4 * d - 2) * lam + 3 * (d - 1) ** 2
    )
    expected_high = (lam - 1) * high_quadratic / (
        2 * d * lam * (d - 1) ** 2
    )
    assert sp.factor(strong_high - expected_high) == 0
    vertex_value = sp.factor(high_quadratic.subs(lam, d - Q(1, 2)))
    assert sp.factor(vertex_value - (2 * d**2 - 8 * d + 5) / 2) == 0

    # Exceptional child dimension d=3.  Parameterize the whole feasible
    # strip by v=1-mu in [0,1] and
    # t=(lambda-mu)/(3(1-mu)) in [0,1].
    v, t = sp.symbols("v t", nonnegative=True)
    d3_gap = sp.factor((gap - rhs).subs({d: 3, mu: 1 - v, lam: 1 - v + 3 * v * t}))
    polynomial = (
        27 * t**3 * v**2
        - 18 * t**2 * v**2
        - 27 * t**2 * v
        + 3 * t * v**2
        + 6 * t * v
        + 6 * t
        + v
        + 4
    )
    assert sp.factor(d3_gap - v * polynomial / (12 * (1 + 3 * t * v))) == 0

    # Tensor Bernstein coefficients, degrees (3,2), ordered by t then v.
    expected_bernstein = [
        [Q(4), Q(9, 2), Q(5)],
        [Q(6), Q(15, 2), Q(10)],
        [Q(8), Q(6), Q(0)],
        [Q(10), Q(0), Q(2)],
    ]
    poly = sp.Poly(polynomial, t, v)
    reconstructed: list[list[sp.Expr]] = []
    for i in range(4):
        row = []
        for j in range(3):
            coefficient = 0
            for k in range(i + 1):
                for ell in range(j + 1):
                    power = poly.coeff_monomial(t**k * v**ell)
                    coefficient += (
                        power
                        * Q(sp.binomial(i, k), sp.binomial(3, k))
                        * Q(sp.binomial(j, ell), sp.binomial(2, ell))
                    )
            row.append(sp.factor(coefficient))
        reconstructed.append(row)
    assert reconstructed == expected_bernstein
    assert all(value >= 0 for row in reconstructed for value in row)

    # Parent dimension m=3 has child dimension d=2.  Full beta compensation
    # is false there, but two smaller compensators close the parent estimate.
    d2_gap = sp.factor(gap.subs(d, 2))
    feasible_lam = 1 - v + 2 * v * t

    # Low-mu branch: kappa=mu/2.  Its scalar inverse comparison has
    # coefficient kappa/mu=1/2.
    low_d2_rhs = Q(1, 2) * (lam - mu) * (1 - mu) / (
        lam * (lam + 1 - mu)
    )
    low_d2_parameterized = sp.factor(
        (d2_gap - low_d2_rhs).subs({mu: 1 - v, lam: feasible_lam})
    )
    low_d2_poly = (
        16 * t**4 * v**3
        - 24 * t**3 * v**3
        + 12 * t**2 * v**3
        - 4 * t**2 * v**2
        - 6 * t**2 * v
        - 2 * t * v**3
        + 4 * t * v**2
        + 6 * t * v
        - t
        - v**2
        - v
        + 2
    )
    assert sp.factor(
        low_d2_parameterized
        - v * low_d2_poly / (2 * (1 + 2 * t * v) * (1 - v + 2 * t * v))
    ) == 0
    expected_low_d2_bernstein = [
        [Q(2), Q(5, 3), Q(1), Q(0)],
        [Q(7, 4), Q(23, 12), Q(25, 12), Q(7, 4)],
        [Q(3, 2), Q(11, 6), Q(41, 18), Q(23, 6)],
        [Q(5, 4), Q(17, 12), Q(19, 12), Q(1, 4)],
        [Q(1), Q(2, 3), Q(0), Q(1)],
    ]
    low_poly = sp.Poly(low_d2_poly, t, v)
    low_reconstructed: list[list[sp.Expr]] = []
    for i in range(5):
        row = []
        for j in range(4):
            coefficient = 0
            for k in range(i + 1):
                for ell in range(j + 1):
                    coefficient += (
                        low_poly.coeff_monomial(t**k * v**ell)
                        * Q(sp.binomial(i, k), sp.binomial(4, k))
                        * Q(sp.binomial(j, ell), sp.binomial(3, ell))
                    )
            row.append(sp.factor(coefficient))
        low_reconstructed.append(row)
    assert low_reconstructed == expected_low_d2_bernstein
    assert all(value >= 0 for row in low_reconstructed for value in row)

    # High-mu branch: kappa=(5mu-2)/4 and w=3(1-mu) in [0,1].
    # After sign normalization the numerator has strictly nonnegative tensor
    # Bernstein coefficients.
    kappa_high = (5 * mu - 2) / 4
    high_d2_rhs = (kappa_high / mu) * (lam - mu) * (1 - mu) / (
        lam * (lam + 1 - mu)
    )
    w = sp.symbols("w", nonnegative=True)
    high_d2_parameterized = sp.factor(
        (d2_gap - high_d2_rhs).subs(
            {mu: 1 - w / 3, lam: 1 - w / 3 + 2 * w * t / 3}
        )
    )
    high_d2_positive_poly = -(
        16 * t**4 * w**4
        - 48 * t**4 * w**3
        - 24 * t**3 * w**4
        + 72 * t**3 * w**3
        + 12 * t**2 * w**4
        - 48 * t**2 * w**3
        - 18 * t**2 * w**2
        + 162 * t**2 * w
        - 2 * t * w**4
        + 18 * t * w**3
        - 9 * t * w**2
        - 162 * t * w
        + 81 * t
        - 3 * w**3
        + 81 * w
        - 162
    )
    assert sp.factor(
        high_d2_parameterized
        - w
        * high_d2_positive_poly
        / (18 * (3 - w) * (3 + 2 * t * w) * (3 - w + 2 * t * w))
    ) == 0
    expected_high_d2_bernstein = [
        [Q(162), Q(567, 4), Q(243, 2), Q(102), Q(84)],
        [Q(567, 4), Q(1053, 8), Q(975, 8), Q(897, 8), Q(205, 2)],
        [Q(243, 2), Q(459, 4), Q(437, 4), Q(211, 2), Q(103)],
        [Q(405, 4), Q(729, 8), Q(669, 8), Q(621, 8), Q(147, 2)],
        [Q(81), Q(243, 4), Q(45), Q(36), Q(34)],
    ]
    high_poly = sp.Poly(high_d2_positive_poly, t, w)
    high_reconstructed: list[list[sp.Expr]] = []
    for i in range(5):
        row = []
        for j in range(5):
            coefficient = 0
            for k in range(i + 1):
                for ell in range(j + 1):
                    coefficient += (
                        high_poly.coeff_monomial(t**k * w**ell)
                        * Q(sp.binomial(i, k), sp.binomial(4, k))
                        * Q(sp.binomial(j, ell), sp.binomial(4, ell))
                    )
            row.append(sp.factor(coefficient))
        high_reconstructed.append(row)
    assert high_reconstructed == expected_high_d2_bernstein
    assert all(value >= 0 for row in high_reconstructed for value in row)

    # Parent coefficient closures, checked as identities rather than samples.
    m = sp.symbols("m", integer=True, positive=True)
    beta_parent = 3 * mu / (2 * (m - 1))
    q_parent = Q(1, 2) / m - beta_parent / m
    general_parent_surplus = sp.factor(
        beta_parent - 2 * mu / m + mu * q_parent
    )
    assert sp.factor(
        general_parent_surplus
        - 3 * mu * (1 - mu) / (2 * m * (m - 1))
    ) == 0
    beta_three = 3 * mu / 4
    q_three = (2 - 3 * mu) / 12
    low_parent_closure = sp.factor(
        beta_three
        - 2 * mu / 3
        - (beta_three - mu / 2) * (1 - mu)
        + q_three * mu
    )
    high_parent_closure = sp.factor(
        beta_three
        - 2 * mu / 3
        - (beta_three - (5 * mu - 2) / 4) * (1 - mu)
        + q_three * (3 - 2 * mu)
    )
    assert low_parent_closure == 0
    assert high_parent_closure == 0

    return {
        "low_endpoint_factor": str(low_endpoint),
        "high_stronger_factor": str(strong_high),
        "high_quadratic_vertex_value": str(vertex_value),
        "d3_gap_parameterization": str(d3_gap),
        "d3_bernstein_coefficients": [
            [str(value) for value in row] for row in reconstructed
        ],
        "d2_low_mu_bernstein_coefficients": [
            [str(value) for value in row] for row in low_reconstructed
        ],
        "d2_high_mu_bernstein_coefficients": [
            [str(value) for value in row] for row in high_reconstructed
        ],
        "general_parent_surplus": str(general_parent_surplus),
        "m3_low_parent_closure": str(low_parent_closure),
        "m3_high_parent_closure": str(high_parent_closure),
    }


def p_child(matrix: sp.Matrix) -> sp.Matrix:
    d = matrix.rows
    identity = sp.eye(d)
    return sp.simplify(
        ((3 * d + 1) * identity - 4 * matrix + 2 * (matrix - identity) ** 2 / (d - 1))
        / (2 * d * (d - 1))
    )


def deletion_data(matrix: sp.Matrix, index: int) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    size = matrix.rows
    keep = [j for j in range(size) if j != index]
    child = matrix.extract(keep, keep)
    b = matrix.extract(keep, [index])
    lift = sp.zeros(size - 1, size)
    for local, original in enumerate(keep):
        lift[local, original] = 1
        lift[local, index] = -matrix[original, index]
    return child, b, lift


def l3_from_children(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    answer = sp.eye(size) / (2 * size)
    for index in range(size):
        child, _, lift = deletion_data(matrix, index)
        answer += lift.T * p_child(child) * lift / size
    return sp.simplify(answer)


def l3_from_b5(matrix: sp.Matrix) -> sp.Matrix:
    size = matrix.rows
    identity = sp.eye(size)
    h = matrix - identity
    diagonal_h2 = sp.diag(*[(h**2)[i, i] for i in range(size)])
    diagonal_h3 = sp.diag(*[(h**3)[i, i] for i in range(size)])
    lifted_square = sp.zeros(size)
    for index in range(size):
        child, _, lift = deletion_data(matrix, index)
        lifted_square += lift.T * (child - sp.eye(size - 1)) ** 2 * lift
    numerator = (
        4 * (size - 1) * (size - 2) * identity
        - 10 * (size - 2) * h
        + 8 * h**2
        + (3 * size - 14) * diagonal_h2
        - 4 * diagonal_h3
        + 2 * lifted_square / (size - 2)
    )
    return sp.simplify(numerator / (2 * size * (size - 1) * (size - 2)))


def gram(points: list[list[sp.Expr]]) -> sp.Matrix:
    vectors = [sp.Matrix(point) for point in points]
    return sp.Matrix([[sp.factor(x.dot(y)) for y in vectors] for x in vectors])


def rational_families() -> list[tuple[str, sp.Matrix, sp.Rational]]:
    families: list[tuple[str, sp.Matrix, sp.Rational]] = []

    base3 = gram(
        [
            [1, 0],
            [Q(3, 5), Q(4, 5)],
            [-Q(5, 13), Q(12, 13)],
        ]
    )
    mu = Q(1, 5)
    families.append(("rank2_rational_gram_m3_low_mu", mu * sp.eye(3) + (1 - mu) * base3, mu))
    mu = Q(4, 5)
    families.append(("rank2_rational_gram_m3_high_mu", mu * sp.eye(3) + (1 - mu) * base3, mu))

    mu = Q(1, 5)
    base = gram(
        [
            [1, 0],
            [0, 1],
            [Q(3, 5), Q(4, 5)],
            [-Q(5, 13), Q(12, 13)],
        ]
    )
    families.append(("rank2_rational_gram_m4", mu * sp.eye(4) + (1 - mu) * base, mu))

    mu = Q(1, 7)
    size = 5
    simplex = sp.Matrix(
        size,
        size,
        lambda i, j: 1 if i == j else -Q(1, size - 1),
    )
    families.append(("simplex_lift_m5", mu * sp.eye(size) + (1 - mu) * simplex, mu))

    mu = Q(2, 9)
    base = gram(
        [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [Q(3, 5), Q(4, 5), 0],
            [0, Q(5, 13), Q(12, 13)],
        ]
    )
    families.append(("rank3_rational_gram_m5", mu * sp.eye(5) + (1 - mu) * base, mu))
    return families


def finite_exact_checks() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for name, matrix, mu in rational_families():
        size = matrix.rows
        beta = 3 * mu / (2 * (size - 1))
        if size >= 4:
            kappa = beta
        elif mu <= Q(2, 3):
            kappa = mu / 2
        else:
            kappa = (5 * mu - 2) / 4
        inverse = matrix.inv()
        minimum_child_margin = None
        maximum_identity_residual = Q(0)
        for index in range(size):
            child, b, lift = deletion_data(matrix, index)
            c = child.inv() * b
            s = sp.factor(1 - (b.T * c)[0])
            child_gap = sp.simplify(
                p_child(child)
                - beta * child.inv()
                - kappa * c * c.T / s
            )
            passed, smallest = all_principal_minors_nonnegative(child_gap)
            assert passed
            if minimum_child_margin is None or smallest < minimum_child_margin:
                minimum_child_margin = smallest

            defect = sp.simplify(
                inverse
                - sp.eye(size)[:, index] * sp.eye(size)[index, :]
                - lift.T * child.inv() * lift
                - lift.T * c * c.T * lift / s
            )
            maximum_identity_residual = max(
                maximum_identity_residual,
                max(abs(sp.factor(value)) for value in defect),
            )
        assert maximum_identity_residual == 0

        l3 = l3_from_children(matrix)
        b5_residual = sp.simplify(l3 - l3_from_b5(matrix))
        assert all(value == 0 for value in b5_residual)
        target_gap = sp.simplify(l3 - 2 * mu * inverse / size)
        target_passed, target_smallest = all_principal_minors_nonnegative(target_gap)
        assert target_passed
        records.append(
            {
                "family": name,
                "size": size,
                "mu": str(mu),
                "kappa": str(kappa),
                "child_rank_one_compensation_all_principal_minors": "PASS",
                "smallest_child_principal_minor": str(minimum_child_margin),
                "block_inverse_identity_max_exact_residual": str(maximum_identity_residual),
                "child_formula_minus_B5_max_exact_residual": "0",
                "l3_target_all_principal_minors": "PASS",
                "smallest_target_principal_minor": str(target_smallest),
            }
        )
    return records


def anisotropic_residual_checks() -> list[dict[str, object]]:
    """Exact regression of the pair-difference identity in proof Section 2."""
    records: list[dict[str, object]] = []
    for name, matrix, _ in rational_families():
        size = matrix.rows
        h = matrix - sp.eye(size)
        diagonal_h2 = sp.diag(*[(h**2)[i, i] for i in range(size)])
        f = sp.simplify(h + h**2 - diagonal_h2)
        r = sp.simplify((size - 2) * h - h**2 + diagonal_h2)
        lifted_square = sp.zeros(size)
        for index in range(size):
            selector = sp.zeros(size)
            selector[index, index] = 1
            w_i = sp.simplify(h - selector * h - f * selector)
            lifted_square += w_i.T * w_i
        z_f = sp.simplify(
            sp.diag(*[(f**2)[i, i] for i in range(size)])
            - f**2 / (size - 1)
        )
        pair_sos = sp.zeros(size)
        for row in range(size):
            keep = [i for i in range(size) if i != row]
            for left, right in itertools.combinations(keep, 2):
                vector = sp.zeros(size, 1)
                vector[left] = f[row, left]
                vector[right] = -f[row, right]
                pair_sos += vector * vector.T / (size - 1)
        residual_one = sp.simplify(lifted_square - r**2 / (size - 1) - z_f)
        residual_two = sp.simplify(z_f - pair_sos)
        assert all(value == 0 for value in residual_one)
        assert all(value == 0 for value in residual_two)
        passed, smallest = all_principal_minors_nonnegative(z_f)
        assert passed
        records.append(
            {
                "family": name,
                "size": size,
                "S_minus_R2_equals_ZF_max_exact_residual": "0",
                "ZF_equals_pair_SOS_max_exact_residual": "0",
                "ZF_all_principal_minors": "PASS",
                "smallest_ZF_principal_minor": str(smallest),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration6/route_l3/evidence/SCHUR_COMPENSATION_EXACT.json"
        ),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E3 proof-candidate algebra plus E2 exact regressions",
        "scope": "Universal scalar algebra for child d>=3 plus the piecewise d=2 closure; fixed rational parent regressions for m=3,4,5.",
        "scalar_checks": scalar_factor_checks(),
        "anisotropic_residual_checks": anisotropic_residual_checks(),
        "finite_exact_checks": finite_exact_checks(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "PASS"}))


if __name__ == "__main__":
    main()
