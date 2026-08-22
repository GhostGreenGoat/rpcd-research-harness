"""Exact rational reconstruction of an n=8 counterexample to T080.

The matrix has two identical poles and a six-point regular-simplex ring.  By
symmetry, for the pole-difference input only the ordered positions of the two
labelled poles matter; the other six symbols are exchangeable.  We enumerate
all 8*7=56 category words with ``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path


POLE_RING = Fraction(2, 3)
RING_OFF_DIAGONAL = Fraction(1, 3)
N = 8


def category_energy(plus_position: int, minus_position: int) -> Fraction:
    """Forward-solve energy for one ordered pole-position category."""
    pole_sum = Fraction(0)
    ring_sum = Fraction(0)
    energy = Fraction(0)
    for position in range(N):
        if position == plus_position:
            value = Fraction(1) - pole_sum - POLE_RING * ring_sum
            pole_sum += value
        elif position == minus_position:
            value = Fraction(-1) - pole_sum - POLE_RING * ring_sum
            pole_sum += value
        else:
            value = -POLE_RING * pole_sum - RING_OFF_DIAGONAL * ring_sum
            ring_sum += value
        energy += value * value
    return energy


def exact_coefficient() -> tuple[Fraction, list[dict[str, object]]]:
    records: list[dict[str, object]] = []
    energy_sum = Fraction(0)
    for plus_position in range(N):
        for minus_position in range(N):
            if plus_position == minus_position:
                continue
            energy = category_energy(plus_position, minus_position)
            energy_sum += energy
            records.append(
                {
                    "plus_position_zero_based": plus_position,
                    "minus_position_zero_based": minus_position,
                    "energy": str(energy),
                }
            )
    expected_energy = energy_sum / len(records)
    # ||e_1-e_2||^2=2.
    return expected_energy / 2, records


def closed_double_sum_energy() -> Fraction:
    """Independent 28-term geometric-series reconstruction of E||M^-1 u||^2."""
    q = Fraction(2, 3)
    total = Fraction(0)
    for middle in range(7):
        for after in range(7 - middle):
            energy = (
                1
                + Fraction(4, 5) * (1 - q ** (2 * middle))
                + Fraction(4, 9) * (1 + 2 * q**middle) ** 2
                + Fraction(4, 45)
                * (2 + q**middle) ** 2
                * (1 - q ** (2 * after))
            )
            total += energy
    # The negative-first orientation is identical, so averaging all 56 words
    # is the same as averaging these 28 positive-first compositions.
    return total / 28


def direct_full_permutation_coefficient() -> Fraction:
    """Independent direct forward solve over all 8! labelled permutations."""
    correlation = [[Fraction(0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        correlation[i][i] = 1
    correlation[0][1] = correlation[1][0] = 1
    for pole in [0, 1]:
        for ring in range(2, N):
            correlation[pole][ring] = correlation[ring][pole] = POLE_RING
    for left in range(2, N):
        for right in range(left + 1, N):
            correlation[left][right] = correlation[right][left] = RING_OFF_DIAGONAL
    right_side = [Fraction(1), Fraction(-1)] + [Fraction(0)] * 6
    total = Fraction(0)
    count = 0
    for order in permutations(range(N)):
        solution = [Fraction(0)] * N
        visited: list[int] = []
        energy = Fraction(0)
        for current in order:
            value = right_side[current] - sum(
                correlation[current][previous] * solution[previous]
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
        default=Path("research/evidence/ITER4_T080_EXACT_COUNTEREXAMPLE_N8_2026_08_21.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    coefficient, records = exact_coefficient()
    closed_energy = closed_double_sum_energy()
    direct_coefficient = direct_full_permutation_coefficient()
    claimed = Fraction(
        1057837,
        531441,
    )
    assert coefficient == claimed
    assert closed_energy == 2 * claimed
    assert direct_coefficient == claimed
    gap = coefficient - 2
    claimed_gap = -Fraction(
        5045,
        531441,
    )
    assert gap == claimed_gap
    assert gap < 0

    # Exact spectral data from the invariant subspaces:
    # pole difference: 0; ring standard: 1-rho=54/125 (multiplicity 5);
    # the two-dimensional trivial block has determinant zero and trace 146/25.
    ring_standard = 1 - RING_OFF_DIAGONAL
    trivial_trace = Fraction(2) + 1 + 5 * RING_OFF_DIAGONAL
    trivial_determinant = Fraction(2) * (1 + 5 * RING_OFF_DIAGONAL) - 12 * POLE_RING**2
    assert ring_standard == Fraction(2, 3)
    assert trivial_trace == Fraction(14, 3)
    assert trivial_determinant == 0

    payload = {
        "status": "E2 exact rational counterexample to T080",
        "statement_refuted": "K0(C) >= 2 P_ker(C) for every singular correlation matrix C",
        "n": N,
        "matrix_parameters": {
            "poles": 2,
            "ring_points": 6,
            "pole_pole": "1",
            "pole_ring": str(POLE_RING),
            "distinct_ring": str(RING_OFF_DIAGONAL),
        },
        "psd_spectrum": {
            "zero": {"value": "0", "multiplicity": 2},
            "ring_standard": {"value": str(ring_standard), "multiplicity": 5},
            "trivial_positive": {"value": str(trivial_trace), "multiplicity": 1},
        },
        "kernel_vector": [1, -1, 0, 0, 0, 0, 0, 0],
        "kernel_vector_squared_norm": 2,
        "category_words": len(records),
        "permutations_represented": 40320,
        "direct_labelled_permutations_enumerated": 40320,
        "category_and_direct_enumerations_agree": True,
        "closed_28_term_double_sum_energy": str(closed_energy),
        "closed_double_sum_agrees": True,
        "rayleigh_coefficient": str(coefficient),
        "rayleigh_coefficient_decimal": float(coefficient),
        "gap_to_2": str(gap),
        "gap_to_2_decimal": float(gap),
        "category_records": records,
        "arithmetic": "Python fractions.Fraction; no floating-point decisions",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "coefficient": str(coefficient),
                "gap_to_2": str(gap),
                "checks": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
