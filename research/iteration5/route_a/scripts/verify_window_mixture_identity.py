"""Exact rational reconstruction of the random-window identity (W2)."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def outer(row: sp.Matrix) -> sp.Matrix:
    return row.T * row


def main() -> None:
    # A nonsymmetric-pattern rational correlation matrix with a strict floor.
    vectors = [
        (sp.Rational(0), sp.Rational(1)),
        (sp.Rational(3, 5), sp.Rational(4, 5)),
        (sp.Rational(5, 13), sp.Rational(12, 13)),
        (sp.Rational(20, 29), sp.Rational(21, 29)),
    ]
    n = len(vectors)
    epsilon = sp.Rational(1, 20)
    gram = sp.Matrix(
        [[sum(vectors[i][z] * vectors[j][z] for z in range(2)) for j in range(n)] for i in range(n)]
    )
    matrix_b = epsilon * sp.eye(n) + (1 - epsilon) * gram
    orders = list(itertools.permutations(range(n)))

    increments = [sp.zeros(n) for _ in range(n)]
    local_frames = {q: sp.zeros(n) for q in range(n)}
    for order in orders:
        ordered_b = matrix_b.extract(order, order)
        matrix_m = sp.eye(n)
        for i in range(n):
            for j in range(i):
                matrix_m[i, j] = ordered_b[i, j]
        inverse_m = matrix_m.inv()

        for position in range(n):
            embedded = sp.zeros(1, n)
            for j in range(n):
                embedded[0, order[j]] = inverse_m[position, j]
            increments[position] += outer(embedded)

        for q in range(n):
            matrix_d = sp.zeros(n)
            for k in range(n):
                start = max(0, k - q)
                row = matrix_m.extract(range(start, k + 1), range(start, k + 1)).inv()[-1, :]
                for offset, value in enumerate(row):
                    matrix_d[k, start + offset] = value
            ordered_frame = matrix_d.T * matrix_d
            inverse_order = [order.index(label) for label in range(n)]
            local_frames[q] += ordered_frame.extract(inverse_order, inverse_order)

    denominator = sp.Rational(1, len(orders))
    increments = [sp.simplify(denominator * matrix) for matrix in increments]
    local_frames = {q: sp.simplify(denominator * matrix) for q, matrix in local_frames.items()}

    checks = []
    for q in range(n):
        predicted = sum(increments[:q], sp.zeros(n)) + (n - q) * increments[q]
        assert sp.simplify(local_frames[q] - predicted) == sp.zeros(n)
        checks.append({"q": q, "window": q + 1, "identity": "pass"})

    output = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact rational reconstruction of W2",
        "n": n,
        "epsilon": str(epsilon),
        "orders": len(orders),
        "checks": checks,
        "result": "passed",
        "scope": "Finite reconstruction of an independently proved distributional identity.",
    }
    path = Path(
        "research/iteration5/route_a/evidence/window_mixture_identity.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "result": "passed"}, indent=2))


if __name__ == "__main__":
    main()
