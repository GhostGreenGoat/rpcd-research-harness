"""Exact controls for the square-zero half-memory and dual identities."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def build(n: int) -> dict[str, object]:
    q = (n + 1) // 2
    matrix_a = sp.eye(n)
    for i in range(n):
        for j in range(i):
            value = sp.Rational(((7 * i + 3 * j) % 7) - 3, 50 * n)
            matrix_a[i, j] = value
            matrix_a[j, i] = value
    assert all(sum(abs(matrix_a[i, j]) for j in range(n) if j != i) < 1 for i in range(n))

    matrix_m = sp.eye(n)
    for i in range(n):
        for j in range(i):
            matrix_m[i, j] = matrix_a[i, j]
    matrix_d = sp.eye(n)
    for k in range(n):
        start = max(0, k - q)
        block = matrix_m[start : k + 1, start : k + 1]
        target = sp.zeros(k - start + 1, 1)
        target[-1] = 1
        row = block.T.inv() * target
        for offset, value in enumerate(row):
            matrix_d[k, start + offset] = value

    defect = sp.simplify(matrix_d * matrix_m - sp.eye(n))
    assert defect * defect == sp.zeros(n)
    exact_inverse = matrix_m.inv()
    matrix_x = (sp.eye(n) - defect) * matrix_d
    matrix_r = matrix_d.T * matrix_d
    matrix_y = (sp.eye(n) + defect.T) * matrix_d
    assert matrix_x == exact_inverse
    assert matrix_y == matrix_m.T * matrix_r
    assert matrix_x.T * matrix_y == matrix_r
    error = matrix_x - matrix_y
    expected_error_gram = matrix_d.T * (defect.T * defect + defect * defect.T) * matrix_d
    assert error.T * error == expected_error_gram

    # Exact energy identities proving both orientations of N10.
    transform = sp.eye(n) - matrix_m.inv() * matrix_a
    decrease = sp.simplify(matrix_a - transform.T * matrix_a * transform)
    expected_decrease = matrix_a * matrix_m.T.inv() * matrix_m.inv() * matrix_a
    assert decrease == expected_decrease
    matrix_reverse = matrix_m.T
    transform_reverse = sp.eye(n) - matrix_reverse.inv() * matrix_a
    decrease_reverse = sp.simplify(matrix_a - transform_reverse.T * matrix_a * transform_reverse)
    expected_reverse = matrix_a * matrix_reverse.T.inv() * matrix_reverse.inv() * matrix_a
    assert decrease_reverse == expected_reverse

    nonzero_defect = [(i, j) for i in range(n) for j in range(n) if defect[i, j] != 0]
    assert all(i - j > q for i, j in nonzero_defect)
    return {
        "n": n,
        "q": q,
        "nonzero_defect_entries": len(nonzero_defect),
        "F_squared_zero": True,
        "inverse_and_biorthogonal_identities": True,
        "two_energy_identities": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for E3 identities",
        "cases": [build(n) for n in (4, 5, 6, 7, 8)],
        "result": "N2--N10 exact identities passed",
    }
    target = Path("research/iteration6/route_frame/evidence/nilpotent_half_memory.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
