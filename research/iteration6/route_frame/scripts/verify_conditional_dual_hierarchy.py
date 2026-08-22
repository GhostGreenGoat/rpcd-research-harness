"""Exact finite controls for the conditional dual-regression hierarchy."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def is_psd_exact(matrix: sp.Matrix) -> bool:
    n = matrix.rows
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            if sp.factor(matrix.extract(subset, subset).det()) < 0:
                return False
    return True


def canonical_cycle(order: tuple[int, ...]) -> tuple[int, ...]:
    rotations = [order[offset:] + order[:offset] for offset in range(len(order))]
    return min(rotations)


def outcome(matrix_a: sp.Matrix, order: tuple[int, ...], q: int) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    n = len(order)
    ordered = matrix_a.extract(order, order)
    matrix_m = sp.eye(n)
    for i in range(n):
        for j in range(i):
            matrix_m[i, j] = ordered[i, j]
    matrix_d = sp.eye(n)
    for k in range(n):
        start = max(0, k - q)
        block = matrix_m[start : k + 1, start : k + 1]
        target = sp.zeros(k - start + 1, 1)
        target[-1] = 1
        row = block.T.inv() * target
        for offset, value in enumerate(row):
            matrix_d[k, start + offset] = value
    matrix_r = matrix_d.T * matrix_d
    matrix_q = matrix_r * matrix_m * matrix_m.T * matrix_r
    matrix_k = matrix_m.T.inv() * matrix_m.inv()
    permutation = sp.zeros(n)
    for position, label in enumerate(order):
        permutation[position, label] = 1
    return (
        permutation.T * matrix_r * permutation,
        permutation.T * matrix_q * permutation,
        permutation.T * matrix_k * permutation,
    )


def moments(items: list[tuple[sp.Matrix, sp.Matrix, sp.Matrix]]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    count = len(items)
    matrix_p = sum((item[0] for item in items), sp.zeros(items[0][0].rows)) / count
    matrix_q = sum((item[1] for item in items), sp.zeros(items[0][0].rows)) / count
    matrix_w = sp.simplify(matrix_q.inv() * matrix_p)
    return matrix_p, matrix_q, matrix_w


def certificate(items: list[tuple[sp.Matrix, sp.Matrix, sp.Matrix]]) -> sp.Matrix:
    matrix_p, matrix_q, _ = moments(items)
    return sp.simplify(matrix_p * matrix_q.inv() * matrix_p)


def verify(n: int) -> dict[str, object]:
    q = (n + 1) // 2
    matrix_a = sp.eye(n)
    for i in range(n):
        for j in range(i):
            value = sp.Rational(((5 * i + 2 * j) % 5) - 2, 30 * n)
            matrix_a[i, j] = value
            matrix_a[j, i] = value
    assert all(sum(abs(matrix_a[i, j]) for j in range(n) if j != i) < 1 for i in range(n))

    all_items = []
    groups: dict[tuple[int, ...], list[tuple[sp.Matrix, sp.Matrix, sp.Matrix]]] = {}
    for order in itertools.permutations(range(n)):
        item = outcome(matrix_a, order, q)
        all_items.append(item)
        groups.setdefault(canonical_cycle(order), []).append(item)
    global_p, global_q, global_w = moments(all_items)
    global_certificate = sp.simplify(global_p * global_q.inv() * global_p)
    group_moments = {key: moments(group) for key, group in groups.items()}
    cycle_certificate = sum((certificate(group) for group in groups.values()), sp.zeros(n)) / len(groups)
    exact_moment = sum((item[2] for item in all_items), sp.zeros(n)) / len(all_items)
    assert all(len(group) == n for group in groups.values())
    assert is_psd_exact(sp.simplify(cycle_certificate - global_certificate))
    assert is_psd_exact(sp.simplify(exact_moment - cycle_certificate))
    first_square = sp.zeros(n)
    second_square = sp.zeros(n)
    for key, group in groups.items():
        _, group_q, group_w = group_moments[key]
        difference = group_w - global_w
        first_square += difference.T * group_q * difference / len(groups)
        for item in group:
            item_p, item_q, _ = moments([item])
            item_w = item_q.inv() * item_p
            fine_difference = item_w - group_w
            second_square += fine_difference.T * item_q * fine_difference / len(all_items)
    assert sp.simplify(first_square - (cycle_certificate - global_certificate)) == sp.zeros(n)
    assert sp.simplify(second_square - (exact_moment - cycle_certificate)) == sp.zeros(n)
    return {
        "n": n,
        "q": q,
        "orders": len(all_items),
        "cycles": len(groups),
        "cuts_per_cycle": n,
        "cycle_minus_global_psd": True,
        "full_minus_cycle_psd": True,
        "global_to_cycle_pythagorean_identity": True,
        "cycle_to_full_pythagorean_identity": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for E3 conditional hierarchy",
        "cases": [verify(n) for n in (3, 4)],
        "result": "trivial <= cyclic-cut <= full certificates exactly",
    }
    target = Path("research/iteration6/route_frame/evidence/conditional_dual_hierarchy.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
