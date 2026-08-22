"""Exact Fraction verifier for the first jet of the random-prefix matrix.

For A(eps)=I+eps*H with diag(H)=0, the exact first-order identity is

    J_t(A(eps)) = (t/n) I
      - eps*t(t-1)/(n(n-1))*H + O(eps^2).

The verifier enumerates all n! orders and constructs the first-order solve
rows directly.  It checks arbitrary deterministic rational test directions
through dimension seven.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path


def zeros(n: int):
    return [[F(0) for _ in range(n)] for _ in range(n)]


def add_outer(target, left, right, scale=F(1)):
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            target[i][j] += scale * x * y


def exact_jet(h: list[list[F]], steps: int):
    n = len(h)
    zeroth = zeros(n)
    first = zeros(n)
    orders = list(itertools.permutations(range(n)))
    for order in orders:
        for position, coordinate in enumerate(order[:steps]):
            row0 = [F(0) for _ in range(n)]
            row1 = [F(0) for _ in range(n)]
            row0[coordinate] = F(1)
            for earlier in order[:position]:
                row1[earlier] = -h[coordinate][earlier]
            add_outer(zeroth, row0, row0)
            add_outer(first, row0, row1)
            add_outer(first, row1, row0)
    denominator = F(len(orders))
    return (
        [[entry / denominator for entry in row] for row in zeroth],
        [[entry / denominator for entry in row] for row in first],
    )


def test_direction(n: int):
    # A deterministic, sign-frustrated zero-diagonal symmetric direction.
    h = zeros(n)
    for i in range(n):
        for j in range(i):
            value = F(((i + 2 * j) % 5) - 2, 3)
            if value == 0:
                value = F(1, 5)
            h[i][j] = h[j][i] = value
    return h


def subtract_half(left, right):
    return [
        [left[i][j] - F(1, 2) * right[i][j] for j in range(len(left))]
        for i in range(len(left))
    ]


def exact_record(max_n: int = 7):
    records = []
    for n in range(2, max_n + 1):
        h = test_direction(n)
        previous_zero = zeros(n)
        previous_first = zeros(n)
        step_records = []
        for steps in range(1, (n + 1) // 2 + 1):
            zeroth, first = exact_jet(h, steps)
            c = F(steps, n)
            d = F(steps * (steps - 1), n * (n - 1))
            expected_zero = [
                [F(int(i == j)) * c for j in range(n)] for i in range(n)
            ]
            expected_first = [[-d * h[i][j] for j in range(n)] for i in range(n)]
            assert zeroth == expected_zero
            assert first == expected_first

            weighted_zero = subtract_half(zeroth, previous_zero)
            weighted_first = subtract_half(first, previous_first)
            weighted_c = F(steps + 1, 2 * n)
            weighted_d = F((steps - 1) * (steps + 2), 2 * n * (n - 1))
            expected_weighted_zero = [
                [F(int(i == j)) * weighted_c for j in range(n)]
                for i in range(n)
            ]
            expected_weighted_first = [
                [-weighted_d * h[i][j] for j in range(n)] for i in range(n)
            ]
            assert weighted_zero == expected_weighted_zero
            assert weighted_first == expected_weighted_first

            step_records.append(
                {
                    "steps": steps,
                    "zeroth_coefficient": str(c),
                    "first_H_coefficient": str(-d),
                    "weighted_zeroth_coefficient": str(weighted_c),
                    "weighted_first_H_coefficient": str(-weighted_d),
                }
            )
            previous_zero, previous_first = zeroth, first
        records.append(
            {
                "n": n,
                "permutations_per_step": math.factorial(n),
                "steps_checked": step_records,
            }
        )
    return {
        "schema_version": "1.0",
        "status": "E3 exact finite reconstruction of the quantified combinatorial jet identity",
        "max_n": max_n,
        "records": records,
        "checks": "passed",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=7)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/evidence/ITER5_PREFIX_IDENTITY_JET_EXACT.json"),
    )
    args = parser.parse_args()
    record = exact_record(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": record["checks"]}, indent=2))


if __name__ == "__main__":
    main()
