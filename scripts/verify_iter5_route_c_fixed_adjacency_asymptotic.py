"""Independent exact audit of the fixed-adjacency equicorrelation decay."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/iteration5/route_c/evidence/FIXED_ADJACENCY_DECAY.json"


def formula(n: int, rho: Fraction) -> dict[str, Fraction]:
    mu = 1 - rho
    ell = 1 + (n - 1) * rho
    p_parallel = (1 + (n - 1) * mu**2) / n
    s0 = (
        (1 + (n - 2) * rho * mu**2) ** 2
        + (n - 1) * mu**2
        + (n - 3) * (n - 2) * rho * mu**3
        + Fraction((n - 3) * (n - 2) * (2 * n - 5), 6)
        * rho**2
        * mu**4
    )
    q_parallel = s0 / n
    normalized = ell * p_parallel**2 / (mu * q_parallel)
    return {
        "ell": ell,
        "p_parallel": p_parallel,
        "q_parallel": q_parallel,
        "normalized_parallel": normalized,
    }


def dense(n: int, rho: sp.Rational) -> tuple[sp.Rational, sp.Rational]:
    lower = sp.zeros(n)
    shift = sp.zeros(n)
    for i in range(n):
        for j in range(i):
            lower[i, j] = 1
        if i:
            shift[i, i - 1] = 1
    m = sp.eye(n) + rho * lower
    d = sp.eye(n) - rho * shift
    r = d.T * d
    f = r * m
    ones = sp.ones(n, 1)
    p_parallel = sp.factor((ones.T * r * ones)[0] / n)
    q_parallel = sp.factor((ones.T * f * f.T * ones)[0] / n)
    return p_parallel, q_parallel


def main() -> None:
    rho = Fraction(1, 10)
    dense_checks = []
    for n in range(3, 9):
        expected = formula(n, rho)
        p_dense, q_dense = dense(n, sp.Rational(1, 10))
        check = (
            p_dense == sp.Rational(expected["p_parallel"].numerator, expected["p_parallel"].denominator)
            and q_dense == sp.Rational(expected["q_parallel"].numerator, expected["q_parallel"].denominator)
        )
        dense_checks.append({"n": n, "exact_match": bool(check)})
        assert check

    n500 = formula(500, rho)["normalized_parallel"]
    assert n500 == Fraction(835670784749, 13025285081505)
    assert n500 < Fraction(1, 8)
    result = {
        "evidence_level": "E2 finite checks plus exact rational asymptotic derivation in audit note",
        "rho": "1/10",
        "mu": "9/10",
        "dense_identity_order_checks": dense_checks,
        "n_500_normalized_parallel": str(n500),
        "n_500_below_one_eighth": True,
        "symbolic_limit": "lim n*c_n = 3/(rho*(1-rho)); hence c_n -> 0",
        "scope": "fixed weighted-adjacency dual feature only; not RPCD itself",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
