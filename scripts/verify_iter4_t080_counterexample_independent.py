"""Independent exact audit of the 4/5, 71/125 n=8 T080 counterexample.

The source report is the 4/5, 71/125 construction recorded in
``ITER4_ROOT_PERMUTATION_BLOCK_SOS.md`` and audited by the independent subset
DP script ``iter4_root_t080_counterexample_audit.py``.  This verifier instead
constructs the full labelled 8-by-8 matrix and loops over all 8! permutations
with generic forward/back substitution.  It also checks one explicit positive
rational mu for the stronger one-epoch energy inequality M1.

At the time of this audit, ``iter4_t080_exact_counterexample.py`` contained a
different 2/3, 1/3 example.  It is therefore deliberately not cited as the
source of the parameters checked here.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path


N = 8
POLE_RING = F(4, 5)
RING_OFF = F(71, 125)


def correlation_matrix():
    matrix = [[F(int(i == j)) for j in range(N)] for i in range(N)]
    matrix[0][1] = matrix[1][0] = F(1)
    for pole in (0, 1):
        for ring in range(2, N):
            matrix[pole][ring] = matrix[ring][pole] = POLE_RING
    for first in range(2, N):
        for second in range(2, N):
            if first != second:
                matrix[first][second] = RING_OFF
    return matrix


def regularized(matrix, mu: F):
    return [
        [F(1) if i == j else (F(1) - mu) * matrix[i][j] for j in range(N)]
        for i in range(N)
    ]


def matvec(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(N)) for i in range(N)]


def identity_matrix():
    return [[F(int(i == j)) for j in range(N)] for i in range(N)]


def matmul(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(N)) for j in range(N)]
        for i in range(N)
    ]


def coordinate_update_matrix(matrix, coordinate):
    """Return U_i=I-e_i e_i^T A for a unit-diagonal quadratic."""
    update = identity_matrix()
    update[coordinate] = [
        update[coordinate][j] - matrix[coordinate][j] for j in range(N)
    ]
    return update


def check_update_product_orientation(matrix, order):
    """Check T_pi=U_last...U_first=I-M_pi^{-1}A exactly."""
    direct_product = identity_matrix()
    for coordinate in order:
        direct_product = matmul(coordinate_update_matrix(matrix, coordinate), direct_product)

    inverse_times_matrix = [[F(0) for _ in range(N)] for _ in range(N)]
    for column in range(N):
        solved_column = forward_solve(
            matrix, order, [matrix[row][column] for row in range(N)]
        )
        for row in range(N):
            inverse_times_matrix[row][column] = solved_column[row]
    triangular_formula = [
        [F(int(i == j)) - inverse_times_matrix[i][j] for j in range(N)]
        for i in range(N)
    ]
    assert direct_product == triangular_formula
    return True


def forward_solve(matrix, order, rhs):
    """Solve the order-lower Gauss--Seidel factor M_order y=rhs."""
    solution = [F(0) for _ in range(N)]
    previous = []
    for coordinate in order:
        solution[coordinate] = rhs[coordinate] - sum(
            matrix[coordinate][earlier] * solution[earlier] for earlier in previous
        )
        previous.append(coordinate)
    return solution


def transpose_solve(matrix, order, rhs):
    """Solve M_order^T z=rhs by generic reverse substitution."""
    solution = [F(0) for _ in range(N)]
    later = []
    for coordinate in reversed(order):
        solution[coordinate] = rhs[coordinate] - sum(
            matrix[later_coordinate][coordinate] * solution[later_coordinate]
            for later_coordinate in later
        )
        later.append(coordinate)
    return solution


def audit_average(matrix):
    u = [F(1), F(-1)] + [F(0)] * 6
    energy_sum = F(0)
    image_sum = [F(0)] * N
    category_counts = Counter()
    category_energies = defaultdict(set)
    permutations = 0
    for order in itertools.permutations(range(N)):
        solution = forward_solve(matrix, order, u)
        # Generic orientation check: M*y=u in every coordinate.
        positions = {coordinate: position for position, coordinate in enumerate(order)}
        reconstructed = []
        for coordinate in range(N):
            reconstructed.append(
                solution[coordinate]
                + sum(
                    matrix[coordinate][other] * solution[other]
                    for other in range(N)
                    if positions[other] < positions[coordinate]
                )
            )
        assert reconstructed == u
        energy = sum(value * value for value in solution)
        image = transpose_solve(matrix, order, solution)
        # M^T*image=solution is checked by reversing the same order relation.
        reconstructed_transpose = []
        for coordinate in range(N):
            reconstructed_transpose.append(
                image[coordinate]
                + sum(
                    matrix[other][coordinate] * image[other]
                    for other in range(N)
                    if positions[other] > positions[coordinate]
                )
            )
        assert reconstructed_transpose == solution
        energy_sum += energy
        image_sum = [left + right for left, right in zip(image_sum, image)]
        category = (positions[0], positions[1])
        category_counts[category] += 1
        category_energies[category].add(energy)
        permutations += 1
    assert permutations == 40320
    assert len(category_counts) == 56
    assert set(category_counts.values()) == {720}
    assert all(len(values) == 1 for values in category_energies.values())
    expected_energy = energy_sum / permutations
    expected_image = [value / permutations for value in image_sum]
    return {
        "permutations": permutations,
        "category_count": len(category_counts),
        "multiplicities": sorted(set(category_counts.values())),
        "expected_energy": expected_energy,
        "rayleigh": expected_energy / 2,
        "K_times_u": expected_image,
        "reducing_exact": expected_image[0] == expected_energy / 2
        and expected_image[1] == -expected_energy / 2
        and expected_image[2:] == [F(0)] * 6,
    }


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    return value


def main():
    matrix = correlation_matrix()
    u = [F(1), F(-1)] + [F(0)] * 6
    assert matvec(matrix, u) == [F(0)] * N
    assert all(matrix[i][i] == 1 for i in range(N))

    # Exact invariant-subspace spectrum.
    ring_standard = F(1) - RING_OFF
    trivial_trace = F(2) + F(1) + 5 * RING_OFF
    trivial_determinant = F(2) * (F(1) + 5 * RING_OFF) - 12 * POLE_RING**2
    assert ring_standard == F(54, 125)
    assert trivial_trace == F(146, 25)
    assert trivial_determinant == 0

    # This is deliberately a second construction of the RPCD epoch matrix,
    # independent of the energy/back-substitution calculation below.
    orientation_orders = [
        tuple(range(N)),
        tuple(reversed(range(N))),
        (0, 2, 4, 6, 1, 3, 5, 7),
        (7, 1, 6, 0, 5, 2, 4, 3),
    ]
    assert all(check_update_product_orientation(matrix, order) for order in orientation_orders)

    boundary = audit_average(matrix)
    claimed = F(2296209806050635263939777, 1164153218269348144531250)
    assert boundary["rayleigh"] == claimed
    assert boundary["rayleigh"] < 2
    assert boundary["reducing_exact"]

    # An explicit interior ray point.  Swap symmetry persists, A_mu*u=mu*u,
    # and the energy decrease along u is mu*u^T K(A_mu)u/||u||^2.
    mu = F(1, 1000)
    interior = audit_average(regularized(matrix, mu))
    active_q = (F(1) - mu / N) ** (2 * N)
    other_q = F(7, 8) ** 8
    assert active_q > other_q
    actual_decrease_on_u = mu * interior["rayleigh"]
    required_decrease = F(1) - active_q
    strict_failure_gap = required_decrease - actual_decrease_on_u
    assert strict_failure_gap > 0

    output = {
        "evidence_level": "E3 independent exact rational reconstruction",
        "matrix": [[str(value) for value in row] for row in matrix],
        "unit_diagonal": True,
        "coordinate_update_orientation": {
            "identity": "T_pi=U_{pi_n}...U_{pi_1}=I-M_pi^{-1}C",
            "exact_representative_orders_checked": [list(order) for order in orientation_orders],
        },
        "exact_spectrum": {
            "pole_odd_zero": {"value": "0", "multiplicity": 1},
            "trivial_even_zero": {"value": "0", "multiplicity": 1},
            "ring_standard": {"value": str(ring_standard), "multiplicity": 5},
            "trivial_positive": {"value": str(trivial_trace), "multiplicity": 1},
        },
        "boundary": encode(boundary),
        "boundary_gap_to_two": str(boundary["rayleigh"] - 2),
        "explicit_positive_mu_M1_failure": {
            "mu": str(mu),
            "lambda_min_A": str(mu),
            "K_rayleigh_on_swap_odd_u": str(interior["rayleigh"]),
            "actual_energy_decrease_on_u": str(actual_decrease_on_u),
            "active_q": str(active_q),
            "other_q": str(other_q),
            "required_decrease_one_minus_q": str(required_decrease),
            "required_minus_actual_decrease": str(strict_failure_gap),
            "strict_failure": True,
        },
        "scope": {
            "refutes": [
                "T080: K0(C) >= 2 P_ker(C)",
                "the stronger one-epoch A-energy matrix bound M1 at the displayed positive mu",
            ],
            "does_not_refute": "the original RPCD covariance-map spectral-radius conjecture C001",
        },
    }
    path = Path("research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_INDEPENDENT_AUDIT.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(path),
        "boundary_rayleigh": str(boundary["rayleigh"]),
        "reducing_exact": boundary["reducing_exact"],
        "positive_mu": str(mu),
        "positive_mu_failure_gap": str(strict_failure_gap),
    }, indent=2))


if __name__ == "__main__":
    main()
