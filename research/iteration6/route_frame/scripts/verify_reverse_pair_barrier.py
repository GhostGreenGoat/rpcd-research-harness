"""Exact finite controls for the reverse-pair Hilbert barrier."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


def skew_hilbert(a: int) -> sp.Matrix:
    return sp.Matrix(
        [[0 if i == j else sp.Rational(1, i - j) for j in range(a)] for i in range(a)]
    )


def case(a: int) -> dict[str, object]:
    tau = sp.Rational(1, 4)
    c = skew_hilbert(a)
    g = sp.zeros(a)
    for i in range(a):
        for j in range(i):
            g[i, j] = c[i, j]
    assert c - g == -g.T

    d = sp.eye(2 * a)
    e = sp.eye(2 * a)
    d[a:, :a] = tau * g.T
    e[a:, :a] = tau * g
    d_rev = d.T
    e_rev = e.T

    u = sp.ones(a, 1)
    x = u.col_join(sp.zeros(a, 1))
    h = g.T * u
    k = g.T * h
    r_pair = d.T * d + d_rev.T * d_rev
    q_pair = d.T * e * e.T * d + d_rev.T * e_rev * e_rev.T * d_rev
    denominator = sp.factor((x.T * r_pair * x)[0])
    numerator = sp.factor((x.T * q_pair * x)[0])
    expected_denominator = sp.factor(2 * a + tau**2 * (h.T * h)[0])
    expected_first = (u + tau**2 * k).dot(u + tau**2 * k) + tau**2 * h.dot(h)
    expected_second = u.dot(u) + tau**2 * (g * u).dot(g * u)
    assert denominator == expected_denominator
    assert numerator == sp.factor(expected_first + expected_second)
    assert numerator >= tau**4 * k.dot(k)
    return {
        "a": a,
        "dimension": 2 * a,
        "denominator": str(denominator),
        "numerator": str(numerator),
        "rayleigh_decimal": float(numerator / denominator),
        "tau4_k2_lower_decimal": float(tau**4 * k.dot(k) / denominator),
    }


def main() -> None:
    payload = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact controls for the E3 reverse-pair barrier",
        "cases": [case(a) for a in (4, 8, 12, 16)],
        "result": "all exact paired identities passed",
        "scope": "Refutes reverse-pair covariance/frame comparison only.",
    }
    target = Path("research/iteration6/route_frame/evidence/reverse_pair_barrier.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "result": payload["result"]}, indent=2))


if __name__ == "__main__":
    main()
