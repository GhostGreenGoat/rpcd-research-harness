"""Exact reconstruction of the local-inverse Schur residual lemma/control."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


def main() -> None:
    vectors = [
        (sp.Rational(0), sp.Rational(1)),
        (sp.Rational(4, 5), sp.Rational(3, 5)),
        (sp.Rational(5, 13), sp.Rational(12, 13)),
        (sp.Rational(7, 25), sp.Rational(24, 25)),
        (sp.Rational(20, 29), sp.Rational(21, 29)),
    ]
    n = len(vectors)
    epsilon = sp.Rational(1, 100)
    gram = sp.Matrix(
        [
            [sum(vectors[i][z] * vectors[j][z] for z in range(2)) for j in range(n)]
            for i in range(n)
        ]
    )
    matrix_b = epsilon * sp.eye(n) + (1 - epsilon) * gram
    assert matrix_b.is_positive_definite

    q = 2
    best = None
    minimum_sharpened_gap = None
    checks = 0
    for order in itertools.permutations(range(n)):
        ordered_b = matrix_b.extract(order, order)
        matrix_m = sp.eye(n)
        for i in range(n):
            for j in range(i):
                matrix_m[i, j] = ordered_b[i, j]

        for k in range(n):
            start = max(0, k - q)
            recent = list(range(start, k + 1))
            old = list(range(start))
            local_m = matrix_m.extract(recent, recent)
            row_d = local_m.inv()[-1, :]
            local_b = ordered_b.extract(recent, recent)
            sigma = sp.factor((row_d * local_b * row_d.T)[0])
            norm_squared = sp.factor((row_d * row_d.T)[0])
            assert sp.factor(sigma - (2 - norm_squared)) == 0
            assert sigma > 0 and sigma <= 1

            if old:
                residual = row_d * ordered_b.extract(recent, old)
                old_b = ordered_b.extract(old, old)
                captured = sp.factor((residual * old_b.inv() * residual.T)[0])
                assert captured <= sigma
                sharpened_gap = sp.factor(sigma - epsilon * norm_squared - captured)
                assert sharpened_gap >= 0
                assert captured <= 1 - epsilon
                if minimum_sharpened_gap is None or sharpened_gap < minimum_sharpened_gap:
                    minimum_sharpened_gap = sharpened_gap
                ratio = sp.factor(captured / sigma)
                if best is None or ratio > best[0]:
                    best = (ratio, order, k, sigma, captured, len(old))
            checks += 1

    assert best is not None and minimum_sharpened_gap is not None
    ratio, order, k, sigma, captured, old_size = best
    expected = sp.Rational(96509036395663477402608, 104696053844535508536025)
    assert ratio == expected
    assert ratio > sp.Rational(9, 10) > sp.Rational(old_size, n)

    output = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact rational reconstruction/control",
        "matrix": "epsilon lift of the displayed five-vector rational Gram matrix",
        "epsilon": str(epsilon),
        "q": q,
        "pathwise_rows_checked": checks,
        "schur_residual_inequality": "pass for every order and row in this control",
        "spectral_floor_strengthening": {
            "mu": str(epsilon),
            "inequality": "captured <= sigma-mu*||d||^2 <= 1-mu",
            "minimum_exact_gap": str(minimum_sharpened_gap),
            "checks": "passed",
        },
        "strong_fractional_bound": {
            "result": "refuted",
            "order": list(order),
            "row_zero_based": k,
            "old_size": old_size,
            "ratio": str(ratio),
            "sigma": str(sigma),
            "captured": str(captured),
            "old_fraction": str(sp.Rational(old_size, n)),
        },
        "scope": "The general Schur lemma is algebraic; the failed strengthening is one exact control.",
    }
    path = Path(
        "research/iteration5/route_a/evidence/local_inverse_schur_residual.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "checks": "passed"}, indent=2))


if __name__ == "__main__":
    main()
