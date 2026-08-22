"""Exact enumeration of the frozen random-rank Gram identity."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def verify(m: int) -> dict[str, object]:
    # A deliberately nonsymmetric rational matrix prevents accidental
    # cancellations particular to a structured test family.
    c = sp.Matrix([[sp.Rational((i + 2) * (j + 3) + i - 2 * j, i + j + 2) for j in range(m)] for i in range(m)])
    total_g = sp.zeros(m)
    total_h = sp.zeros(m)
    total_weighted_g = sp.zeros(m)
    total_weighted_h = sp.zeros(m)
    weight = sp.Matrix(
        [[sp.Rational((i + 1) * (j + 1) + (1 if i == j else 0), m + 1) for j in range(m)] for i in range(m)]
    )
    perms = list(itertools.permutations(range(m)))
    count = 0
    for row_order in perms:
        row_pos = {label: rank for rank, label in enumerate(row_order)}
        for col_order in perms:
            col_pos = {label: rank for rank, label in enumerate(col_order)}
            g = sp.zeros(m)
            h = sp.zeros(m)
            for i in range(m):
                for j in range(m):
                    if col_pos[j] <= row_pos[i]:
                        g[i, j] = c[i, j]
                    else:
                        h[i, j] = c[i, j]
            total_g += g * g.T
            total_h += h * h.T
            total_weighted_g += g * weight * g.T
            total_weighted_h += h * weight * h.T
            count += 1
    avg_g = total_g / count
    avg_h = total_h / count
    z = c * c.T
    diag_z = sp.diag(*[z[i, i] for i in range(m)])
    expected_g = sp.Rational(m + 1, 3 * m) * z + sp.Rational(m + 1, 6 * m) * diag_z
    expected_h = sp.Rational(m - 2, 3 * m) * z + sp.Rational(m + 1, 6 * m) * diag_z
    assert avg_g == expected_g
    assert avg_h == expected_h
    assert avg_g - avg_h == z / m
    avg_weighted_g = total_weighted_g / count
    avg_weighted_h = total_weighted_h / count
    assert avg_weighted_g - avg_weighted_h == c * weight * c.T / m
    return {
        "m": m,
        "permutation_pairs": count,
        "unweighted_identities_passed": True,
        "operator_weighted_identity_passed": True,
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact reconstruction of E3 finite identity",
        "cases": [verify(m) for m in (2, 3, 4)],
        "result": "G1--G3w passed exactly",
    }
    target = Path("research/iteration6/route_frame/evidence/random_rank_gram.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
