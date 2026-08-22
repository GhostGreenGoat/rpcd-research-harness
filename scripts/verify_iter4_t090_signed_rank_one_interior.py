"""Independent exact audit of the signed-rank-one interior obstruction.

For A=mu I+(1-mu) J, the parallel vector is solved by every triangular
factor as (1,mu,...,mu^(n-1)) in permutation order.  The resulting parallel
eigenvalue gives an upper bound on

    gamma(A)=lambda_min(A^(1/2) K(A) A^(1/2)).

At n=9, mu=9/10 we also reconstruct the transverse eigenvalue by a separate
two-labelled-coordinate category recurrence, proving that the parallel value
is the actual minimum in that finite example.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path


def parallel_solve(n: int, mu: Fraction) -> list[Fraction]:
    off_diagonal = 1 - mu
    previous_sum = Fraction(0)
    values = []
    for _ in range(n):
        value = 1 - off_diagonal * previous_sum
        values.append(value)
        previous_sum += value
    return values


def audit_labelled_permutation_orientation() -> int:
    """Generic labelled solve for all 5! orders, independent of the scalar recurrence."""
    n = 5
    mu = Fraction(2, 3)
    off_diagonal = 1 - mu
    matrix = [
        [Fraction(1) if row == column else off_diagonal for column in range(n)]
        for row in range(n)
    ]
    right_side = [Fraction(1)] * n
    count = 0
    for order in permutations(range(n)):
        solution = [Fraction(0)] * n
        visited: list[int] = []
        for power, current in enumerate(order):
            solution[current] = right_side[current] - sum(
                matrix[current][previous] * solution[previous] for previous in visited
            )
            assert solution[current] == mu**power
            visited.append(current)
        for current in range(n):
            position = order.index(current)
            reconstructed = solution[current] + sum(
                matrix[current][previous] * solution[previous]
                for previous in order[:position]
            )
            assert reconstructed == 1
        count += 1
    assert count == 120
    return count


def transverse_category_energy(
    n: int, mu: Fraction, plus_position: int, minus_position: int
) -> Fraction:
    """Solve e_1-e_2 with all off-diagonal entries equal to 1-mu."""
    off_diagonal = 1 - mu
    previous_sum = Fraction(0)
    energy = Fraction(0)
    for position in range(n):
        right_side = (
            Fraction(1)
            if position == plus_position
            else Fraction(-1)
            if position == minus_position
            else Fraction(0)
        )
        value = right_side - off_diagonal * previous_sum
        previous_sum += value
        energy += value * value
    return energy


def transverse_kappa(n: int, mu: Fraction) -> Fraction:
    total = Fraction(0)
    count = 0
    for plus_position in range(n):
        for minus_position in range(n):
            if plus_position == minus_position:
                continue
            total += transverse_category_energy(n, mu, plus_position, minus_position)
            count += 1
    assert count == n * (n - 1)
    # Average and divide by ||e_1-e_2||^2=2.
    return total / count / 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/evidence/ITER4_T090_SIGNED_RANK_ONE_INTERIOR_AUDIT_2026_08_21.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    labelled_orders_checked = audit_labelled_permutation_orientation()
    n = 9
    mu = Fraction(9, 10)

    solve = parallel_solve(n, mu)
    claimed_solve = [mu**power for power in range(n)]
    assert solve == claimed_solve
    parallel_kappa_from_solve = sum(value * value for value in solve) / n
    parallel_kappa_closed = (1 - mu ** (2 * n)) / (n * (1 - mu * mu))
    assert parallel_kappa_from_solve == parallel_kappa_closed

    parallel_a = n - (n - 1) * mu
    transverse_a = mu
    assert parallel_a > transverse_a
    parallel_gamma = parallel_a * parallel_kappa_closed

    transverse_k = transverse_kappa(n, mu)
    transverse_gamma = transverse_a * transverse_k
    gamma = min(parallel_gamma, transverse_gamma)
    assert gamma == parallel_gamma
    assert gamma == Fraction(44731861300157941, 50000000000000000)
    assert gamma < mu

    ratio = gamma / mu
    gap_to_one = ratio - 1
    assert gap_to_one < 0

    payload = {
        "status": "independent exact rational audit of the signed-rank-one interior obstruction",
        "evidence_level": "E4 hostile audit artifact",
        "family": "A=mu*I+(1-mu)*J_n",
        "orientation": (
            "For order pi, M_pi is lower in permutation order and solves "
            "y_pi[k]=1-(1-mu)*sum_(l<k)y_pi[l]."
        ),
        "generic_labelled_orientation_orders_checked": labelled_orders_checked,
        "general_formulae": {
            "parallel_solve_in_order": "(1,mu,...,mu^(n-1))",
            "parallel_K_eigenvalue": "(1-mu^(2n))/(n*(1-mu^2))",
            "parallel_A_eigenvalue": "n-(n-1)*mu",
            "gamma_upper_bound": (
                "[n-(n-1)*mu]*(1-mu^(2n))/(n*(1-mu^2))"
            ),
            "iterated_ratio_limit": (
                "lim_(mu up to 1) lim_(n to infinity) gamma(A)/mu <= 1/2"
            ),
        },
        "exact_finite_instance": {
            "n": n,
            "mu": str(mu),
            "lambda_min_A": str(mu),
            "parallel_A_eigenvalue": str(parallel_a),
            "parallel_K_eigenvalue": str(parallel_kappa_closed),
            "transverse_K_eigenvalue": str(transverse_k),
            "parallel_gamma": str(parallel_gamma),
            "transverse_gamma": str(transverse_gamma),
            "gamma_actual": str(gamma),
            "gamma_over_mu": str(ratio),
            "gamma_over_mu_minus_one": str(gap_to_one),
            "parallel_is_actual_minimum": True,
        },
        "quantifier_consequence": (
            "For every c>1/2, first choose fixed mu<1 sufficiently close to 1, "
            "then choose n sufficiently large; the displayed parallel ratio is below c."
        ),
        "scope_warning": (
            "This rules out global one-epoch K(A)>=c*mu*A^-1 only for c>1/2. "
            "It does not refute c=1/2, the covariance spectral conjecture, or the "
            "O((n/mu) log(1/epsilon)) complexity order."
        ),
        "arithmetic": "Python fractions.Fraction; no floating-point decisions",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "gamma": str(gamma),
                "gamma_minus_mu": str(gamma - mu),
                "checks": "passed",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
