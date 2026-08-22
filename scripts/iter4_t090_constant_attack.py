"""Attack the repaired boundary constant K0(C) >= (3/2) P_ker(C).

The scan is restricted to the analytically dangerous two-pole plus regular
simplex family.  A moment DP over the three symbol counts evaluates quadratic
forms without enumerating permutations and, importantly, also evaluates the
even kernel/range Schur correction rather than only the odd kernel Rayleigh
quotient.  Exact Fraction checks at k=6 audit the DP against an independent
full 2^8 subset recursion.
"""

from __future__ import annotations

import json
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from search_strong_one_epoch_energy import (
    expected_epoch_energy_dp,
    generalized_max,
    lifted,
    normalize_rows,
)
from verify_iter4_t080_simple_subset_dp import (
    boundary_matrix,
    dot,
    expected_inverse_gram,
    matvec,
)


def _add_entry(target, source):
    for index in range(8):
        target[index] += source[index]


def expected_energy(
    k,
    a,
    rhs_plus,
    rhs_minus,
    rhs_ring,
    *,
    pole_pole=None,
    ring_off=None,
):
    """Expected ||M_pi^{-1} rhs||^2 via affine first/second state moments.

    A state stores probability mass, the two first moments of accumulated pole
    and ring solve values, their symmetric second moments, and accumulated
    solve energy.  Only O(k) count states occur.
    """
    rho = (k * a * a - 1) / (k - 1) if ring_off is None else ring_off
    zero = a * 0
    one = zero + 1
    pole_pole = one if pole_pole is None else pole_pole
    # entry = [mass, E sp, E sr, E sp^2, E sp*sr, E sr^2, E energy, unused]
    states = {(0, 0, 0): [one, zero, zero, zero, zero, zero, zero, zero]}
    for _ in range(k + 2):
        next_states = {}
        for (used_plus, used_minus, used_ring), entry in states.items():
            mass, s0, s1, s00, s01, s11, accumulated, _unused = entry
            remaining_total = k + 2 - used_plus - used_minus - used_ring
            choices = []
            if used_plus == 0:
                choices.append(("plus", one / remaining_total))
            if used_minus == 0:
                choices.append(("minus", one / remaining_total))
            if used_ring < k:
                choices.append(("ring", one * (k - used_ring) / remaining_total))
            for symbol, probability in choices:
                if symbol == "ring":
                    # y=h+d*z; z'=F*z+c, z=(pole_sum,ring_sum).
                    h = rhs_ring
                    d0, d1 = -a, -rho
                    f00, f01, c0 = one, zero, zero
                    f10, f11, c1 = -a, one - rho, h
                    new_key = (used_plus, used_minus, used_ring + 1)
                else:
                    h = rhs_plus if symbol == "plus" else rhs_minus
                    d0, d1 = -pole_pole, -a
                    f00, f01, c0 = one - pole_pole, -a, h
                    f10, f11, c1 = zero, one, zero
                    new_key = (
                        used_plus + int(symbol == "plus"),
                        used_minus + int(symbol == "minus"),
                        used_ring,
                    )

                fs0 = f00 * s0 + f01 * s1
                fs1 = f10 * s0 + f11 * s1
                transformed_s0 = fs0 + c0 * mass
                transformed_s1 = fs1 + c1 * mass

                transformed_s00 = (
                    f00 * f00 * s00
                    + 2 * f00 * f01 * s01
                    + f01 * f01 * s11
                    + 2 * c0 * fs0
                    + c0 * c0 * mass
                )
                transformed_s01 = (
                    f00 * f10 * s00
                    + (f00 * f11 + f01 * f10) * s01
                    + f01 * f11 * s11
                    + c0 * fs1
                    + c1 * fs0
                    + c0 * c1 * mass
                )
                transformed_s11 = (
                    f10 * f10 * s00
                    + 2 * f10 * f11 * s01
                    + f11 * f11 * s11
                    + 2 * c1 * fs1
                    + c1 * c1 * mass
                )
                expected_y_squared = (
                    d0 * d0 * s00
                    + 2 * d0 * d1 * s01
                    + d1 * d1 * s11
                    + 2 * h * (d0 * s0 + d1 * s1)
                    + h * h * mass
                )
                contribution = [
                    probability * mass,
                    probability * transformed_s0,
                    probability * transformed_s1,
                    probability * transformed_s00,
                    probability * transformed_s01,
                    probability * transformed_s11,
                    probability * (accumulated + expected_y_squared),
                    zero,
                ]
                if new_key not in next_states:
                    next_states[new_key] = [zero] * 8
                _add_entry(next_states[new_key], contribution)
        states = next_states
    final = states[(1, 1, k)]
    if isinstance(final[0], F):
        assert final[0] == 1
    else:
        assert abs(final[0] - 1.0) < 1e-10
    return final[6]


def family_schur_coefficients(k, a):
    """Return the odd and even full-Schur kernel coefficients."""
    odd_energy = expected_energy(k, a, 1, -1, 0)
    odd = odd_energy / 2

    # Orthogonal trivial vectors: v is null and w spans range(C).
    v_pole, v_ring = -k * a / 2, a * 0 + 1
    w_pole, w_ring = a * 0 + 1, a
    q_v = expected_energy(k, a, v_pole, v_pole, v_ring)
    q_w = expected_energy(k, a, w_pole, w_pole, w_ring)
    q_sum = expected_energy(
        k, a, v_pole + w_pole, v_pole + w_pole, v_ring + w_ring
    )
    cross = (q_sum - q_v - q_w) / 2
    norm_v_squared = 2 * v_pole * v_pole + k * v_ring * v_ring
    even_compression = q_v / norm_v_squared
    even_schur = even_compression - cross * cross / (norm_v_squared * q_w)
    return odd, even_schur, even_compression, cross, q_w


def global_gamma_record(matrix, family):
    eigenvalues = np.linalg.eigvalsh((matrix + matrix.T) / 2)
    mu = float(eigenvalues[0])
    final_energy = expected_epoch_energy_dp(matrix)
    rate = generalized_max(matrix, final_energy)
    gamma = 1.0 - rate
    return {
        "n": int(matrix.shape[0]),
        "family": family,
        "mu": mu,
        "gamma": gamma,
        "gamma_over_mu": gamma / mu,
        "gamma_minus_mu": gamma - mu,
    }


def global_candidate_scan():
    """E1 attack on gamma(A)>=mu over several interior families."""
    rng = np.random.default_rng(20260901)
    records = []
    for n in range(3, 10):
        records.append(global_gamma_record(np.eye(n), "identity"))
        for mu in [1e-4, 1e-3, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]:
            signs = rng.choice(np.array([-1.0, 1.0]), size=n)
            records.append(
                global_gamma_record(lifted(np.outer(signs, signs), mu), "signed_rank_one")
            )
            if n >= 4:
                k = n - 2
                for latitude in [0.05, 0.2, 0.5, 0.8]:
                    rho = (k * latitude * latitude - 1) / (k - 1)
                    correlation = np.full((n, n), rho)
                    np.fill_diagonal(correlation, 1.0)
                    correlation[:2, :2] = 1.0
                    correlation[:2, 2:] = latitude
                    correlation[2:, :2] = latitude
                    records.append(
                        global_gamma_record(
                            lifted(correlation, mu), "two_pole_simplex"
                        )
                    )
            for _ in range(15):
                rank = int(rng.integers(1, n))
                vectors = normalize_rows(rng.normal(size=(n, rank)))
                records.append(
                    global_gamma_record(
                        lifted(vectors @ vectors.T, mu), f"random_gram_rank_{rank}"
                    )
                )
    return {
        "seed": 20260901,
        "evaluations": len(records),
        "minimum": min(records, key=lambda record: record["gamma_over_mu"]),
        "smallest_ten": sorted(records, key=lambda record: record["gamma_over_mu"])[:10],
        "warning": "Float64 null search; gamma/mu >= 1 in this sample is not a proof.",
    }


def exact_signed_rank_one_counterexample():
    """Exact counterexample to the tempting global constant c=1."""
    n = 9
    k = n - 2
    mu = F(9, 10)
    off_diagonal = F(1) - mu
    transverse_k = expected_energy(
        k,
        off_diagonal,
        F(1),
        F(-1),
        F(0),
        pole_pole=off_diagonal,
        ring_off=off_diagonal,
    ) / 2
    parallel_k = expected_energy(
        k,
        off_diagonal,
        F(1),
        F(1),
        F(1),
        pole_pole=off_diagonal,
        ring_off=off_diagonal,
    ) / n
    parallel_a = n - (n - 1) * mu
    closed_parallel_k = (F(1) - mu ** (2 * n)) / (n * (F(1) - mu * mu))
    assert parallel_k == closed_parallel_k
    gamma_transverse = mu * transverse_k
    gamma_parallel = parallel_a * parallel_k
    gamma = min(gamma_transverse, gamma_parallel)
    assert gamma == gamma_parallel
    assert gamma < mu
    return {
        "n": n,
        "mu": str(mu),
        "A": "mu I+(1-mu)11^T (up to diagonal sign conjugation)",
        "transverse_K_eigenvalue": str(transverse_k),
        "parallel_K_eigenvalue": str(parallel_k),
        "parallel_K_closed_form": "(1-mu^(2n))/[n(1-mu^2)]",
        "transverse_gamma": str(gamma_transverse),
        "parallel_gamma": str(gamma_parallel),
        "gamma": str(gamma),
        "gamma_minus_mu": str(gamma - mu),
        "gamma_over_mu": str(gamma / mu),
        "strict_counterexample_to_gamma_ge_mu": True,
        "iterated_dimension_gap_limit": (
            "lim_(mu up to 1) lim_(n to infinity) gamma/(mu) <= "
            "lim_(mu up to 1) 1/[mu(1+mu)] = 1/2"
        ),
        "arithmetic": "Fraction moment DP over all type words; no float sign decision",
    }


def exact_bare_jensen_barrier():
    """Exact failure of the bare Jensen certificate on equicorrelation."""
    n = 21
    mu = F(9, 20)
    parallel_a = n - (n - 1) * mu
    parallel_s = (F(1) - mu) ** 2 * (n - 1) * (2 * n - 1) / 6
    ratio = parallel_a / (mu * (parallel_a + parallel_s))
    assert parallel_a == 12
    assert parallel_s == F(4961, 120)
    assert ratio == F(3200, 6401)
    assert ratio == F(1, 2) - F(1, 12802)
    # A smaller-dimensional, simpler transverse witness.
    transverse_n = 12
    transverse_mu = F(1, 100)
    transverse_s = (F(1) - transverse_mu) ** 2 * (transverse_n + 1) / 6
    transverse_ratio = F(1) / (transverse_mu + transverse_s)
    assert transverse_s == F(42471, 20000)
    assert transverse_ratio == F(20000, 42671)
    assert transverse_ratio - F(1, 2) == -F(2671, 85342)
    return {
        "certificate": "K >= (A+S)^-1",
        "S": "(A-I)^2/3+Diag(diag((A-I)^2))/6",
        "family": "A=mu I+(1-mu)11^T",
        "parallel_S_eigenvalue": "(1-mu)^2(n-1)(2n-1)/6",
        "n": n,
        "mu": str(mu),
        "parallel_A_eigenvalue": str(parallel_a),
        "parallel_S_value": str(parallel_s),
        "Jensen_gamma_over_mu": str(ratio),
        "gap_below_one_half": str(ratio - F(1, 2)),
        "smaller_transverse_witness": {
            "n": transverse_n,
            "mu": str(transverse_mu),
            "transverse_S_value": str(transverse_s),
            "Jensen_gamma_over_mu": str(transverse_ratio),
            "gap_below_one_half": str(transverse_ratio - F(1, 2)),
        },
        "fixed_mu_large_n_asymptotic": "3/[n mu(1-mu)] -> 0",
        "consequence": "bare Jensen cannot prove any universal positive c",
    }


def exact_signed_rank_one_sharpness_checks():
    """Finite exact checks of the matching one-half family lower bound."""
    records = []
    for n in range(3, 13):
        for mu in [F(1, 10), F(1, 2), F(9, 10), F(99, 100)]:
            geometric_sum = sum(mu ** (2 * power) for power in range(n))
            z = mu ** (2 * n)
            parallel_ratio = (
                (n - (n - 1) * mu) * geometric_sum / (n * mu)
            )
            certified_lower = F(1) / (mu * (1 + mu)) + z / (mu * mu * (1 + mu))
            assert parallel_ratio >= certified_lower > F(1, 2)

            off_diagonal = 1 - mu
            transverse_k = expected_energy(
                n - 2,
                off_diagonal,
                F(1),
                F(-1),
                F(0),
                pole_pole=off_diagonal,
                ring_off=off_diagonal,
            ) / 2
            assert transverse_k >= 1
            records.append(
                {
                    "n": n,
                    "mu": str(mu),
                    "parallel_gamma_over_mu": str(parallel_ratio),
                    "parallel_lower_bound": str(certified_lower),
                    "transverse_gamma_over_mu": str(transverse_k),
                }
            )
    return {
        "general_parallel_identity": (
            "R=S_n/n+(1-z)/[mu(1+mu)], z=mu^(2n)"
        ),
        "general_lower_bound": (
            "R>=1/[mu(1+mu)]+z/[mu^2(1+mu)]>1/2"
        ),
        "general_transverse_bound": (
            "first and second distinguished solve entries each have squared magnitude >=1, "
            "so kappa_transverse>=1"
        ),
        "finite_fraction_checks": records,
    }


def main():
    # Exact audit against the independently implemented full subset DP.
    k = 6
    a = F(2, 3)
    odd, even_schur, even_compression, cross, q_w = family_schur_coefficients(k, a)
    full_k = expected_inverse_gram(boundary_matrix())
    u = [F(1), F(-1)] + [F(0)] * k
    v = [-k * a / 2, -k * a / 2] + [F(1)] * k
    w = [F(1), F(1)] + [a] * k
    assert odd == dot(u, matvec(full_k, u)) / dot(u, u)
    assert even_compression == dot(v, matvec(full_k, v)) / dot(v, v)
    direct_cross = dot(v, matvec(full_k, w))
    direct_q_w = dot(w, matvec(full_k, w))
    assert cross == direct_cross
    assert q_w == direct_q_w
    assert even_schur == even_compression - direct_cross**2 / (dot(v, v) * direct_q_w)

    scan = []
    best = None
    for size in [2, 3, 4, 6, 8, 10, 20, 50, 100, 200, 500, 1000, 2000]:
        for latitude in [0.0001, 0.001, 0.003, 0.01, 0.03, 0.1, 0.2, 1 / 3, 0.5, 2 / 3, 0.8, 0.95]:
            odd_float, even_float, _, _, _ = family_schur_coefficients(size, latitude)
            value = min(odd_float, even_float)
            record = {
                "k": size,
                "n": size + 2,
                "a": latitude,
                "odd": odd_float,
                "even_full_schur": even_float,
                "minimum": value,
                "gap_to_three_halves": value - 1.5,
            }
            scan.append(record)
            if best is None or value < best["minimum"]:
                best = record

    output = {
        "status": "E1 scan plus E3 exact cross-check; null result is not a proof",
        "target_attacked": "K0(C) >= (3/2) P_ker(C)",
        "family": "two duplicate poles plus k-point regular-simplex ring",
        "exact_k6_crosscheck": {
            "a": str(a),
            "odd": str(odd),
            "even_compression": str(even_compression),
            "even_full_schur": str(even_schur),
            "kernel_range_cross": str(cross),
            "range_quadratic": str(q_w),
            "moment_DP_equals_independent_full_subset_DP": True,
        },
        "best_scanned": best,
        "scan": scan,
        "exact_global_c1_counterexample": exact_signed_rank_one_counterexample(),
        "exact_signed_rank_one_half_sharpness": exact_signed_rank_one_sharpness_checks(),
        "exact_bare_jensen_barrier": exact_bare_jensen_barrier(),
        "global_gamma_ge_mu_attack": global_candidate_scan(),
        "interpretation": (
            "No finite violation in this structured scan is not a proof.  The odd coefficient "
            "has iterated infimum 3/2, so any proof at exactly 3/2 must be sharp and cannot "
            "tolerate a dimension-independent additive loss."
        ),
    }
    path = Path("research/evidence/ITER4_T090_THREE_HALVES_ATTACK.json")
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(path), "best": best}, indent=2))


if __name__ == "__main__":
    main()
