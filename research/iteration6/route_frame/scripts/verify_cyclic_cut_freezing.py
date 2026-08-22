"""Exact finite reconstruction of cyclic-cut residual freezing."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def local_inverse(matrix_a: sp.Matrix, order: list[int], q: int) -> tuple[sp.Matrix, sp.Matrix]:
    n = len(order)
    ordered = matrix_a.extract(order, order)
    matrix_m = sp.zeros(n)
    for i in range(n):
        matrix_m[i, i] = 1
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
    permutation = sp.zeros(n)
    for position, label in enumerate(order):
        permutation[position, label] = 1
    return permutation.T * matrix_d * permutation, permutation.T * matrix_m * permutation


def verify(n: int) -> dict[str, object]:
    q = (n + 1) // 2
    m = n - q - 1
    # Strict diagonal dominance makes SPD immediate, with exact rationals.
    matrix_a = sp.eye(n)
    for i in range(n):
        for j in range(i):
            value = sp.Rational(((3 * i + 5 * j) % 5) - 2, 40 * n)
            matrix_a[i, j] = value
            matrix_a[j, i] = value
    assert all(sum(abs(matrix_a[i, j]) for j in range(n) if j != i) < 1 for i in range(n))

    cycle = list(range(n))
    cyclic_rows: list[sp.Matrix] = []
    correlations = sp.zeros(n)
    for label in cycle:
        window = [cycle[(label - q + offset) % n] for offset in range(q + 1)]
        ordered = matrix_a.extract(window, window)
        matrix_m = sp.zeros(q + 1)
        for i in range(q + 1):
            matrix_m[i, i] = 1
            for j in range(i):
                matrix_m[i, j] = ordered[i, j]
        target = sp.zeros(q + 1, 1)
        target[-1] = 1
        row_local = matrix_m.T.inv() * target
        row = sp.zeros(1, n)
        for position, window_label in enumerate(window):
            row[window_label] = row_local[position]
        cyclic_rows.append(row)
        for distance in range(1, m + 1):
            successor = cycle[(label + distance) % n]
            correlations[label, successor] = (row * matrix_a[:, successor])[0]

    indicators: list[sp.Matrix] = []
    tail_matrices: list[sp.Matrix] = []
    for cut in range(n):
        order = [cycle[(cut + offset) % n] for offset in range(n)]
        matrix_d, matrix_m = local_inverse(matrix_a, order, q)
        defect = sp.simplify(matrix_d * matrix_m - sp.eye(n))
        positions = {label: position for position, label in enumerate(order)}
        predicted = sp.zeros(n)
        indicator = sp.zeros(n)
        for i in range(n):
            for j in range(n):
                cyclic_distance = (j - i) % n
                if 1 <= cyclic_distance <= m and positions[j] < positions[i]:
                    predicted[i, j] = correlations[i, j]
                    indicator[i, j] = 1
        assert defect == predicted
        predicted_tail = sp.zeros(n)
        for i in range(n):
            for j in range(n):
                if indicator[i, j]:
                    predicted_tail[j, :] += correlations[i, j] * cyclic_rows[i]
        tail = sp.simplify(defect.T * matrix_d)
        assert tail == predicted_tail
        indicators.append(indicator)
        tail_matrices.append(tail)

    singles_ok = True
    products_ok = True
    arcs: dict[tuple[int, int], set[int]] = {}
    for i in range(n):
        for distance in range(1, m + 1):
            j = (i + distance) % n
            # Cuts at labels i+1,...,j make j precede i.
            arcs[(i, j)] = {(i + step) % n for step in range(1, distance + 1)}
            count = sum(int(indicator[i, j]) for indicator in indicators)
            singles_ok &= count == distance
    keys = list(arcs)
    for first in keys:
        for second in keys:
            count = sum(
                int(indicator[first[0], first[1]] * indicator[second[0], second[1]])
                for indicator in indicators
            )
            products_ok &= count == len(arcs[first].intersection(arcs[second]))
    assert singles_ok and products_ok
    test_vector = sp.Matrix([sp.Rational(index + 1, n + 2) for index in range(n)])
    cut_tail_energy = sum((tail * test_vector).dot(tail * test_vector) for tail in tail_matrices) / n
    nested_energy = 0
    for j in range(n):
        coefficients = []
        for distance in range(1, m + 1):
            i = (j - distance) % n
            coefficients.append(correlations[i, j] * (cyclic_rows[i] * test_vector)[0])
        for start in range(m):
            nested_energy += sum(coefficients[start:]) ** 2 / n
    assert sp.factor(cut_tail_energy - nested_energy) == 0
    return {
        "n": n,
        "q": q,
        "m": m,
        "cuts_checked": n,
        "defect_identity_every_cut": True,
        "single_arc_counts": True,
        "pairwise_arc_overlap_counts": True,
        "dual_tail_arc_identity": True,
        "nested_Hardy_identity": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact reconstruction of E3 cyclic-cut identity",
        "cases": [verify(n) for n in (5, 6, 7, 8)],
        "result": "C1--C6 passed exactly",
    }
    target = Path("research/iteration6/route_frame/evidence/cyclic_cut_freezing.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
