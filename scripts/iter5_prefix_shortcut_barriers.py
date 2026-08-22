"""Two exact shortcut failures for the half-prefix route."""

from fractions import Fraction as F


def exact_record():
    # n=3, t=2, A=(1-rho)I+rho J with rho=4/5.
    n = 3
    rho = F(4, 5)
    alpha = 1 - rho
    # Exact invariant recurrence for J_2.
    child_parallel = F(1, 2)
    parallel_j2 = F(1, 3) + F(2, 3) * alpha**2 * child_parallel
    ordinary_floor_gap = parallel_j2 - F(2, 3)
    # The contribution of chronological position k on the parallel line is
    # alpha^(2(k-1))/n, so position two minus position one is negative.
    position_monotonicity_gap = (alpha**2 - 1) / n
    # Yet the actual normalized target has a positive parallel margin.
    lambda_parallel = 1 + (n - 1) * rho
    mu = 1 - rho
    normalized_target_gap = lambda_parallel * parallel_j2 - F(2, 3) * mu
    assert parallel_j2 == F(26, 75)
    assert ordinary_floor_gap == F(-8, 25)
    assert position_monotonicity_gap == F(-8, 25)
    assert normalized_target_gap == F(96, 125)
    return {
        "schema_version": "1.0",
        "status": "exact rational proof-route counterexamples; the normalized half-prefix target survives",
        "matrix": "A=(1/5)I+(4/5)J in dimension 3",
        "parallel_J2_eigenvalue": str(parallel_j2),
        "J2_minus_2I_over_3_parallel_gap": str(ordinary_floor_gap),
        "position_2_minus_position_1_parallel_gap": str(position_monotonicity_gap),
        "actual_normalized_target_parallel_margin": str(normalized_target_gap),
        "checks": "passed",
    }


if __name__ == "__main__":
    for key, value in exact_record().items():
        print(f"{key}: {value}")
