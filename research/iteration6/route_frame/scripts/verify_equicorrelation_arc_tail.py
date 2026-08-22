"""Exact finite controls for the equicorrelation arc-tail formulas."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def case(n: int, rho: sp.Rational) -> dict[str, object]:
    q = (n + 1) // 2
    m = n - q - 1
    mu = 1 - rho
    c0 = rho * mu**q

    cyclic_d = sp.zeros(n)
    for current in range(n):
        cyclic_d[current, current] = 1
        for lag in range(1, q + 1):
            cyclic_d[current, (current - lag) % n] = -rho * mu ** (lag - 1)

    matrix_s = sp.zeros(n)
    for successor in range(n):
        for start in range(1, m + 1):
            row = sp.zeros(1, n)
            for distance in range(start, m + 1):
                predecessor = (successor - distance) % n
                row += c0 * cyclic_d[predecessor, :]
            matrix_s += row.T * row / n

    ones = sp.ones(n, 1)
    parallel_s = sp.factor((ones.T * matrix_s * ones)[0] / n)
    sum_squares = sp.Rational(m * (m + 1) * (2 * m + 1), 6)
    expected_parallel = sp.factor(c0**2 * mu ** (2 * q) * sum_squares / n)
    assert parallel_s == expected_parallel

    # Linear-order local frame; its permutation average is exchangeable.
    linear_d = sp.eye(n)
    for current in range(n):
        for lag in range(1, min(current, q) + 1):
            linear_d[current, current - lag] = -rho * mu ** (lag - 1)
    parallel_p = sp.factor((linear_d * ones).dot(linear_d * ones) / n)
    transverse_p = sp.factor((sp.trace(linear_d.T * linear_d) - parallel_p) / (n - 1))
    transverse_s = sp.factor((sp.trace(matrix_s) - parallel_s) / (n - 1))
    if rho > 0:
        assert parallel_p >= mu ** (2 * q)
        assert transverse_p >= 1
        # Rational substitute 1/e^2 < 4/25 from e>5/2.
        assert parallel_s <= sp.Rational(4, 25) * parallel_p
        assert transverse_s <= sp.Rational(4, 25) * transverse_p
        bound = "S <= (4/25) P exact control for analytic S <= e^-2 P"
    else:
        spectral_mu = 1 + (n - 1) * rho
        assert spectral_mu > 0
        assert parallel_p >= 1
        assert transverse_p >= sp.Rational(1, 4)
        assert parallel_s <= 3 * parallel_p
        assert transverse_s <= 3 * transverse_p
        assert parallel_p >= sp.Rational(1, 4) * spectral_mu / spectral_mu
        assert transverse_p >= sp.Rational(1, 4) * spectral_mu / (1 - rho)
        bound = "S <= 3 P and P >= (mu/4) A^-1"
    return {
        "n": n,
        "rho": str(rho),
        "q": q,
        "m": m,
        "parallel_tail": str(parallel_s),
        "transverse_tail": str(transverse_s),
        "parallel_frame": str(parallel_p),
        "transverse_frame": str(transverse_p),
        "bound_checked": bound,
    }


def main() -> None:
    cases = []
    for n in range(4, 11):
        for rho in (sp.Rational(1, 10), sp.Rational(1, 2), sp.Rational(9, 10)):
            cases.append(case(n, rho))
        for rho in (
            -sp.Rational(1, 2 * (n - 1)),
            -sp.Rational(9, 10 * (n - 1)),
        ):
            cases.append(case(n, rho))
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for E3 family proof",
        "cases": cases,
        "result": "A9--A18 finite formulas passed exactly",
        "scope": "Signed equicorrelation validation, not a generic theorem.",
    }
    target = Path("research/iteration6/route_frame/evidence/equicorrelation_arc_tail.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
