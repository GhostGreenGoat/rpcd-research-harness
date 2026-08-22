"""Exact barrier to the *direct* adjacency regression.

Provenance is important: this file uses the dual test ``R_pi=D_pi.T``.  It
does not test the richer ``R_pi=D_pi.T @ D_pi`` certificate in
``weighted_adjacency_dual.md``.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def exact_barrier() -> dict[str, object]:
    n = 20
    mu = F(1, 2)
    rho = 1 - mu
    conditional = rho * mu

    trace_q = F(n) + conditional**2 * F((n - 1) * (n - 2), 2)
    parallel_sum_square = (
        F(n)
        + conditional * (n - 1) * (n - 2)
        + conditional**2 * F((n - 2) * (n - 1) * (2 * n - 3), 6)
    )
    q_parallel = parallel_sum_square / n
    q_transverse = (trace_q - q_parallel) / (n - 1)

    lambda_parallel = 1 + (n - 1) * rho
    p_transverse = F(n) + rho
    p_transverse /= n
    p_parallel = F(n) - (n - 1) * rho
    p_parallel /= n

    ratio_transverse = p_transverse**2 / q_transverse
    ratio_parallel = lambda_parallel * p_parallel**2 / (mu * q_parallel)
    gap = ratio_parallel - F(1, 2)
    assert ratio_transverse == F(1681, 1585)
    assert ratio_parallel == F(9261, 18985)
    assert gap == -F(463, 37970)
    return {
        "status": "exact counterexample to a restricted dual feature",
        "dual_test": "R_pi=D_pi^T (direct adjacency)",
        "explicitly_not_tested": "R_pi=D_pi^T D_pi (weighted adjacency frame)",
        "n": n,
        "mu": str(mu),
        "rho": str(rho),
        "conditional_covariance_entry": str(conditional),
        "trace_Q": str(trace_q),
        "q_parallel": str(q_parallel),
        "q_transverse": str(q_transverse),
        "p_parallel": str(p_parallel),
        "p_transverse": str(p_transverse),
        "certificate_over_mu_transverse": str(ratio_transverse),
        "certificate_over_mu_parallel": str(ratio_parallel),
        "parallel_gap_to_one_half": str(gap),
        "scope": (
            "Refutes only the direct immediate-adjacency regression and its "
            "Q inequality.  It does not refute J_s, H_s, K, the weighted "
            "D^T D feature, or the RPCD complexity conjecture."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_a/evidence/direct_adjacency_exact_barrier.json"
        ),
    )
    args = parser.parse_args()
    result = exact_barrier()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "status": result["status"]}, indent=2))


if __name__ == "__main__":
    main()
