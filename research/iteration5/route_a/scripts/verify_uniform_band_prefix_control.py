"""Exact finite control of the direct-prefix near-identity corollary."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def all_principal_minors_nonnegative(matrix: sp.Matrix) -> tuple[bool, sp.Rational]:
    n = matrix.rows
    minimum = None
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            determinant = sp.factor(matrix.extract(subset, subset).det())
            if determinant < 0:
                return False, determinant
            if minimum is None or determinant < minimum:
                minimum = determinant
    assert minimum is not None
    return True, minimum


def main() -> None:
    # Three unequal signed 2x2 blocks; mu=29/30 and theta=1/5.
    correlations = [sp.Rational(1, 30), -sp.Rational(1, 40), sp.Rational(1, 50)]
    n = 2 * len(correlations)
    matrix_b = sp.eye(n)
    for block, correlation in enumerate(correlations):
        i = 2 * block
        matrix_b[i, i + 1] = matrix_b[i + 1, i] = correlation
    mu = sp.Rational(29, 30)
    theta = n * (1 - mu)
    assert theta == sp.Rational(1, 5)

    increments = [sp.zeros(n) for _ in range(n)]
    orders = list(itertools.permutations(range(n)))
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
            increments[position] += embedded.T * embedded
    increments = [matrix / len(orders) for matrix in increments]

    inverse_b = matrix_b.inv()
    matrix_j = sp.zeros(n)
    records = []
    for t, increment in enumerate(increments, start=1):
        matrix_j += increment
        # theta=1/5 lies in the audited half-coefficient band, so use the
        # conservative rational c_theta=1/2 rather than an irrational bound.
        margin = sp.simplify(matrix_j - sp.Rational(t, 2 * n) * mu * inverse_b)
        passed, minimum_minor = all_principal_minors_nonnegative(margin)
        assert passed
        records.append(
            {"t": t, "target_coefficient": str(sp.Rational(t, 2 * n)), "minimum_principal_minor": str(minimum_minor)}
        )

    output = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact rational control of N8",
        "matrix": "three unequal signed 2x2 correlation blocks",
        "n": n,
        "mu": str(mu),
        "theta": str(theta),
        "orders": len(orders),
        "all_prefix_records": records,
        "result": "all exact principal-minor checks passed",
        "scope": "One finite control, not a proof of the quantified prefix statement.",
    }
    path = Path(
        "research/iteration5/route_a/evidence/uniform_band_prefix_control.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "result": output["result"]}, indent=2))


if __name__ == "__main__":
    main()
