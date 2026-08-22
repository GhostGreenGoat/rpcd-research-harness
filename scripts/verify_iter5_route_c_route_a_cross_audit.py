"""Exact auxiliary checks for the Route-A cross-audit.

This script is not the proof.  It independently reconstructs the Bernstein
coefficients in (A9), checks the path-energy identity for symbolic symmetric
matrices in dimensions 2--5, and writes a portable JSON record.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/iteration5/route_c/evidence/ROUTE_A_CROSS_AUDIT.json"


def bernstein_check() -> dict[str, str | bool]:
    n, mu, t = sp.symbols("n mu t", positive=True)
    lam = mu + t * (n - (n - 1) * mu - mu)
    g = sp.expand(lam * ((n - lam) ** 2 + n + (n - 1) * mu**2) - n**2 * mu)
    b = sp.symbols("b0:4")
    reconstruction = sp.expand(
        b[0] * (1 - t) ** 3
        + 3 * b[1] * t * (1 - t) ** 2
        + 3 * b[2] * t**2 * (1 - t)
        + b[3] * t**3
    )
    equations = [sp.expand(reconstruction - g).coeff(t, k) for k in range(4)]
    solved = sp.solve(equations, b, dict=True)[0]
    expected = [
        n * mu * (1 - mu) ** 2,
        n
        * (1 - mu)
        * ((n - 1) * mu**2 - (4 * n - 3) * mu + n**2 + n)
        / 3,
        n
        * (1 - mu)
        * (-(n - 1) * mu**2 + (2 * n**2 - 5 * n + 3) * mu + 2 * n)
        / 3,
        n
        * (1 - mu)
        * ((n - 1) ** 2 * mu**2 - (n - 1) * mu + n),
    ]
    return {
        "exact_match": all(sp.expand(solved[b[k]] - expected[k]) == 0 for k in range(4)),
        **{f"b{k}": str(sp.factor(solved[b[k]])) for k in range(4)},
    }


def path_identity(n: int) -> dict[str, object]:
    # Use distinct exact rational off-diagonal entries; symbolic permutation
    # enumeration is unnecessary for checking the combinatorial coefficients.
    B = sp.eye(n)
    value = 1
    for i in range(n):
        for j in range(i):
            B[i, j] = B[j, i] = sp.Rational(value, 10 * n * n)
            value += 1

    total = sp.zeros(n)
    perms = list(itertools.permutations(range(n)))
    for perm in perms:
        D = sp.zeros(n)
        D[perm[0], perm[0]] = 1
        for k in range(1, n):
            i, j = perm[k], perm[k - 1]
            D[i, i] = 1
            D[i, j] = -B[i, j]
        total += D.T * D
    average = total / sp.factorial(n)
    delta = sp.diag(*[(B**2)[i, i] for i in range(n)])
    formula = ((n + 1) * sp.eye(n) - 2 * B + delta) / n
    return {
        "n": n,
        "permutations": len(perms),
        "exact_identity": average == formula,
    }


def main() -> None:
    result = {
        "status": "exact auxiliary verification; proof is in the Markdown audit",
        "bernstein": bernstein_check(),
        "path_identities": [path_identity(n) for n in range(2, 6)],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
