"""Exact positive-definite lift of the n=8 T080 boundary counterexample.

For C with two identical poles, six regular-simplex ring points, pole--ring
correlation 2/3 and ring off-diagonal 1/3, set

    A_mu = mu I + (1-mu) C.

At mu=1/100 this script proves with rational arithmetic that the strong
one-epoch A-energy target q=(1-mu/8)^16 fails.  This is a refutation of that
particular one-epoch certificate, not of the original RPCD covariance/spectral
conjecture or of the desired multi-epoch complexity.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path


N = 8
MU = Fraction(1, 100)
SCALE = 1 - MU
POLE_POLE = SCALE
POLE_RING = SCALE * Fraction(2, 3)
RING_OFF_DIAGONAL = SCALE * Fraction(1, 3)


def category_energy(plus_position: int, minus_position: int) -> Fraction:
    """Compute ||M_pi(A_mu)^(-1)(e_1-e_2)||^2 for one class."""
    pole_sum = Fraction(0)
    ring_sum = Fraction(0)
    energy = Fraction(0)
    for position in range(N):
        if position == plus_position:
            value = Fraction(1) - POLE_POLE * pole_sum - POLE_RING * ring_sum
            pole_sum += value
        elif position == minus_position:
            value = Fraction(-1) - POLE_POLE * pole_sum - POLE_RING * ring_sum
            pole_sum += value
        else:
            value = -POLE_RING * pole_sum - RING_OFF_DIAGONAL * ring_sum
            ring_sum += value
        energy += value * value
    return energy


def category_coefficient() -> Fraction:
    total = Fraction(0)
    count = 0
    for plus_position in range(N):
        for minus_position in range(N):
            if plus_position == minus_position:
                continue
            total += category_energy(plus_position, minus_position)
            count += 1
    assert count == N * (N - 1) == 56
    # Divide by the 56 classes and by ||e_1-e_2||^2=2.
    return total / count / 2


def direct_full_permutation_coefficient() -> Fraction:
    """Independent exact solve over all 8! labelled permutations."""
    matrix = [[Fraction(0) for _ in range(N)] for _ in range(N)]
    for index in range(N):
        matrix[index][index] = 1
    matrix[0][1] = matrix[1][0] = POLE_POLE
    for pole in (0, 1):
        for ring in range(2, N):
            matrix[pole][ring] = matrix[ring][pole] = POLE_RING
    for left in range(2, N):
        for right in range(left + 1, N):
            matrix[left][right] = matrix[right][left] = RING_OFF_DIAGONAL

    right_side = [Fraction(1), Fraction(-1)] + [Fraction(0)] * 6
    total = Fraction(0)
    count = 0
    for order in permutations(range(N)):
        solution = [Fraction(0)] * N
        visited: list[int] = []
        energy = Fraction(0)
        for current in order:
            value = right_side[current] - sum(
                matrix[current][previous] * solution[previous]
                for previous in visited
            )
            solution[current] = value
            visited.append(current)
            energy += value * value
        total += energy
        count += 1
    assert count == 40320
    return total / count / 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T080_POSITIVE_MU_EXACT_LIFT_2026_08_21.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    kappa = category_coefficient()
    direct_kappa = direct_full_permutation_coefficient()
    assert kappa == direct_kappa

    q_low_gap = (1 - MU / N) ** (2 * N)
    q_dimension = Fraction(N - 1, N) ** N
    assert q_low_gap > q_dimension
    q_target = max(q_low_gap, q_dimension)

    # Along u=e_1-e_2, A_mu u=mu u.  Pole-swap symmetry makes u a
    # simultaneous eigenvector of K(A_mu), with eigenvalue kappa.  Therefore
    # the expected A-energy ratio for this direction is 1-mu*kappa.
    witnessed_ratio = 1 - MU * kappa
    violation = witnessed_ratio - q_target
    decrement_coefficient_target = (1 - q_target) / MU
    coefficient_gap = decrement_coefficient_target - kappa
    assert violation == MU * coefficient_gap
    assert coefficient_gap > 0
    assert violation > 0

    # Exact eigenvalues inherited from C: 0 (mult 2), 2/3 (mult 5), 14/3.
    eigenvalues = {
        "kernel": MU,
        "ring_standard": MU + SCALE * Fraction(2, 3),
        "trivial_positive": MU + SCALE * Fraction(14, 3),
    }
    assert eigenvalues["kernel"] > 0
    assert eigenvalues["ring_standard"] > 0
    assert eigenvalues["trivial_positive"] > 0

    payload = {
        "status": "exact rational finite-mu refutation of the strong one-epoch M1 target",
        "scope_warning": (
            "Does not refute the original RPCD covariance/spectral conjecture or "
            "the desired finite-time complexity."
        ),
        "n": N,
        "mu": str(MU),
        "A_mu_definition": "mu*I + (1-mu)*C",
        "off_diagonal_parameters": {
            "pole_pole": str(POLE_POLE),
            "pole_ring": str(POLE_RING),
            "distinct_ring": str(RING_OFF_DIAGONAL),
        },
        "exact_eigenvalues": {
            "mu_on_kernel_mult_2": str(eigenvalues["kernel"]),
            "ring_standard_mult_5": str(eigenvalues["ring_standard"]),
            "trivial_positive_mult_1": str(eigenvalues["trivial_positive"]),
        },
        "kernel_direction": [1, -1, 0, 0, 0, 0, 0, 0],
        "kappa_u": str(kappa),
        "kappa_u_decimal": float(kappa),
        "q_low_gap": str(q_low_gap),
        "q_dimension": str(q_dimension),
        "q_target": str(q_target),
        "witnessed_energy_ratio": str(witnessed_ratio),
        "witnessed_energy_ratio_decimal": float(witnessed_ratio),
        "ratio_minus_q_target": str(violation),
        "ratio_minus_q_target_decimal": float(violation),
        "target_decrement_coefficient_minus_kappa": str(coefficient_gap),
        "target_decrement_coefficient_minus_kappa_decimal": float(coefficient_gap),
        "category_words": 56,
        "permutations_per_category": 720,
        "permutations_represented": 40320,
        "direct_labelled_permutations_enumerated": 40320,
        "category_and_direct_enumerations_agree": True,
        "arithmetic": "Python fractions.Fraction; no floating-point decisions",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "kappa_u": str(kappa),
                "ratio_minus_q_target": str(violation),
                "ratio_minus_q_target_decimal": float(violation),
                "checks": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
