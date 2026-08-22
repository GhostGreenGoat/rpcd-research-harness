"""Exact obstruction for the weighted adjacency feature R=D.T*D.

This is deliberately separate from direct_adjacency_equicorrelation_barrier.py,
which tests the different random feature R=D.T.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path


def certificate_blocks(n: int, rho: F) -> dict[str, F]:
    mu = 1 - rho
    ell = 1 + (n - 1) * rho
    diagonal_b2 = 1 + (n - 1) * rho**2

    p_perp = (n + 1 - 2 * mu + diagonal_b2) / n
    p_parallel = (n + 1 - 2 * ell + diagonal_b2) / n

    trace_q = (
        n
        + (n - 1) * rho**2
        + (n - 2) * rho**2 * mu**2 * (1 + rho**2)
        + F((n - 2) * (n - 3), 2) * rho**2 * mu**4
    )
    one_q_one = (
        (1 + (n - 2) * rho * mu**2) ** 2
        + (n - 1) * mu**2
        + (n - 3) * (n - 2) * rho * mu**3
        + F((n - 3) * (n - 2) * (2 * n - 5), 6) * rho**2 * mu**4
    )
    q_parallel = one_q_one / n
    q_perp = (trace_q - q_parallel) / (n - 1)

    normalized_perp = p_perp**2 / q_perp
    normalized_parallel = ell * p_parallel**2 / (mu * q_parallel)
    return {
        "mu": mu,
        "ell": ell,
        "p_perp": p_perp,
        "p_parallel": p_parallel,
        "trace_q": trace_q,
        "one_q_one": one_q_one,
        "q_perp": q_perp,
        "q_parallel": q_parallel,
        "normalized_perp": normalized_perp,
        "normalized_parallel": normalized_parallel,
        "parallel_gap_to_half": normalized_parallel - F(1, 2),
    }


def dense_reconstruction(n: int, rho: F) -> tuple[F, F]:
    """Rebuild tr(Q) and 1^TQ1 directly from exact dense matrices."""
    matrix_m = [
        [F(int(i == j)) + (rho if i > j else 0) for j in range(n)]
        for i in range(n)
    ]
    matrix_d = [
        [F(int(i == j)) - (rho if i == j + 1 else 0) for j in range(n)]
        for i in range(n)
    ]

    def transpose(a: list[list[F]]) -> list[list[F]]:
        return [list(row) for row in zip(*a)]

    def multiply(a: list[list[F]], b: list[list[F]]) -> list[list[F]]:
        bt = transpose(b)
        return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]

    matrix_r = multiply(transpose(matrix_d), matrix_d)
    matrix_f = multiply(matrix_r, matrix_m)
    matrix_q = multiply(matrix_f, transpose(matrix_f))
    return sum(matrix_q[i][i] for i in range(n)), sum(map(sum, matrix_q))


def main() -> None:
    n = 50
    rho = F(1, 10)
    values = certificate_blocks(n, rho)
    dense_trace, dense_one = dense_reconstruction(n, rho)
    assert dense_trace == values["trace_q"]
    assert dense_one == values["one_q_one"]
    assert values["normalized_perp"] == F(1259043289, 1225885468)
    assert values["normalized_parallel"] == F(75142223, 160062876)
    assert values["parallel_gap_to_half"] == -F(4889215, 160062876)

    output = {
        "schema_version": "1.0",
        "evidence_level": "E2 exact rational counterexample to D14",
        "feature": "weighted adjacency R_pi=D_pi^T D_pi",
        "not_feature": "direct adjacency R_pi=D_pi^T",
        "matrix": {"n": n, "rho": str(rho), "family": "positive equicorrelation"},
        "values": {name: str(value) for name, value in values.items()},
        "dense_formula_reconstruction": "pass",
        "conclusion": (
            "The optimal dual-regression certificate for this R_pi has "
            "normalized parallel eigenvalue below 1/2. This refutes D14, "
            "not the RPCD half-prefix conjecture."
        ),
    }
    path = Path(
        "research/iteration5/route_a/evidence/"
        "weighted_adjacency_exact_barrier.json"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "result": "exact counterexample"}, indent=2))


if __name__ == "__main__":
    main()
