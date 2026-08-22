"""Fixed exact probes for the next Schur-recovery lemma after L3.

This is not a search and not a proof of W4.  It records a few exact rational
controls for the matrix inequality identified in Route L3.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sympy as sp

from iter6_l3_schur_compensation import deletion_data, gram, l3_from_children


Q = sp.Rational


def bernstein_univariate(poly: sp.Expr, variable: sp.Symbol, degree: int) -> list[sp.Expr]:
    from math import comb

    expanded = sp.Poly(poly, variable)
    return [
        sp.factor(
            sum(
                expanded.coeff_monomial(variable**power)
                * Q(comb(index, power), comb(degree, power))
                for power in range(index + 1)
            )
        )
        for index in range(degree + 1)
    ]


def positive_equicorrelation_symbolic() -> dict[str, object]:
    d, mu = sp.symbols("d mu", positive=True)
    parallel = (2 * mu**4 + mu**2 + 1) / (2 * d)
    lam = d - (d - 1) * mu
    alpha = 2 * mu / d
    schur = mu * (d + 1 - d * mu) / lam
    c_norm = d * (1 - mu) ** 2 / lam**2
    ratio = sp.factor(alpha * c_norm / (schur * (parallel - alpha / lam)))
    p_d = 2 * (d - 1) * mu**4 - 2 * mu**3 + (d - 3) * mu**2 - 3 * mu + d
    expected_ratio = 4 * d * (1 - mu) / ((d + 1 - d * mu) * p_d)
    assert sp.factor(ratio - expected_ratio) == 0
    t_d = 2 * d * mu**4 - 2 * mu**3 + (d - 2) * mu**2 - 3 * mu + d - 3
    expected_one_minus = lam * t_d / ((d + 1 - d * mu) * p_d)
    assert sp.factor(1 - ratio - expected_one_minus) == 0
    p6_coefficients = bernstein_univariate(p_d.subs(d, 6), mu, 4)
    t6_coefficients = bernstein_univariate(t_d.subs(d, 6), mu, 4)
    assert p6_coefficients == [Q(6), Q(21, 4), Q(5), Q(19, 4), Q(14)]
    assert t6_coefficients == [Q(3), Q(9, 4), Q(13, 6), Q(9, 4), Q(14)]
    assert all(value > 0 for value in p6_coefficients + t6_coefficients)
    increment = 2 * mu**4 + mu**2 + 1
    assert sp.factor(p_d - p_d.subs(d, 6) - (d - 6) * increment) == 0
    assert sp.factor(t_d - t_d.subs(d, 6) - (d - 6) * increment) == 0
    a = 1 - mu
    transverse_l3 = (
        2 * a**4 * d**2
        - 6 * a**4 * d
        + 4 * a**4
        - 4 * a**3 * d**2
        + 16 * a**3 * d
        - 16 * a**3
        + 3 * a**2 * d**2
        - 17 * a**2 * d
        + 26 * a**2
        + 10 * a * d
        - 20 * a
        + 4 * d**2
        - 12 * d
        + 8
    ) / (2 * d * (d - 2) * (d - 1))
    u_d = sp.factor(
        (transverse_l3 - 2 / d) * 2 * d * (d - 2) * (d - 1) / a
    )
    transverse_gap = sp.factor(a * u_d / (2 * d * (d - 2) * (d - 1)))
    assert sp.factor(transverse_l3 - 2 / d - transverse_gap) == 0
    # The helper variable is mu, so reconstruct in an independent symbol to
    # avoid treating a=1-mu as a generator.
    aa = sp.symbols("a", nonnegative=True)
    u_in_a = sp.factor(u_d.subs(mu, 1 - aa))
    u6_bernstein = bernstein_univariate(aa * u_in_a.subs(d, 6), aa, 4)
    derivative6_bernstein = bernstein_univariate(
        sp.diff(u_in_a, d).subs(d, 6), aa, 3
    )
    assert u6_bernstein == [Q(0), Q(10), Q(76, 3), Q(30), Q(48)]
    assert derivative6_bernstein == [Q(10), Q(49, 3), Q(12), Q(15)]
    assert sp.factor(
        sp.diff(u_in_a, d, 2) - 2 * aa * (2 * aa**2 - 4 * aa + 3)
    ) == 0
    return {
        "parallel_L3_eigenvalue": str(parallel),
        "rank_one_ratio": str(ratio),
        "one_minus_ratio": str(expected_one_minus),
        "P6_bernstein_coefficients": [str(value) for value in p6_coefficients],
        "T6_bernstein_coefficients": [str(value) for value in t6_coefficients],
        "dimension_increment": str(increment),
        "uniform_transverse_U": str(u_in_a),
        "uniform_transverse_d6_bernstein": [str(value) for value in u6_bernstein],
        "uniform_transverse_dimension_derivative_bernstein": [str(value) for value in derivative6_bernstein],
        "conclusion": "Exact E3 algebra proves the positive-equicorrelation W4 recovery for child d>=6.",
    }


def negative_equicorrelation_symbolic() -> dict[str, object]:
    d, z = sp.symbols("d z", positive=True)
    a = -z / d
    mu = 1 - z
    lam = 1 + a * (d - 1)
    parallel = (2 * a**4 - 8 * a**3 + 13 * a**2 - 10 * a + 4) / (2 * d)
    alpha = 2 * mu / d
    schur = mu * (1 - a) / lam
    c_norm = d * a**2 / lam**2
    ratio = sp.factor(alpha * c_norm / (schur * (parallel - alpha / lam)))
    p_d = (
        d**4 * (14 - 10 * z)
        + d**3 * z * (23 - 13 * z)
        + d**2 * z**2 * (21 - 8 * z)
        + 2 * d * z**3 * (5 - z)
        + 2 * z**4
    )
    expected_ratio = 4 * d**5 * z / ((d + z) * p_d)
    assert sp.factor(ratio - expected_ratio) == 0
    positive_factor = (
        14 * d**4
        + 23 * d**3 * z
        + 21 * d**2 * z**2
        + 10 * d * z**3
        + 2 * z**4
    )
    expected_one_minus = (
        (d * (1 - z) + z) * positive_factor / ((d + z) * p_d)
    )
    assert sp.factor(1 - ratio - expected_one_minus) == 0
    transverse_l3 = (
        2 * a**4 * d**2
        - 6 * a**4 * d
        + 4 * a**4
        - 4 * a**3 * d**2
        + 16 * a**3 * d
        - 16 * a**3
        + 3 * a**2 * d**2
        - 17 * a**2 * d
        + 26 * a**2
        + 10 * a * d
        - 20 * a
        + 4 * d**2
        - 12 * d
        + 8
    ) / (2 * d * (d - 2) * (d - 1))
    transverse_shifted_inverse = 2 / (d * (1 - a + z))
    transverse_gap = sp.factor(transverse_l3 - transverse_shifted_inverse)
    transverse_numerator = (
        4 * d**7
        - 8 * d**6
        + 3 * d**5 * z**2
        - 7 * d**5 * z
        - 14 * d**5
        + 4 * d**4 * z**3
        - 10 * d**4 * z**2
        - 7 * d**4 * z
        + 28 * d**4
        + 2 * d**3 * z**4
        - 10 * d**3 * z**3
        - 7 * d**3 * z**2
        + 46 * d**3 * z
        - 4 * d**2 * z**4
        - 6 * d**2 * z**3
        + 42 * d**2 * z**2
        - 2 * d * z**4
        + 20 * d * z**3
        + 4 * z**4
    )
    expected_transverse_gap = z * transverse_numerator / (
        2 * d**5 * (d - 2) * (d - 1) * (d * z + d + z)
    )
    assert sp.factor(transverse_gap - expected_transverse_gap) == 0
    return {
        "rank_one_ratio": str(ratio),
        "positive_denominator_polynomial": str(sp.expand(p_d)),
        "one_minus_ratio": str(sp.factor(expected_one_minus)),
        "uniform_transverse_numerator": str(sp.expand(transverse_numerator)),
        "uniform_transverse_gap": str(sp.factor(expected_transverse_gap)),
        "conclusion": "Exact E3 algebra proves the negative-equicorrelation W4 recovery.",
    }


def positive_rank_one(size: int, mu: sp.Rational) -> sp.Matrix:
    return mu * sp.eye(size) + (1 - mu) * sp.ones(size)


def simplex_lift(size: int, mu: sp.Rational) -> sp.Matrix:
    return sp.Matrix(
        size,
        size,
        lambda i, j: 1 if i == j else -(1 - mu) / (size - 1),
    )


def families() -> list[tuple[str, sp.Matrix, sp.Rational]]:
    records: list[tuple[str, sp.Matrix, sp.Rational]] = []
    mu = Q(1, 4)
    records.append(("positive_rank_one_m7", positive_rank_one(7, mu), mu))
    mu = Q(1, 7)
    records.append(("simplex_lift_m7", simplex_lift(7, mu), mu))
    mu = Q(1, 100)
    records.append(
        (
            "positive2_plus_simplex5_m7",
            sp.diag(positive_rank_one(2, mu), simplex_lift(5, mu)),
            mu,
        )
    )
    records.append(
        (
            "two_positive2_plus_identity3_m7",
            sp.diag(
                positive_rank_one(2, mu),
                positive_rank_one(2, mu),
                sp.eye(3),
            ),
            mu,
        )
    )
    mu = Q(1, 5)
    points = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [Q(3, 5), Q(4, 5), 0],
        [0, Q(5, 13), Q(12, 13)],
        [Q(8, 17), 0, Q(15, 17)],
        [Q(20, 29), Q(21, 29), 0],
    ]
    base = gram(points)
    records.append(("asymmetric_rank3_gram_m7", mu * sp.eye(7) + (1 - mu) * base, mu))
    return records


def recovery_ratios(matrix: sp.Matrix, mu: sp.Rational) -> list[sp.Expr]:
    size = matrix.rows
    child_size = size - 1
    alpha = 2 * mu / child_size
    ratios: list[sp.Expr] = []
    for index in range(size):
        child, b, _ = deletion_data(matrix, index)
        c = child.inv() * b
        if all(value == 0 for value in c):
            ratios.append(Q(0))
            continue
        schur = sp.factor(1 - (b.T * c)[0])
        surplus = sp.simplify(
            l3_from_children(child) - alpha * child.inv()
        )
        ratio = sp.factor(alpha * (c.T * surplus.inv() * c)[0] / schur)
        ratios.append(ratio)
    return ratios


def relevant_dimension_controls() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for name, matrix, mu in families():
        ratios = recovery_ratios(matrix, mu)
        assert all(value <= 1 for value in ratios)
        records.append(
            {
                "family": name,
                "size": matrix.rows,
                "mu": str(mu),
                "exact_ratios": [str(value) for value in ratios],
                "maximum_exact_ratio": str(max(ratios)),
                "result": "PASS on this fixed exact family",
            }
        )
    return records


def too_broad_dimension_barrier() -> dict[str, object]:
    """Full next-level recovery is false if asserted down to parent m=4."""
    size = 4
    mu = Q(1, 4)
    matrix = positive_rank_one(size, mu)
    ratios = recovery_ratios(matrix, mu)
    expected = Q(2304, 1859)
    assert all(value == expected for value in ratios)
    assert expected > 1
    return {
        "family": "positive_rank_one_m4",
        "size": size,
        "mu": str(mu),
        "failed_claim": "The next-level full Schur recovery holds for every parent dimension m>=4.",
        "exact_rank_one_domination_ratio": str(expected),
        "gap_over_one": str(sp.factor(expected - 1)),
        "scope": "W4 is only required from m>=7 in the half-depth hierarchy, so this does not refute the relevant next lemma.",
    }


def spectral_proxy_barrier() -> dict[str, object]:
    """The global spectral terms of the L3 certificate cannot close W4."""
    d = 6
    mu = Q(1, 100)
    eigenvalue = Q(1)
    q_d = (d - 1 - 3 * mu) / (2 * d * (d - 1))
    delta_d = 3 * mu * (1 - mu) / (2 * d * (d - 1))
    proxy = sp.factor(
        (q_d * (eigenvalue - mu) + delta_d) / eigenvalue
    )
    required = sp.factor(
        Q(2, d)
        * (eigenvalue - mu)
        * (1 - mu)
        / (eigenvalue * (eigenvalue + 1 - mu))
    )
    gap = sp.factor(proxy - required)
    assert proxy == Q(33, 400)
    assert required == Q(3267, 19900)
    assert gap == -Q(6501, 79600)

    parent = sp.diag(
        positive_rank_one(2, mu),
        positive_rank_one(2, mu),
        sp.eye(3),
    )
    full_ratios = recovery_ratios(parent, mu)
    assert max(full_ratios) == Q(99, 199) < 1
    return {
        "child_dimension": d,
        "parent_dimension": d + 1,
        "mu": str(mu),
        "child_eigenvalue": str(eigenvalue),
        "spectral_proxy_value": str(proxy),
        "required_schur_envelope": str(required),
        "exact_gap": str(gap),
        "realizing_parent": "direct sum of two [[1,99/100],[99/100,1]] blocks and I_3",
        "full_anisotropic_max_ratio": str(max(full_ratios)),
        "scope": "The full Q_i survives; only dropping its anisotropic child-remainder term is refuted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/iteration6/route_l3/evidence/W4_SCHUR_RECOVERY_EXACT.json"),
    )
    args = parser.parse_args()
    record = {
        "schema_version": "1.0",
        "evidence_level": "E2 fixed exact controls only",
        "candidate": "For m>=7,d=m-1,Q_i=L3(C_i)-(2mu/d)C_i^-1, prove Q_i >=(2mu/(d s_i))c_i c_i^T.",
        "positive_equicorrelation_symbolic": positive_equicorrelation_symbolic(),
        "negative_equicorrelation_symbolic": negative_equicorrelation_symbolic(),
        "relevant_dimension_controls": relevant_dimension_controls(),
        "spectral_proxy_barrier": spectral_proxy_barrier(),
        "too_broad_dimension_barrier": too_broad_dimension_barrier(),
        "scope_warning": "Finite positive controls do not prove the candidate or W4.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "checks": "PASS"}))


if __name__ == "__main__":
    main()
