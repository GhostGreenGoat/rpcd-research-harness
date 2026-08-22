"""Exact controls for the pathwise triangular-projection barrier."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def hilbert_skew(a: int) -> sp.Matrix:
    return sp.Matrix(
        [[sp.Rational(0) if i == j else sp.Rational(1, i - j) for j in range(a)] for i in range(a)]
    )


def build_case(a: int) -> dict[str, object]:
    tau = sp.Rational(1, 4)
    matrix_c = hilbert_skew(a)
    matrix_a = sp.eye(2 * a)
    matrix_a[:a, a:] = tau * matrix_c.T
    matrix_a[a:, :a] = tau * matrix_c
    assert matrix_a.is_positive_definite

    matrix_m = sp.eye(2 * a)
    matrix_m[a:, :a] = tau * matrix_c
    matrix_d = sp.eye(2 * a)
    upper = sp.zeros(a)
    lower = sp.zeros(a)
    for i in range(a):
        for j in range(a):
            if j >= i:
                upper[i, j] = matrix_c[i, j]
            else:
                lower[i, j] = matrix_c[i, j]
    matrix_d[a:, :a] = -tau * upper
    matrix_e = sp.simplify(matrix_d * matrix_m)
    expected_e = sp.eye(2 * a)
    expected_e[a:, :a] = tau * lower
    assert matrix_e == expected_e

    # Q/R reduces to the Rayleigh quotient of E E^T.  Hence y must be
    # supported on the late block so that E^T y exposes G^T 1.
    vector_y = sp.Matrix([0] * a + [1] * a)
    quotient = sp.factor((vector_y.T * matrix_e * matrix_e.T * vector_y)[0] / a)
    harmonic_sum = sum(sum(sp.Rational(1, j) for j in range(1, r)) ** 2 for r in range(1, a + 1))
    expected = sp.factor(1 + tau**2 * harmonic_sum / a)
    assert quotient == expected

    matrix_r = matrix_d.T * matrix_d
    matrix_q = matrix_d.T * matrix_e * matrix_e.T * matrix_d
    vector_x = matrix_d.inv() * vector_y
    generalized = sp.factor((vector_x.T * matrix_q * vector_x)[0] / (vector_x.T * matrix_r * vector_x)[0])
    assert generalized == expected
    return {
        "a": a,
        "dimension": 2 * a,
        "q": a,
        "exact_rayleigh": str(expected),
        "decimal_rayleigh": float(expected),
    }


def main() -> None:
    cases = [build_case(a) for a in [2, 3, 4, 6, 8, 12]]
    output = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for an E3 pathwise barrier",
        "family": "bipartite skew-Hilbert, tau=1/4, group-ordered permutation",
        "cases": cases,
        "result": "all exact identities and SPD checks passed",
        "scope": "Refutes only a pathwise Q_pi<=Gamma R_pi comparison.",
    }
    path = Path(
        "research/iteration6/route_frame/evidence/pathwise_triangular_barrier.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "result": output["result"]}, indent=2))


if __name__ == "__main__":
    main()
