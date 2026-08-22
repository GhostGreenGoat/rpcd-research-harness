"""Exact finite enumeration of the half-memory tail covariance jet."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def verify(n: int) -> dict[str, object]:
    q = (n + 1) // 2
    m = n - q - 1
    matrix_h = sp.zeros(n)
    for i in range(n):
        for j in range(i):
            value = sp.Rational(((5 * i + 7 * j) % 9) - 4, 11)
            matrix_h[i, j] = value
            matrix_h[j, i] = value

    average = sp.zeros(n)
    count = 0
    for order in itertools.permutations(range(n)):
        positions = {label: position for position, label in enumerate(order)}
        far = sp.zeros(n)
        for row_label in range(n):
            for column_label in range(n):
                if positions[row_label] - positions[column_label] > q:
                    far[row_label, column_label] = matrix_h[row_label, column_label]
        average += far * far.T
        count += 1
    average /= count
    p1 = sp.Rational(m * (m + 1), 2 * n * (n - 1))
    p2 = sp.Rational(m * (m + 1) * (m - 1), 3 * n * (n - 1) * (n - 2))
    square = matrix_h * matrix_h
    diagonal = sp.diag(*[square[i, i] for i in range(n)])
    expected = p2 * square + (p1 - p2) * diagonal
    assert average == expected
    assert p1 < sp.Rational(1, 8)
    return {
        "n": n,
        "q": q,
        "m": m,
        "permutations": count,
        "p1": str(p1),
        "p2": str(p2),
        "J4_passed_exactly": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for E3 all-dimensional jet",
        "cases": [verify(n) for n in (4, 5, 6, 7)],
        "result": "J4 passed exactly",
        "scope": "Leading epsilon^2 coefficient only; no uniform remainder radius.",
    }
    target = Path("research/iteration6/route_frame/evidence/near_identity_tail_jet.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
