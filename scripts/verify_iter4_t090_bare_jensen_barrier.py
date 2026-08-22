"""Exact full-matrix audit of the bare Jensen half-constant barrier."""

from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path


def matmul(left, right):
    n = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def matvec(matrix, vector):
    return [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]


def build(n, mu):
    identity = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    matrix = [
        [mu * identity[i][j] + (1 - mu) for j in range(n)] for i in range(n)
    ]
    h = [[matrix[i][j] - identity[i][j] for j in range(n)] for i in range(n)]
    h_squared = matmul(h, h)
    s = [
        [h_squared[i][j] / 3 + (h_squared[i][i] / 6 if i == j else 0) for j in range(n)]
        for i in range(n)
    ]
    return matrix, s


def main():
    n = 12
    mu = F(1, 100)
    matrix, s = build(n, mu)
    u = [F(1), F(-1)] + [F(0)] * (n - 2)
    s_transverse = F(42471, 20000)
    assert matvec(matrix, u) == [mu * value for value in u]
    assert matvec(s, u) == [s_transverse * value for value in u]

    # The desired implication from the bare Jensen certificate would require
    # mu(A+S)<=2A.  Its transverse residual is strictly negative.
    residual_eigenvalue = 2 * mu - mu * (mu + s_transverse)
    assert residual_eigenvalue == -F(2671, 2000000)
    assert residual_eigenvalue < 0
    jensen_gamma_over_mu = F(1) / (mu + s_transverse)
    assert jensen_gamma_over_mu == F(20000, 42671)
    assert jensen_gamma_over_mu - F(1, 2) == -F(2671, 85342)

    output = {
        "status": "independent exact full-matrix bare Jensen barrier",
        "evidence_level": "E3 exact rational reconstruction",
        "family": "A=mu I+(1-mu)J_n",
        "n": n,
        "mu": str(mu),
        "direction": [int(value) for value in u],
        "A_eigenvalue": str(mu),
        "S_eigenvalue": str(s_transverse),
        "eigenvalue_of_2A_minus_mu_times_A_plus_S": str(residual_eigenvalue),
        "Jensen_gamma_over_mu": str(jensen_gamma_over_mu),
        "gap_to_one_half": str(jensen_gamma_over_mu - F(1, 2)),
        "scope": (
            "Refutes the bare Jensen implication at constant 1/2; does not refute "
            "the actual K(A)>=(mu/2)A^{-1} candidate."
        ),
        "arithmetic": "Fraction full 12-by-12 matrix multiplication",
    }
    path = Path("research/evidence/ITER4_T090_BARE_JENSEN_EXACT_BARRIER.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "residual": str(residual_eigenvalue)}, indent=2))


if __name__ == "__main__":
    main()
