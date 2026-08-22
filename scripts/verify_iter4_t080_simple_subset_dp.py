"""Independent 2^n subset-DP audit of the simple n=8 T080 example.

This file audits the correlation matrix with pole--ring correlation 2/3 and
distinct-ring correlation 1/3.  It does not use the 56 pole-position classes,
does not enumerate 8! permutations, and does not import either discovery
script.  All decisions are made with ``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path


N = 8
POLE_RING = F(2, 3)
RING_OFF = F(1, 3)


def boundary_matrix():
    matrix = [[F(int(i == j)) for j in range(N)] for i in range(N)]
    matrix[0][1] = matrix[1][0] = F(1)
    for pole in (0, 1):
        for ring in range(2, N):
            matrix[pole][ring] = matrix[ring][pole] = POLE_RING
    for first in range(2, N):
        for second in range(first + 1, N):
            matrix[first][second] = matrix[second][first] = RING_OFF
    return matrix


def regularize(matrix, mu):
    return [
        [F(1) if i == j else (F(1) - mu) * matrix[i][j] for j in range(N)]
        for i in range(N)
    ]


def matvec(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(vector))]


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def expected_inverse_gram(matrix):
    """Return E_pi[M_pi^{-T} M_pi^{-1}] by a first-pivot subset recursion.

    If i is first and C is the remaining set, then in (i,C) block order

        M_pi^{-1} = [[1, 0], [-M_C^{-1} b, M_C^{-1}]],

    so averaging the inverse Gram over the remaining order only requires the
    child matrix K_C=E[M_C^{-T}M_C^{-1}].
    """

    @lru_cache(maxsize=None)
    def recurse(indices):
        size = len(indices)
        if size == 0:
            return tuple()
        accumulator = [[F(0) for _ in range(size)] for _ in range(size)]
        for pivot_position, pivot in enumerate(indices):
            rest = indices[:pivot_position] + indices[pivot_position + 1 :]
            child_tuple = recurse(rest)
            child = [list(row) for row in child_tuple]
            b = [matrix[coordinate][pivot] for coordinate in rest]
            child_b = [
                sum(child[row][column] * b[column] for column in range(size - 1))
                for row in range(size - 1)
            ]
            local_to_parent = [position for position in range(size) if position != pivot_position]

            accumulator[pivot_position][pivot_position] += F(1) + dot(b, child_b)
            for local, parent_position in enumerate(local_to_parent):
                accumulator[pivot_position][parent_position] -= child_b[local]
                accumulator[parent_position][pivot_position] -= child_b[local]
            for local_row, parent_row in enumerate(local_to_parent):
                for local_column, parent_column in enumerate(local_to_parent):
                    accumulator[parent_row][parent_column] += child[local_row][local_column]

        averaged = [[entry / size for entry in row] for row in accumulator]
        assert all(averaged[i][j] == averaged[j][i] for i in range(size) for j in range(size))
        return tuple(tuple(row) for row in averaged)

    return [list(row) for row in recurse(tuple(range(N)))]


def rayleigh(matrix, vector):
    return dot(vector, matvec(matrix, vector)) / dot(vector, vector)


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def main():
    correlation = boundary_matrix()
    u = [F(1), F(-1)] + [F(0)] * 6
    even_kernel = [F(-2), F(-2)] + [F(1)] * 6
    assert all(correlation[i][i] == 1 for i in range(N))
    assert matvec(correlation, u) == [F(0)] * N
    assert matvec(correlation, even_kernel) == [F(0)] * N
    assert dot(u, even_kernel) == 0

    # Exact invariant-subspace spectrum: two kernel lines, the five-dimensional
    # ring-standard space, and one remaining positive trivial eigenline.
    ring_standard = F(1) - RING_OFF
    trivial_trace = F(2) + F(1) + 5 * RING_OFF
    trivial_determinant = F(2) * (F(1) + 5 * RING_OFF) - 12 * POLE_RING**2
    assert ring_standard == F(2, 3)
    assert trivial_trace == F(14, 3)
    assert trivial_determinant == 0

    boundary_k = expected_inverse_gram(correlation)
    boundary_coefficient = rayleigh(boundary_k, u)
    claimed_boundary = F(1057837, 531441)
    assert boundary_coefficient == claimed_boundary
    assert boundary_coefficient < 2
    boundary_image = matvec(boundary_k, u)
    assert boundary_image == [boundary_coefficient, -boundary_coefficient] + [F(0)] * 6

    # Give a direct interior counterexample rather than only invoking continuity
    # of the boundary Schur coefficient.
    mu = F(1, 100)
    positive_matrix = regularize(correlation, mu)
    positive_k = expected_inverse_gram(positive_matrix)
    positive_coefficient = rayleigh(positive_k, u)
    claimed_positive = F(
        277091954946975183681661134197,
        140000000000000000000000000000,
    )
    assert positive_coefficient == claimed_positive
    positive_image = matvec(positive_k, u)
    assert positive_image == [positive_coefficient, -positive_coefficient] + [F(0)] * 6

    q_mu = (F(1) - mu / N) ** (2 * N)
    q_dimension = F(N - 1, N) ** N
    assert q_mu > q_dimension
    witnessed_final_energy_ratio = F(1) - mu * positive_coefficient
    violation = witnessed_final_energy_ratio - q_mu
    claimed_violation = F(
        4198136398771974389711477950466919707327993,
        197032483697459200000000000000000000000000000000,
    )
    assert violation == claimed_violation
    assert violation > 0

    output = {
        "schema_version": "1.0",
        "evidence_level": "E4 independent exact reconstruction",
        "method": "standard-library Fraction 2^8 first-pivot subset DP",
        "matrix_family": "simple two-pole/six-ring example",
        "boundary_parameters": {
            "pole_pole": "1",
            "pole_ring": str(POLE_RING),
            "distinct_ring": str(RING_OFF),
        },
        "boundary_spectrum": {
            "zero": {"value": "0", "multiplicity": 2},
            "ring_standard": {"value": str(ring_standard), "multiplicity": 5},
            "trivial_positive": {"value": str(trivial_trace), "multiplicity": 1},
        },
        "boundary": {
            "kernel_direction_u": encode(u),
            "second_kernel_direction": encode(even_kernel),
            "K0_rayleigh_on_u": str(boundary_coefficient),
            "gap_to_two": str(boundary_coefficient - 2),
            "K0_times_u": encode(boundary_image),
            "swap_odd_line_reducing_exact": True,
            "Schur_complement_eigenvalue_on_u": str(boundary_coefficient),
        },
        "positive_mu_M1_failure": {
            "mu": str(mu),
            "lambda_min": str(mu),
            "positive_eigenvalues": {
                "ring_standard": str(mu + (1 - mu) * ring_standard),
                "trivial": str(mu + (1 - mu) * trivial_trace),
            },
            "K_rayleigh_on_u": str(positive_coefficient),
            "active_q": str(q_mu),
            "other_q": str(q_dimension),
            "witnessed_final_energy_ratio": str(witnessed_final_energy_ratio),
            "witnessed_ratio_minus_q": str(violation),
            "strict_failure": True,
        },
        "scope": {
            "refutes": [
                "T080 boundary inequality K0(C) >= 2 P_ker(C)",
                "strong one-epoch A-energy M1 target at mu=1/100",
            ],
            "does_not_refute": "original covariance-map spectral-radius conjecture C001",
        },
    }
    output_path = Path(
        "research/evidence/ITER4_T080_SIMPLE_SUBSET_DP_INDEPENDENT_AUDIT.json"
    )
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(output_path),
                "boundary_coefficient": str(boundary_coefficient),
                "positive_mu": str(mu),
                "M1_violation": str(violation),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
