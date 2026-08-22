"""Exact regression checks for the independent linear-memory audit."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/iteration5/route_c/evidence/LINEAR_MEMORY_AUDIT.json"


def matrices(n: int, rho: Fraction, q: int):
    mu = 1 - rho
    m = [[Fraction(int(i == j)) + (rho if i > j else 0) for j in range(n)] for i in range(n)]
    d = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        d[i][i] = 1
        for j in range(max(0, i - q), i):
            d[i][j] = -rho * mu ** (i - j - 1)
    product = [
        [sum(d[i][k] * m[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]
    return mu, d, product


def check_dimension(n: int) -> dict[str, object]:
    rho = Fraction(2, 7)
    q = (n + 1) // 2
    mu, d, product = matrices(n, rho, q)
    defect_ok = all(
        product[i][j]
        == (
            Fraction(int(i == j))
            + (rho * mu**q if i - j > q else 0)
        )
        for i in range(n)
        for j in range(n)
    )
    row_sums = [sum(row) for row in d]
    expected_rows = [mu ** min(q, i) for i in range(n)]
    s_q = sum(mu ** (2 * j) for j in range(q))
    z = mu ** (2 * q)
    ell = n - (n - 1) * mu
    identity_left = ell * s_q / (n * mu)
    identity_right = s_q / n + (1 - z) / (mu * (1 + mu))
    lower = z / (2 * mu**2) + (1 - z) / (mu * (1 + mu))
    assert defect_ok
    assert row_sums == expected_rows
    assert identity_left == identity_right
    assert lower >= Fraction(1, 2)
    assert n - q - 1 <= q
    return {
        "n": n,
        "q": q,
        "parity": "even" if n % 2 == 0 else "odd",
        "exact_defect_identity": True,
        "exact_row_sums": True,
        "L17_identity": True,
        "L17_lower_bound": str(lower),
        "tail_row_column_bound": n - q - 1,
    }


def main() -> None:
    records = [check_dimension(n) for n in range(2, 11)]
    result = {
        "evidence_level": "E2 exact finite regression; analytic proof is in the audit note",
        "rho": "2/7",
        "dimensions": records,
        "checks": "PASS",
        "scope": "positive equicorrelation only",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
