"""Exact rational checks for Iteration-4 task T085.

This script is deliberately dependency-free.  It verifies finite algebraic
identities with ``fractions.Fraction``; its output is an E3 finite certificate,
not a proof of any quantified statement beyond the displayed finite cases.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path


def eye(n: int):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def zeros(rows: int, cols: int):
    return [[F(0) for _ in range(cols)] for _ in range(rows)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b):
    return [[x + y for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def subtract(a, b):
    return [[x - y for x, y in zip(rx, ry)] for rx, ry in zip(a, b)]


def scale(c, a):
    return [[c * x for x in row] for row in a]


def multiply(a, b):
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def outer(x, y):
    return [[xi * yj for yj in y] for xi in x]


def inverse(a):
    n = len(a)
    work = [list(row) + ident for row, ident in zip(a, eye(n))]
    for col in range(n):
        pivot = next(row for row in range(col, n) if work[row][col] != 0)
        work[col], work[pivot] = work[pivot], work[col]
        divisor = work[col][col]
        work[col] = [x / divisor for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            work[row] = [x - factor * y for x, y in zip(work[row], work[col])]
    return [row[n:] for row in work]


def principal(a, keep):
    return [[a[i][j] for j in keep] for i in keep]


def deletion_data(a, index: int):
    n = len(a)
    keep = [j for j in range(n) if j != index]
    child = principal(a, keep)
    # L_i maps a full residual h to h_{-i}-B_{-i,i}h_i.
    lift = zeros(n - 1, n)
    for local, original in enumerate(keep):
        lift[local][original] = F(1)
        lift[local][index] = -a[original][index]
    return child, lift


def first_schur_moment(a):
    n = len(a)
    g = inverse(a)
    shifted = subtract(g, eye(n))
    leverage = [F(1) / g[i][i] for i in range(n)]
    weighted = [[shifted[i][j] * leverage[j] for j in range(n)] for i in range(n)]
    return scale(F(1, n), multiply(weighted, shifted))


def second_schur_moment(a):
    n = len(a)
    result = zeros(n, n)
    for index in range(n):
        child, lift = deletion_data(a, index)
        result = add(result, multiply(transpose(lift), multiply(first_schur_moment(child), lift)))
    return scale(F(1, n), result)


def ordered_pair_formula(a):
    n = len(a)
    g = inverse(a)
    shifted = subtract(g, eye(n))
    result = zeros(n, n)
    for first in range(n):
        for second in range(n):
            if first == second:
                continue
            denominator = g[second][second] - g[first][second] ** 2 / g[first][first]
            child_leverage = F(1) / denominator
            vector = []
            for row in range(n):
                value = shifted[row][second]
                value -= g[first][second] / g[first][first] * shifted[row][first]
                if row == first:
                    value += a[first][second]
                vector.append(value)
            result = add(result, scale(child_leverage, outer(vector, vector)))
    return scale(F(1, n * (n - 1)), result)


def compound_matrix(n: int, off_diagonal: F):
    return [[F(1) if i == j else off_diagonal for j in range(n)] for i in range(n)]


def encode_fraction(x: F):
    return {"numerator": x.numerator, "denominator": x.denominator, "text": str(x)}


def encode_matrix(a):
    return [[str(x) for x in row] for row in a]


def quadratic_form(a, x):
    return sum(x[i] * a[i][j] * x[j] for i in range(len(x)) for j in range(len(x)))


def shallow_transverse_coefficient(n: int, depth: int) -> F:
    if depth == 1:
        return F(1, n)
    previous = shallow_transverse_coefficient(n - 1, depth - 1)
    return F(1, n) + F(n - 2, n - 1) * previous + F(n, (n - 1) ** 2)


def coordinate_update(a, index: int):
    update = eye(len(a))
    update[index] = [update[index][j] - a[index][j] for j in range(len(a))]
    return update


def update_product(a, sequence):
    product = eye(len(a))
    for index in sequence:
        product = multiply(coordinate_update(a, index), product)
    return product


def main():
    # Regular-simplex lift at mu=1/5: diagonal one, off-diagonal -2/5.
    simplex = compound_matrix(3, F(-2, 5))
    first = first_schur_moment(simplex)
    second = second_schur_moment(simplex)
    pair = ordered_pair_formula(simplex)
    difference = subtract(first, second)
    # For a 3-by-3 compound-symmetry matrix, the transverse eigenvalue is d-o.
    transverse = difference[0][0] - difference[0][1]

    # A second exact input checks the ordered-pair identity away from the
    # simplex sign pattern.
    rank_one = compound_matrix(4, F(2, 3))
    pair_rank_one_residual = subtract(second_schur_moment(rank_one), ordered_pair_formula(rank_one))

    # This SPD matrix has eigenvalues 7/12, 1, 17/12.  Therefore the first
    # Schur moment has a genuine kernel generated by the eigenvalue-one mode,
    # while the second moment is positive on that mode.  It rules out
    # R_B <= C * bar(D)_B for every finite scalar C.
    kernel_example = [
        [F(1), F(1, 3), F(1, 4)],
        [F(1, 3), F(1), F(0)],
        [F(1, 4), F(0), F(1)],
    ]
    kernel_vector = [F(0), F(1, 4), F(-1, 3)]
    kernel_first = first_schur_moment(kernel_example)
    kernel_second = second_schur_moment(kernel_example)
    first_on_vector = multiply(kernel_first, [[x] for x in kernel_vector])
    second_quadratic = quadratic_form(kernel_second, kernel_vector)

    # Chaining the sharp two-step scalar coefficient through a child still
    # fails.  In dimension three, all children of this equicorrelation matrix
    # have floor mu=1/8.  Replacing each exact child J_2 by
    # mu*C_i^{-1} gives the displayed parent lower bound, whose transverse
    # generalized coefficient is smaller than the desired mu.
    scalar_chain_mu = F(1, 8)
    scalar_chain_b = compound_matrix(3, F(7, 8))
    scalar_chain_g = inverse(scalar_chain_b)
    scalar_chain_d = first_schur_moment(scalar_chain_b)
    scalar_chain_lift_average = subtract(
        subtract(scalar_chain_g, scale(F(1, 3), eye(3))), scalar_chain_d
    )
    scalar_chain_lower = add(
        scale(F(1, 3), eye(3)), scale(scalar_chain_mu, scalar_chain_lift_average)
    )
    scalar_chain_transverse = (
        F(1, 8) * (scalar_chain_lower[0][0] - scalar_chain_lower[0][1])
    )

    # The historical n=3, mu=1/5 H1 barrier is passed once the exact second
    # loss is retained.  In dimension three there are no higher losses, so
    # K=G-bar(D)-R=H2.
    h2_barrier_b = compound_matrix(3, F(4, 5))
    h2_barrier_g = inverse(h2_barrier_b)
    h2_barrier_k = subtract(
        subtract(h2_barrier_g, first_schur_moment(h2_barrier_b)),
        second_schur_moment(h2_barrier_b),
    )
    h2_transverse = F(1, 5) * (h2_barrier_k[0][0] - h2_barrier_k[0][1])
    h2_parallel = F(13, 5) * (
        h2_barrier_k[0][0] + 2 * h2_barrier_k[0][1]
    )
    strong_target = F(1) - F(14, 15) ** 6

    # A tempting half-depth proof pairs the first half of an order with the
    # reversed complementary half, both started from the same point.  The
    # desired pathwise sum of decreases is false even on equicorrelation.
    complement_b = compound_matrix(3, F(1, 3))  # mu=2/3
    complement_first = update_product(complement_b, [0, 1])
    complement_second = update_product(complement_b, [2])
    complement_gap = subtract(
        subtract(
            subtract(
                scale(F(2), complement_b),
                multiply(transpose(complement_first), multiply(complement_b, complement_first)),
            ),
            multiply(transpose(complement_second), multiply(complement_b, complement_second)),
        ),
        scale(F(2, 3), complement_b),
    )
    complement_vector = [F(-4), F(-5), F(7)]
    complement_quadratic = quadratic_form(complement_gap, complement_vector)

    recurrence_checks = []
    for n in range(4, 13):
        for depth in range(1, n - 2):
            coefficient = shallow_transverse_coefficient(n, depth)
            closed = F(2 * depth - 1, n - 1) - F(1, n * (n - 1))
            recurrence_checks.append({
                "n": n,
                "depth": depth,
                "coefficient": str(coefficient),
                "closed_form": str(closed),
                "equal": coefficient == closed,
            })

    output = {
        "evidence_level": "E3 exact finite rational computation",
        "scope_warning": "Finite identities only; quantified claims require the accompanying algebraic proof.",
        "simplex_mu_one_fifth": {
            "B": encode_matrix(simplex),
            "first_schur_moment": encode_matrix(first),
            "second_schur_moment": encode_matrix(second),
            "ordered_pair_identity_exact": second == pair,
            "transverse_eigenvalue_first_minus_second": encode_fraction(transverse),
            "R2_leq_R1": transverse >= 0,
        },
        "rank_one_n4_offdiag_two_thirds": {
            "ordered_pair_identity_exact": pair_rank_one_residual == zeros(4, 4),
            "residual": encode_matrix(pair_rank_one_residual),
        },
        "no_scalar_second_over_first_compression": {
            "B": encode_matrix(kernel_example),
            "spectrum": ["7/12", "1", "17/12"],
            "kernel_vector": [str(x) for x in kernel_vector],
            "first_moment_times_vector": encode_matrix(first_on_vector),
            "second_moment_quadratic_form": encode_fraction(second_quadratic),
            "conclusion": "No finite C can make R_B <= C bar(D)_B on all unit-diagonal SPD B.",
        },
        "two_step_scalar_chain_barrier": {
            "B": encode_matrix(scalar_chain_b),
            "mu": str(scalar_chain_mu),
            "parent_lower_bound": encode_matrix(scalar_chain_lower),
            "transverse_generalized_coefficient": encode_fraction(scalar_chain_transverse),
            "target_mu": str(scalar_chain_mu),
            "gap": encode_fraction(scalar_chain_transverse - scalar_chain_mu),
            "conclusion": "The valid sharp J2 child scalar bound does not induct to J3 >= mu G.",
        },
        "n3_second_moment_clears_H1_barrier": {
            "B": encode_matrix(h2_barrier_b),
            "H2_equals_K": encode_matrix(h2_barrier_k),
            "transverse_coefficient": encode_fraction(h2_transverse),
            "parallel_coefficient": encode_fraction(h2_parallel),
            "strong_target": encode_fraction(strong_target),
            "minimum_minus_target": encode_fraction(
                min(h2_transverse, h2_parallel) - strong_target
            ),
        },
        "pathwise_complementary_half_barrier": {
            "B": encode_matrix(complement_b),
            "mu": "2/3",
            "first_sequence": [0, 1],
            "reversed_complement_sequence": [2],
            "gap_matrix": encode_matrix(complement_gap),
            "test_vector": [str(x) for x in complement_vector],
            "quadratic_form": encode_fraction(complement_quadratic),
            "conclusion": "The two separately started complementary-prefix decreases do not pathwise sum to mu*A. Averaging may still work.",
        },
        "shallow_rank_one_recurrence": {
            "range": "4 <= n <= 12, 1 <= depth <= n-3",
            "all_equal": all(item["equal"] for item in recurrence_checks),
            "checks": recurrence_checks,
        },
    }
    path = Path("research/evidence/ITER4_T085_EXACT_CERTIFICATES.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "ordered_pair_simplex": second == pair,
        "ordered_pair_rank_one": pair_rank_one_residual == zeros(4, 4),
        "transverse_first_minus_second": str(transverse),
        "second_positive_on_first_kernel": str(second_quadratic),
        "recurrences_all_equal": output["shallow_rank_one_recurrence"]["all_equal"],
    }, indent=2))


if __name__ == "__main__":
    main()
