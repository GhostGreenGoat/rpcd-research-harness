"""Exact permutation controls for the m<=2 generic arc-tail bounds."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def psd(matrix: sp.Matrix) -> bool:
    n = matrix.rows
    return all(
        sp.factor(matrix.extract(indices, indices).det()) >= 0
        for size in range(1, n + 1)
        for indices in itertools.combinations(range(n), size)
    )


def case(n: int) -> dict[str, object]:
    q = (n + 1) // 2
    m = n - q - 1
    matrix_a = sp.eye(n)
    for i in range(n):
        for j in range(i):
            value = sp.Rational(((3 * i + 2 * j) % 5) - 2, 25 * n)
            matrix_a[i, j] = value
            matrix_a[j, i] = value
    matrix_p = sp.zeros(n)
    matrix_s = sp.zeros(n)
    count = 0
    for order in itertools.permutations(range(n)):
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
        defect = matrix_d * matrix_m - sp.eye(n)
        tail = defect.T * matrix_d
        permutation = sp.zeros(n)
        for position, label in enumerate(order):
            permutation[position, label] = 1
        matrix_p += permutation.T * matrix_d.T * matrix_d * permutation
        matrix_s += permutation.T * tail.T * tail * permutation
        count += 1
    matrix_p /= count
    matrix_s /= count
    constant = sp.Rational(1, 2) if m == 1 else sp.Rational(7, 4)
    gap = sp.simplify(constant * matrix_p - matrix_s)
    if not psd(gap):
        numerical_eigenvalues = sorted(
            float(value) for value in gap.evalf().eigenvals(multiple=True)
        )
        raise AssertionError(
            f"n={n}, m={m}: proposed constant {constant} failed; "
            f"eigenvalues={numerical_eigenvalues}"
        )
    return {
        "n": n,
        "q": q,
        "m": m,
        "permutations": count,
        "C_tail": str(constant),
        "exact_Loewner_check": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for E3 m<=2 theorem",
        "cases": [case(n) for n in (4, 5, 6)],
        "result": "small-complement arc-tail bounds passed exactly",
        "scope": "Analytic proof covers n=4,...,7; verifier samples n<=6.",
    }
    target = Path("research/iteration6/route_frame/evidence/small_complement_arc_tail.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
