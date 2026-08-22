"""Independent exact audit of the Iteration-5 equicorrelation prefix proof.

This reconstruction deliberately does not import the source verifier.  It
checks the Bellman recurrence against chronological triangular solves, the
positive-correlation polynomial identity, the negative-correlation pathwise
lower bound, and the rho=0 endpoint.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path

import sympy as sp


def chronological_energy(
    n: int, steps: int, rho: F, right: tuple[F, ...]
) -> F:
    total = F(0)
    count = 0
    for order in itertools.permutations(range(n)):
        running = F(0)
        energy = F(0)
        for coordinate in order[:steps]:
            solve = right[coordinate] - rho * running
            running += solve
            energy += solve * solve
        total += energy
        count += 1
    return total / count


def brute_blocks(n: int, steps: int, rho: F) -> tuple[F, F]:
    transverse = (F(1), F(-1), *(F(0) for _ in range(n - 2)))
    parallel = tuple(F(1) for _ in range(n))
    return (
        chronological_energy(n, steps, rho, transverse) / 2,
        chronological_energy(n, steps, rho, parallel) / n,
    )


def independent_recurrence(n: int, steps: int, rho: F) -> tuple[F, F]:
    # Base at the remaining size n-steps, followed by exactly `steps` lifts.
    a = F(0)
    p = F(0)
    for k in range(n - steps + 1, n + 1):
        old_a, old_p = a, p
        parent_parallel = F(1, k) + F(k - 1, k) * (1 - rho) ** 2 * old_p

        # Non-special first pivots contribute (k-2)/k * old_a.  The two
        # special pivots jointly add another (k-2)/(k(k-1))*old_a and the
        # parallel component below.  Their sum is (k-2)/(k-1).
        parent_lambda = 1 + (k - 1) * rho
        parent_transverse = (
            F(1, k)
            + F(k - 2, k - 1) * old_a
            + parent_lambda**2 * old_p / F(k * (k - 1))
        )
        a, p = parent_transverse, parent_parallel
    return a, p


def symbolic_positive_identity() -> str:
    s, delta = sp.symbols("s delta", integer=True, positive=True)
    lhs = (1 + 2 * (s - 1) * delta) * (2 + (2 * s + 1) * delta)
    rhs = (1 - delta) * (2 - delta) * (
        1 + s * delta * (2 + (2 * s + 1) * delta)
    )
    claimed = delta * (
        2 * s
        + (2 * s - 3) * delta
        + s * (6 * s + 1) * delta**2
        - s * (2 * s + 1) * delta**3
    )
    assert sp.expand(lhs - rhs - claimed) == 0
    return str(sp.factor(claimed))


def audit_records(max_n: int) -> dict[str, object]:
    records: list[dict[str, object]] = []
    for n in range(2, max_n + 1):
        # Include rho=0 explicitly; the analytic geometric-quotient formula
        # must be interpreted separately there rather than divided by rho.
        correlations = [F(0), F(2, 5), -F(1, 3 * (n - 1))]
        for steps in range(1, (n + 1) // 2 + 1):
            # The source proof only uses n>=2*steps-1 and therefore claims all
            # of these prefix depths simultaneously, not merely the endpoint.
            assert n >= 2 * steps - 1
            for rho in correlations:
                brute = brute_blocks(n, steps, rho)
                recurrence = independent_recurrence(n, steps, rho)
                assert brute == recurrence
                alpha = 1 - rho
                parallel_lambda = 1 + (n - 1) * rho
                mu = min(alpha, parallel_lambda)
                target = F(steps, n) * mu
                transverse_margin = alpha * brute[0] - target
                parallel_margin = parallel_lambda * brute[1] - target
                assert transverse_margin >= 0
                assert parallel_margin >= 0
                if rho == 0:
                    assert brute == (F(steps, n), F(steps, n))
                    assert transverse_margin == parallel_margin == 0
                records.append(
                    {
                        "n": n,
                        "steps": steps,
                        "rho": str(rho),
                        "transverse": str(brute[0]),
                        "parallel": str(brute[1]),
                        "transverse_margin": str(transverse_margin),
                        "parallel_margin": str(parallel_margin),
                        "orders": math.factorial(n),
                    }
                )

    # Direct exact checks of the negative-rho path estimate over every possible
    # gap ell for a denser finite grid.  These are controls, not the general
    # quantified proof.
    negative_path_checks = 0
    for n in range(3, 31):
        beta = F(1, 2 * (n - 1))
        alpha = 1 + beta
        for ell in range(n - 1):
            assert (1 - beta * alpha**ell) ** 2 >= 1 - 2 * beta * alpha ** (n - 2)
            negative_path_checks += 1

    return {
        "schema_version": "1.0",
        "evidence_level": "E4 hostile-audit reconstruction of an E3 family proof",
        "result": (
            "pass simultaneously for every 1<=steps<=ceil(n/2), after "
            "explicitly separating rho=0"
        ),
        "max_permutation_dimension": max_n,
        "records": records,
        "positive_polynomial_factorization": symbolic_positive_identity(),
        "negative_path_checks": negative_path_checks,
        "scope": (
            "All equicorrelation matrices only.  This proves no assertion for "
            "a general correlation matrix and does not decide C001."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-n", type=int, default=7)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/iteration5/route_a/evidence/equicorrelation_hostile_audit.json"
        ),
    )
    args = parser.parse_args()
    result = audit_records(args.max_n)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "result": result["result"]}, indent=2))


if __name__ == "__main__":
    main()
