"""Exact and asymptotic controls for a q-step local-inverse dual state."""

from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path


def blocks(n: int, rho: F, q: int) -> dict[str, F]:
    """Exact exchangeable blocks for weighted R=D_q^T D_q.

    D_q keeps the exact equicorrelation inverse coefficients at the q most
    recent positions.  No permutation enumeration is needed because averaging
    conjugates one canonical order into an exchangeable matrix.
    """
    assert 0 <= q <= n - 1
    mu = 1 - rho
    ell = 1 + (n - 1) * rho
    residual = rho * mu**q

    # D[i,j] is nonzero on the diagonal and the q subdiagonals.
    matrix_d = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix_d[i][i] = 1
        for distance in range(1, min(q, i) + 1):
            matrix_d[i][i - distance] = -rho * mu ** (distance - 1)

    # E=D M is I plus a constant residual below the q-th subdiagonal.
    matrix_e = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix_e[i][i] = 1
        for j in range(max(0, i - q)):
            matrix_e[i][j] = residual

    row_sums_d = [sum(row) for row in matrix_d]
    trace_p_order = sum(value * value for row in matrix_d for value in row)
    p_parallel = sum(value * value for value in row_sums_d) / n
    p_perp = (trace_p_order - p_parallel) / (n - 1)

    # q_parallel=||E^T D1||^2/n.
    e_transpose_d1 = [
        sum(matrix_e[i][j] * row_sums_d[i] for i in range(n))
        for j in range(n)
    ]
    q_parallel = sum(value * value for value in e_transpose_d1) / n

    # trace(Q_order)=||D^T E||_F^2.  Exploit the q-band of D.
    trace_q_order = F(0)
    for i in range(n):
        for j in range(n):
            value = sum(
                matrix_d[k][i] * matrix_e[k][j]
                for k in range(i, min(n, i + q + 1))
            )
            trace_q_order += value * value
    q_perp = (trace_q_order - q_parallel) / (n - 1)

    normalized_perp = p_perp**2 / q_perp
    normalized_parallel = ell * p_parallel**2 / (mu * q_parallel)
    return {
        "mu": mu,
        "ell": ell,
        "p_perp": p_perp,
        "p_parallel": p_parallel,
        "q_perp": q_perp,
        "q_parallel": q_parallel,
        "normalized_perp": normalized_perp,
        "normalized_parallel": normalized_parallel,
        "minimum_normalized": min(normalized_perp, normalized_parallel),
    }


def half_linear_limit(c: float) -> tuple[float, float, float]:
    """Parallel block limit for rho=c/n and q/n -> 1/2."""
    exponential = math.exp(-c)
    p = (1 + (c - 1) * exponential) / (2 * c)
    q_value = (
        (1 - exponential) / (2 * c)
        + 1.5 * exponential
        - 2 * exponential * (1 - math.exp(-c / 2)) / c
        + c * c * exponential * exponential / 24
    )
    return (1 + c) * p * p / q_value, p, q_value


def main() -> None:
    exact_cases = []
    for n, rho, q in [
        (20, F(1, 4), 1),
        (50, F(1, 10), 1),
        (24, F(1, 6), 12),
        (60, F(1, 60), 30),
        (60, F(1, 12), 30),
        (60, F(1, 6), 30),
    ]:
        result = blocks(n, rho, q)
        exact_cases.append(
            {
                "n": n,
                "rho": str(rho),
                "q": q,
                **{name: str(value) for name, value in result.items()},
            }
        )

    # Exact q=1 provenance check against the independent D18 verifier.
    q1 = blocks(50, F(1, 10), 1)
    assert q1["normalized_perp"] == F(1259043289, 1225885468)
    assert q1["normalized_parallel"] == F(75142223, 160062876)

    # These selected rational controls support, but do not prove, the q=n/2
    # finite-dimensional inequality.
    for case in exact_cases[2:]:
        assert F(case["minimum_normalized"]) > F(1, 2)

    limit_scan = []
    minimum = (float("inf"), 0.0)
    for exponent_index in range(-8000, 10001):
        c = math.exp(exponent_index / 1000)
        value, p_value, q_value = half_linear_limit(c)
        if value < minimum[0]:
            minimum = (value, c)
        if exponent_index in {-6000, -3000, 0, 1000, 2000, 4000, 8000}:
            limit_scan.append(
                {"c": c, "certificate": value, "p": p_value, "q": q_value}
            )

    output = {
        "schema_version": "1.0",
        "evidence_level": (
            "E2 exact identities and rational controls; E1 scan for the "
            "half-band continuum inequality"
        ),
        "feature": "q-step local inverse, weighted R_pi=D_q^T D_q",
        "exact_cases": exact_cases,
        "sublinear_limit": {
            "rho_scaling": "rho=c/n, q=o(n)",
            "parallel_certificate": "(1+c)/(1+c+c^2/3)",
            "below_half_when": "c>(3+sqrt(21))/2",
        },
        "half_linear_limit": {
            "rho_scaling": "rho=c/n, q/n->1/2",
            "scan_minimum": minimum[0],
            "at_c": minimum[1],
            "samples": limit_scan,
            "status": "no violation in log scan; this is not a proof",
        },
        "scope": (
            "This concerns the dual certificate on positive equicorrelation "
            "matrices, not general B and not the actual RPCD inequality."
        ),
    }
    path = Path(
        "research/iteration5/route_a/evidence/linear_memory_equicorrelation.json"
    )
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "result": "complete"}, indent=2))


if __name__ == "__main__":
    main()
